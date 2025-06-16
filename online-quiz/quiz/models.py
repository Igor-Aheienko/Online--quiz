from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tests_taken = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0)

    def average_score(self):
        if self.tests_taken == 0:
            return 0
        return round(self.total_score / self.tests_taken, 2)
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        
        UserProfile.objects.get_or_create(user=instance)

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    skipped_questions = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(help_text='Час проходження у секундах')
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} — {self.subject.name} — {self.score}/{self.total_questions} ({self.date_taken.date()})'

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)