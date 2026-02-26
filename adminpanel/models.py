from django.db import models
from django.contrib.auth.models import User

class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Login Activities"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    @property
    def duration(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None
