from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.core.management import call_command
from assignment.models import Reviews, User, Card
from assignment.serializers import ReviewsSerializer, UserSerializer, CardSerializer
from datetime import datetime
from django.shortcuts import get_object_or_404
from assignment.permissions import IdempotencyPermission


@api_view(["POST"])
def initialize_data(request):
    try:
        file_name = request.data.get("file", "MOCK_DATA.json")
        print(f"Initializing data from {file_name}")
        call_command("init_data", file=file_name)

        return Response(
            {
                "message": "Database Initialized successfully and cards assigned to user 'testuser'"
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user-related operations.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

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

    @action(detail=True, methods=["get"])
    def due_cards(self, request, pk=None):
        """
        ViewSet that lists all cards related to a specific user, where the next_review date is lte the until parameter.
        """
        until_date_str = request.query_params.get("until", None)
        if until_date_str:
            try:
                until_date = datetime.fromisoformat(until_date_str)
            except ValueError:
                return Response(
                    {"error": "Invalid ISO8601 date format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "'until' query parameter is required (ISO8601 datetime)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # pk is the user ID from the URL
        user = get_object_or_404(User, pk=pk)
        # Not having a next_review date means the card has never been seen before so it doesnt get listed out i think thats fine.
        user_cards_queryset = Card.objects.filter(
            user=user, next_review__lte=until_date
        )
        serializer = CardSerializer(user_cards_queryset, many=True)
        return Response(serializer.data)


class ReviewsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for POSTing a review and getting next due date in response.
    """

    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [IdempotencyPermission]
    authentication_classes = []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        reviewCard = serializer.validated_data.get("card")
        # convert to JST
        nxtReviewDate = CardSerializer(reviewCard).data["next_review"]
        response = {
            "next_review": nxtReviewDate,
        }

        return Response(response, status=status.HTTP_201_CREATED)
