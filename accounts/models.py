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
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES ,default="STUDENT")
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True
    )
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4,unique=True)
    
    def __str__(self):
        return self.name
    
       
class Batch(models.Model):
    name = models.CharField(max_length=4, unique=True, validators= [MinLengthValidator(4)])

    def __str__(self):
        return self.name 
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE,related_name="student_profile") 
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
    batch = models.ForeignKey(
    Batch,
    on_delete=models.PROTECT
    )
    department = models.ForeignKey(
        Department,
        related_name="students",
        on_delete=models.PROTECT
    )

    def __str__(self):
        return self.registration_number
       
class Teacher(models.Model):
    
    user =models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    department = models.ForeignKey(  
        Department,
        related_name="teachers",
        on_delete= models.PROTECT
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True
    )
    specialization = models.CharField(max_length=100)
    
    def __str__(self):
        return self.employee_id
    
class Subject(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    credit_hours = models.PositiveIntegerField(
          validators=[
        MinValueValidator(1),
        MaxValueValidator(4)
    ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["department", "code"],
                name="unique_subject_code_per_department"
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

class SubjectTeaching(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )
    
    
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT
        )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "department",
                    "batch",
                    "subject"
                ],
                name="unique_department_batch_subject"
            )
        ]
        
class AttendanceSession(models.Model):
    subject_teaching = models.ForeignKey(
        SubjectTeaching,
        on_delete=models.CASCADE
    )

    date = models.DateField()
    
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=[
                "subject_teaching",
                "date"
            ],
            name="unique_session_per_day"
        )
    ]

    def __str__(self):
        return f"{self.subject_teaching.subject} - {self.date}"
    
class Attendance(models.Model):
    STATUS_CHOICES = (
        ("P", "Present"),
        ("A", "Absent")
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                name="unique_student_attendance"
            )
        ]