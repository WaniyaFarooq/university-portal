
from django.core.validators import RegexValidator,MaxLengthValidator,MaxValueValidator,MinLengthValidator,MinValueValidator

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE
# Create your models here.




registration_validator = RegexValidator(
    regex= rf'SP\d{2}-[A-Z]{3}-\d{3}$',
    message='Registration Number must be like SP24-BAI-001'
)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT','Student'),
        ('TEACHER','Teacher'),
        ('ADMIN','Admin')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True
    )
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE) 
    # uper wala user model k attributes k li
    registration_number = models.CharField(
        unique = True,
        max_length=12,
        validators=[registration_validator]
    )
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(8)
                    ]
    )
    cgpa = models.DecimalField(max_digits=4,decimal_places=2,
                               validators=[MaxValueValidator(4.00),MinValueValidator(0.00)])
    batch = models.CharField(
        max_length=4
    )