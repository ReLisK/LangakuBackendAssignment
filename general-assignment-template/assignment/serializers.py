from rest_framework import serializers
from assignment.models import Reviews, User, Card
from zoneinfo import ZoneInfo


# Time Zone
jst_tz = ZoneInfo("Japan")


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["id", "card", "ratings"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]
        
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "user", "front", "back", "continuous_recall", "last_reviewed", "next_review"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['last_reviewed'] = instance.last_reviewed.astimezone(jst_tz)
        representation['next_review'] = instance.next_review.astimezone(jst_tz)
        return representation

