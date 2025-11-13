from rest_framework import serializers
from assignment.models import Reviews


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["id", "card", "ratings"]
