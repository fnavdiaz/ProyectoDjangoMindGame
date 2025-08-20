from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Game


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuarios"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class GameSerializer(serializers.ModelSerializer):
    """Serializer para juegos"""
    players_count = serializers.ReadOnlyField()
    connected_players = serializers.SerializerMethodField()
    time_remaining_in_round = serializers.ReadOnlyField()
    is_round_finished = serializers.ReadOnlyField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'started_at', 'current_round',
            'round_duration_seconds', 'round_started_at', 'round_ends_at',
            'players_count', 'connected_players', 'time_remaining_in_round',
            'is_round_finished', 'is_paused', 'paused_at', 'paused_duration'
        ]
        read_only_fields = [
            'id', 'created_at', 'started_at', 'current_round',
            'round_started_at', 'round_ends_at', 'is_paused', 'paused_at', 'paused_duration'
        ]
    
    def get_connected_players(self, obj):
        """Devuelve información básica de jugadores conectados"""
        from players.serializers import PlayerSerializer
        return PlayerSerializer(obj.connected_players, many=True).data


class GameCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear juegos"""
    class Meta:
        model = Game
        fields = [
            'name', 'description', 'round_duration_seconds'
        ]