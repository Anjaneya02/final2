from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    height = models.IntegerField()
    weight = models.IntegerField()
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    activity = models.CharField(max_length=20, choices=[
        ('S', 'Sedentary'),
        ('L', 'Lightly active'),
        ('M', 'Moderately active'),
        ('V', 'Very active'),
        ('E', 'Extremely active')
    ])
    calories_required = models.IntegerField(blank=True, null=True)

    def calculate_calories_required(self):
        weight = float(self.weight) if self.weight is not None else 0.0
        height = float(self.height) if self.height is not None else 0.0
        age = float(self.age) if self.age is not None else 0.0
        # Harris-Benedict Equation to estimate BMR
        if self.gender == 'M':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

        # Activity factor
        activity_factors = {
            'S': 1.2,  # Sedentary
            'L': 1.375,  # Lightly active
            'M': 1.55,  # Moderately active
            'V': 1.725,  # Very active
            'E': 1.9  # Extremely active
        }
        activity_factor = activity_factors.get(self.activity, 1.2)

        # Calculate total calories required
        total_calories_required = int(bmr * activity_factor)

        return total_calories_required

    def save(self, *args, **kwargs):
            self.calories_required = self.calculate_calories_required()
            super(Profile, self).save(*args, **kwargs)
    def __str__(self):
        return self.user.username
    
class DailyActivity(models.Model):
        user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
        date = models.DateField()
        calories_consumed = models.IntegerField()
    
        class Meta:
            unique_together = ('user', 'date')