import json
import os
from django.core.management.base import BaseCommand
from assignment.models import User
from assignment.models import Card, Rating_Buckets, Reviews, IdempotencyKeys


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file", default="MOCK_DATA.json", help="JSON file name to load data from"
        )

    def handle(self, *args, **options):
        User.objects.all().delete()

        # Delete old test data
        IdempotencyKeys.objects.all().delete()
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
            Rating_Buckets.objects.create(score=0, default_interval=1)  # 1 minute
            Rating_Buckets.objects.create(score=1, default_interval=4320)  # 3 days
            Rating_Buckets.objects.create(score=2, default_interval=7200)  # 5 days

            # Creating 6 Cards tied to the user
            for i in range(1, 6):
                Card.objects.create(
                    user=user, front=f"foo{i}", back=f"bar{i}", continuous_recall=0
                )

            self.stdout.write(
                self.style.SUCCESS(f"Mock data successfully loaded to database \nYou can use test UserId: {user.id}, for due_cards API call.\nHere are a list of card IDs: {Card.objects.values_list('id')}\nRating scores are 0, 1, 2 as outlined in requirements\nPlease remember POST call to reviews requires header X-IDEMPOTENCY-KEY to be set.")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
