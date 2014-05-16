from django.db import models

class OldPoll(models.Model):
    old_poll_name = models.CharField(max_length=30)

class NewPoll(models.Model):
    new_poll_name = models.CharField(max_length=36, unique=True)
