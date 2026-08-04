from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator,
    MinLengthValidator
)

from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# Validators
# =========================

registration_validator = RegexValidator(
    regex=r'SP\d{2}-[A-Z]{3}-\d{3}$',
    message="Registration Number must be like SP24-BAI-001"
)


# =========================
# Custom User
# =========================

class User(AbstractUser):

    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="STUDENT"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username



# =========================
# Department
# =========================

class Department(models.Model):

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=4,
        unique=True
    )


    def __str__(self):
        return self.name



# =========================
# Batch
# =========================

class Batch(models.Model):

    name = models.CharField(
        max_length=4,
        unique=True,
        validators=[
            MinLengthValidator(4)
        ]
    )


    def __str__(self):
        return self.name



# =========================
# Academic Session
# =========================

class AcademicSession(models.Model):

    name = models.CharField(
        max_length=20,
        unique=True
    )

    start_year = models.PositiveIntegerField()

    end_year = models.PositiveIntegerField()


    def __str__(self):
        return self.name



# =========================
# Student
# =========================

class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )


    registration_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            registration_validator
        ]
    )


    semester = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )


    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4)
        ]
    )


    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="students"
    )


    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students"
    )


    def __str__(self):
        return self.registration_number




# =========================
# Teacher
# =========================

class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )


    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="teachers"
    )


    employee_id = models.CharField(
        max_length=20,
        unique=True
    )


    specialization = models.CharField(
        max_length=100
    )


    def __str__(self):
        return self.employee_id




# =========================
# Subject
# =========================

class Subject(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects"
    )


    name = models.CharField(
        max_length=100
    )


    code = models.CharField(
        max_length=20
    )


    semester = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )


    credit_hours = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ]
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "department",
                    "code"
                ],
                name="unique_subject_code"
            )
        ]


    def __str__(self):
        return f"{self.code} - {self.name}"




# =========================
# Subject Teaching
# =========================

class SubjectTeaching(models.Model):

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teachings"
    )


    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teachings"
    )


    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="teachings"
    )


    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="teachings"
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subject",
                    "batch",
                    "academic_session"
                ],
                name="unique_subject_batch_session"
            )
        ]


    def __str__(self):
        return f"{self.subject} - {self.batch}"




# =========================
# Enrollment
# =========================

class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )


    subject_teaching = models.ForeignKey(
        SubjectTeaching,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "subject_teaching"
                ],
                name="unique_student_subject"
            )
        ]


    def __str__(self):
        return f"{self.student} - {self.subject_teaching}"




# =========================
# Attendance Session
# =========================

class AttendanceSession(models.Model):

    subject_teaching = models.ForeignKey(
        SubjectTeaching,
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )


    date = models.DateField()



    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subject_teaching",
                    "date"
                ],
                name="unique_attendance_session"
            )
        ]


    def __str__(self):
        return f"{self.subject_teaching} - {self.date}"




# =========================
# Attendance
# =========================

class Attendance(models.Model):

    STATUS_CHOICES = (
        ("P","Present"),
        ("A","Absent")
    )


    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="attendance"
    )


    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="attendance"
    )


    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES
    )


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "session",
                    "enrollment"
                ],
                name="unique_student_attendance"
            )
        ]