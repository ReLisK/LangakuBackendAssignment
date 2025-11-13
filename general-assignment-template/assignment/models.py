# from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model that extends the default Django User model.
    This can be used to add additional fields or methods in the future.
    """

    pass


###############################################################################
## TODO: Modify the following

class Rating_Buckets(models.Model):
    score = models.IntegerField(primary_key=True)
    default_interval = models.IntegerField() #Minutes

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    front = models.CharField(max_length= 100)
    back = models.CharField(max_length= 100)
    continuous_recall = models.IntegerField(default=0)
    #Seen Bool
    #Rating_Bucket = models.ForeignKey(Rating_Buckets, on_delete=models.CASCADE)
    last_reviewed= models.DateTimeField(default=timezone.now)
    next_review = models.DateTimeField(blank=True, null=True)

class Reviews(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    ratings = models.ForeignKey(Rating_Buckets, on_delete=models.CASCADE)

class IdempotencyKeys(models.Model):
    key = models.CharField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField()
    expires_at = models.DateTimeField()

