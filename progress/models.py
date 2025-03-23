from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    date = models.DateField(auto_now_add=True)
    goal_completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.date}'
