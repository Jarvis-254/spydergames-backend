from rest_framework import serializers
from .models import Match,MatchRound,MatchScore
# create your serializer here

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = "__all__"

class MatchRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchRound
        fields = "__all__"

class MatchScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchScore
        fields = "__all__"