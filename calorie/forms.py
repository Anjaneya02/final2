from django import forms

class CalorieForm (forms.Form):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.ChoiceField (choices=GENDER_CHOICES, widget=forms.RadioSelect (), required=False)
    height = forms.IntegerField (label='Height (cm)', required=False)
    weight = forms.IntegerField (label='Weight (kg)', required=False)
    calories = forms.IntegerField (label='Calories', required=False)
