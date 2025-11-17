from datetime import timedelta
import pytest
from django.contrib.auth import get_user_model
from assignment.models import Card

User = get_user_model()


@pytest.mark.django_db
class TestCardModelFunctions:
    def setup_method(self):
        self.test_username = "testuser"
        self.user = User.objects.create_user(username=self.test_username)
        self.card = Card.objects.create(
            user=self.user, front="Test", back="Card", step=0
        )
        self.card2 = Card.objects.create(
            user=self.user, front="Test", back="Card", step=0
        )
        self.card3 = Card.objects.create(
            user=self.user, front="Test", back="Card", step=0
        )

    def test_again_always_sets_interval_to_one_minute(self):
        """Test that no matter what call preceded it, again sets interval to 1 minute"""
        self.card.again()
        assert self.card.interval == timedelta(minutes=1)

        self.card.hard()
        self.card.again()
        assert self.card.interval == timedelta(minutes=1)

        self.card.easy()
        self.card.again()
        assert self.card.interval == timedelta(minutes=1)

    def test_again_changes_state_to_relearning(self):
        """Test that again changes state to relearning if prev state was reviewing"""
        self.card.easy()
        assert self.card.state == "reviewing"
        self.card.again()
        assert self.card.state == "relearning"

    def test_hard_changes_state_to_reviewing_on_second_attempt(self):
        """Test that hard changes state to reviewing on second attempt"""
        self.card.hard()
        self.card.hard()
        assert self.card.state == "reviewing"

    def test_easy_always_changes_state_to_reviewing(self):
        """Test that easy always changes state to reviewing"""
        # Learning state to reviewing
        self.card.easy()
        assert self.card.state == "reviewing"

        # Relearning state to reviewing
        self.card.easy()
        self.card.again()
        self.card.easy()
        assert self.card.state == "reviewing"

    def test_monotonicity(self):
        """Test that subsequent attempts of hard or easy never shorten interval time"""
        # Set interval to 1 minute
        self.card.again()

        for _ in range(5):
            oldInterval = self.card.interval
            self.card.hard()
            assert self.card.interval > oldInterval

        # Set interval to 1 minute
        self.card.again()

        for _ in range(5):
            oldInterval = self.card.interval
            self.card.easy()
            assert self.card.interval > oldInterval
