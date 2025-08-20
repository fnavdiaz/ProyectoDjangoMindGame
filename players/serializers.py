from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Player


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuarios"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer para jugadores"""
    user = UserSerializer(read_only=True)
    karma_level = serializers.ReadOnlyField()
    suit_emoji = serializers.ReadOnlyField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'user', 'display_name', 'karma_score', 'karma_level',
            'suit_symbol', 'suit_emoji', 'is_online', 'last_activity',
            'current_game_score', 'secrets_discovered_this_game', 'created_at'
        ]
        read_only_fields = [
            'last_activity', 'current_game_score', 
            'secrets_discovered_this_game', 'created_at'
        ]


class OnlinePlayerSerializer(serializers.ModelSerializer):
    """Serializer simplificado para jugadores conectados"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    suit_emoji = serializers.ReadOnlyField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'display_name', 'user_username', 'karma_score', 
            'suit_symbol', 'suit_emoji', 'last_activity', 'is_dead', 'death_reason'
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer para el ranking de jugadores"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    karma_level = serializers.ReadOnlyField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'display_name', 'user_username', 'karma_score', 
            'karma_level', 'suit_symbol', 'current_game_score',
            'secrets_discovered_this_game'
        ]
