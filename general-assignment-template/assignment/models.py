# from django.db import models
from datetime import timedelta
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


class Card(models.Model):
    HARDBIAS = 1.2
    EASYBIAS = 1.2
    MIN_EASE = 1.3

    class STATES(models.TextChoices):
        LEARNING = "learning", "Learning"
        REVEIWING = "reviewing", "Reviewing"
        RELEARNING = "relearning", "Relearning"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    front = models.CharField(max_length=100)
    back = models.CharField(max_length=100)
    state = models.CharField(max_length=10, choices=STATES, default=STATES.LEARNING)
    ease = models.FloatField(default=2.5)
    interval = models.DurationField(default=timedelta)
    step = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(default=timezone.now)
    next_review = models.DateTimeField(blank=True, null=True)

    def _setNextReview(self, interval):
        self.last_reviewed = timezone.now()
        self.next_review = self.last_reviewed + interval
        return

    def again(self):
        self.interval = timedelta(minutes=1)
        match self.state:
            case "learning":
                pass
            case "reviewing":
                self.state = "relearning"
                # when Again is selected we modify the ease by minus 0.2.
                self.ease = max(self.MIN_EASE, self.ease - 0.2)
            case "relearning":
                pass

        self._setNextReview(self.interval)
        self.save()

    def hard(self):
        match self.state:
            case "learning":
                if self.step == 0:
                    self.step = 1
                    self.interval = timedelta(minutes=6)
                else:
                    self.state = "reviewing"
                    self.interval = timedelta(days=1)
            case "reviewing":
                # Modify ease negatively as it was still hard.
                self.ease -= 0.15
                # Dont let ease fall below 1.3
                self.ease = max(self.MIN_EASE, self.ease)
                # Set new interval, note we don't use ease in this calculation as it was still answered as hard.
                # But we do multiply by a bias 1.2 so that the user doesnt get hard stuck at the same interval.
                self.interval = self.interval * self.HARDBIAS
            case "relearning":
                self.interval = timedelta(days=1)

        self._setNextReview(self.interval)
        self.save()

    def easy(self):
        match self.state:
            case "learning":
                if self.step == 0:
                    self.step = 1
                    self.interval = timedelta(days=4)
                else:
                    # Basically I think if you selected HARD for a card, then selected EASY you should get 3 days instead of 4, as you dont know it as perfectly as someone who knew it instantly..
                    self.interval = timedelta(days=3)
                self.state = "reviewing"
            case "reviewing":
                # Modify ease positively as it was still easy.
                self.ease += 0.15
                # Use ease as a multiple to increase interval.
                self.interval = self.interval * self.EASYBIAS * self.ease
            case "relearning":
                self.state = "reviewing"
                self.interval = timedelta(days=4)

        self._setNextReview(self.interval)
        self.save()


class Reviews(models.Model):
    class Rating(models.IntegerChoices):
        AGAIN = 0, "Again"
        HARD = 1, "Hard"
        EASY = 2, "Easy"

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    ratingScore = models.IntegerField(choices=Rating)

    def save(self, **kwargs):
        if self.ratingScore == 0:
            self.card.again()
        elif self.ratingScore == 1:
            self.card.hard()
        else:
            self.card.easy()

        super(Reviews, self).save(**kwargs)


class IdempotencyKeys(models.Model):
    key = models.CharField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField()
    expires_at = models.DateTimeField()
