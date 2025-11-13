import json
import os
from django.core.management.base import BaseCommand
from assignment.models import User
from assignment.models import Card, Rating_Buckets, Reviews


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file", default="MOCK_DATA.json", help="JSON file name to load data from"
        )

    def handle(self, *args, **options):
        User.objects.all().delete()

        # Delete old test data
        Rating_Buckets.objects.all().delete()
        Card.objects.all().delete()
        Reviews.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All existing item data has been deleted"))

        try:
            file_name = options.get("file", "MOCK_DATA.json")
            json_file_path = os.path.join(os.path.dirname(__file__), file_name)

            with open(json_file_path) as json_file:
                _ = json.load(json_file)
                # Handle the data as needed, e.g., creating User objects

            user = User.objects.create_superuser(
                "testuser", email="testuser@example.com", password="testpassword"
            )
            for i in range(1, 6):
                User.objects.create_user(
                    f"testuser{i}",
                    email=f"testuser{i}@example.com",
                    password="testpassword",
                )

            self.stdout.write(
                self.style.SUCCESS(f"Mock data loaded successfully from {file_name}")
            )

            # Creating test Cards, and setting up Rating_Buckets defaults so a quick setup and test can be done.

            # Setting up 3 rating bucket defaults
            ratingBucket0 = Rating_Buckets.objects.create(score = 0, default_interval=1)      # 1 minute
            ratingBucket2 = Rating_Buckets.objects.create(score = 1, default_interval=4320)   # 3 days 
            ratingBucket3 = Rating_Buckets.objects.create(score = 2, default_interval=7200)   # 5 days

            # Creating 6 Cards tied to the user
            card1 = Card.objects.create(user=user, front="foo1", back="bar", continuous_recall = 0)
            card2 = Card.objects.create(user=user, front="foo2", back="bar", continuous_recall = 0)
            card3 = Card.objects.create(user=user, front="foo3", back="bar", continuous_recall = 0)
            card4 = Card.objects.create(user=user, front="foo4", back="bar", continuous_recall = 0)
            card5 = Card.objects.create(user=user, front="foo5", back="bar", continuous_recall = 0)
            card6 = Card.objects.create(user=user, front="foo6", back="bar", continuous_recall = 0)

            self.stdout.write(
                self.style.SUCCESS(f"Mock data successfully loaded to database")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
