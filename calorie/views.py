from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from calorie.models import *
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def login_page(request):
    return render(request,"login.html")

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

def save(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        raw_password = request.POST.get('pass')
        email = request.POST.get('email')
        # Hash the password before saving it
        hashed_password = make_password(raw_password)
        # Create and save the new user with the hashed password
        new_user = CustomUser(username=user, password=hashed_password, email=email)
        new_user.save()
        return redirect('login_page')
    return HttpResponse("Invalid request method.")
    
def check(request):
    if request.method == 'POST':
        # Get the form data
        username_raw = request.POST['username2']
        password_raw = request.POST['password2']
        
        # Check if the user exists for login
        
        user = authenticate(request,username=username_raw,password=password_raw)
        
        if user is not None:
            # If the user exists, perform login
            login(request,user)
            
            return render(request, 'home.html')
        else:
            return HttpResponse("Login unsuccessful!")
    else:
   
        return HttpResponse("HAHAHA")

def home(request):
    return render(request, "home.html")

@login_required(login_url='/login/')
def profile_view(request):
    current_username = None
    if request.user.is_authenticated:
        current_username = request.user.username
    else :
        pass
    return render(request, 'profile.html', {'username': current_username})

@csrf_exempt
@login_required
def submit_health_form(request):
    if request.method == 'POST':
        # Retrieve data from the form
        height_raw = request.POST.get('height')
        weight_raw = request.POST.get('weight')
        age_raw = request.POST.get('age')
        gender = request.POST.get('gender')
        activity = request.POST.get('activity')

        profile_exists = Profile.objects.filter(user=request.user).exists()

        # Check if the profile exists
        if profile_exists:
            # Retrieve the existing profile
            profile = Profile.objects.get(user=request.user)
            # Update the profile with the new information
            profile.height = int(height_raw) if height_raw else None
            profile.weight = weight_raw if weight_raw else None
            profile.age = age_raw if age_raw else None
            profile.gender = gender if gender else None
            profile.activity = activity if activity else None
            profile.calories_required = profile.calculate_calories_required()
        else:
            # Create a new profile with all parameters
            profile = Profile(
                user=request.user,
                height=int(height_raw) if height_raw else None,
                weight=weight_raw if weight_raw else None,
                age=age_raw if age_raw else None,
                gender=gender if gender else None,
                activity=activity if activity else None,
                calories_required=None  # Set your default value or leave it as None
            )

        

        try:
            # Save the profile instance to the database
            profile.save()

            if profile_exists:
                messages.success(request, 'Health information updated successfully.')
            else:
                messages.success(request, 'Profile created successfully.')
        except Exception as e:
            messages.error(request, f'Error updating health information: {str(e)}')

    # Redirect to a success page or display a message
    return redirect('/dashboard/')  # Change 'success_page' to the actual URL or name of the success page

@login_required(login_url='/login/')
def dashboard(request):
        if request.user.is_authenticated:
            active_user = request.user

            # Retrieve the profile for the active user
            try:
                active_user_profile = Profile.objects.get(user=active_user)
                calories_required = active_user_profile.calories_required
                prams={'calories':calories_required,'username':active_user_profile}
            except Profile.DoesNotExist:
                # Handle the case where the profile for the user does not exist
                active_user_profile = None

            return render(request, 'dashboard.html',prams)
        else:
            # Handle the case where the user is not authenticated
            return redirect(request, 'login.html')
        
def save_calories(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        calories = request.POST.get("calories_consumed")
        current_date = timezone.now().date()

        # Get the corresponding CustomUser instance
        user_instance = get_object_or_404(CustomUser, username=username)

        # Check if DailyActivity instance exists for the user and date
        daily_activity_exists = DailyActivity.objects.filter(user=user_instance, date=current_date).exists()

        if daily_activity_exists:
            # Retrieve the existing DailyActivity instance
            daily_activity = DailyActivity.objects.get(user=user_instance, date=current_date)
            daily_activity.calories_consumed += int(calories)
        else:
            # If the instance doesn't exist, create a new one
            daily_activity = DailyActivity(user=user_instance, date=current_date, calories_consumed=int(calories))

        # Save the changes
        daily_activity.save()

        return HttpResponse(f"Calories consumed ({calories}) saved successfully.")
    else:
        return HttpResponse("Invalid request method.")