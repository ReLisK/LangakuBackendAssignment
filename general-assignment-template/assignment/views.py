from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.management import call_command
from assignment.models import Card, Rating_Buckets, Reviews
from assignment.serializers import ReviewsSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from zoneinfo import ZoneInfo


#Time Zone
jst_tz = ZoneInfo("Japan")

@api_view(["POST"])
def initialize_data(request):
    try:
        file_name = request.data.get("file", "MOCK_DATA.json")
        print(f"Initializing data from {file_name}")
        call_command("init_data", file=file_name)

        return Response(
            {"message": f"Database Initialized successfully: RatingBuckets have been setup and cards assigned to user 'testuser'"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user-related operations.
    """

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Returns the username of the logged-in user.
        """
        if request.user.is_authenticated:
            return Response(
                {"username": request.user.username}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
            )

class ReviewsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for POSTing a review and getting next due date in response.
    """
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        reviewCard = serializer.validated_data.get('card')
        rating = serializer.validated_data.get('ratings')
        defaultInterval = rating.default_interval
        time_delta = timedelta(minutes=defaultInterval)

        reviewCard.last_reviewed = timezone.now()
        reviewCard.save()

        if rating.score == 0:
            reviewCard.next_review = reviewCard.last_reviewed + time_delta
            reviewCard.continuous_recall = 0
        else:
            # if they got it right we want to incrementally keep increasing the addtional review time_delta by multiplying by continuous_recall
            reviewCard.continuous_recall += 1
            print(f"tiemdelta {time_delta}")
            print(f"qucik maffs {(time_delta * reviewCard.continuous_recall)}")
            print(f"qucik maffs?!! {reviewCard.last_reviewed + (time_delta * reviewCard.continuous_recall)}")
            reviewCard.next_review = reviewCard.last_reviewed + (time_delta * reviewCard.continuous_recall)
        reviewCard.save()

        #convert to JST
        response = {
            "next_review" : reviewCard.next_review,
            "next_review_JST" : reviewCard.next_review.astimezone(jst_tz)
        }

        return Response(response, status=status.HTTP_201_CREATED)

