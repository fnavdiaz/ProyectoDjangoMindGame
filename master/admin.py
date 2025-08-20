from django.contrib import admin
from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Administración de juegos"""
    list_display = [
        'name', 'status', 'players_count', 'current_round',
        'created_at', 'started_at'
    ]
    list_filter = ['status', 'created_at', 'current_round']
    search_fields = ['name', 'description']
    readonly_fields = [
        'id', 'created_at', 'started_at', 'players_count', 'is_active',
        'current_round', 'round_started_at', 'round_ends_at', 'time_remaining_in_round'
    ]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description')
        }),
        ('Configuración del juego', {
            'fields': ('status', 'round_duration_seconds')
        }),
        ('Estado actual', {
            'fields': ('current_round', 'round_started_at', 'round_ends_at', 'time_remaining_in_round'),
            'classes': ['collapse']
        }),
        ('Estadísticas', {
            'fields': ('players_count', 'is_active'),
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': ('created_at', 'started_at'),
            'classes': ['collapse']
        })
    )
    
    actions = ['start_selected_games', 'finish_selected_games', 'advance_round']
    
    def start_selected_games(self, request, queryset):
        """Acción para iniciar juegos seleccionados"""
        updated = 0
        for game in queryset.filter(status='waiting'):
            if game.start_game():
                updated += 1
        
        self.message_user(
            request, 
            f'{updated} juego(s) iniciado(s) correctamente.'
        )
    start_selected_games.short_description = "Iniciar juegos seleccionados"
    
    def finish_selected_games(self, request, queryset):
        """Acción para finalizar juegos seleccionados"""
        updated = 0
        for game in queryset.filter(status='active'):
            game.finish_game()
            updated += 1
        
        self.message_user(
            request, 
            f'{updated} juego(s) finalizado(s) correctamente.'
        )
    finish_selected_games.short_description = "Finalizar juegos seleccionados"
    
    def advance_round(self, request, queryset):
        """Acción para avanzar a la siguiente ronda"""
        updated = 0
        for game in queryset.filter(status='active'):
            game.advance_round()
            updated += 1
        
        self.message_user(
            request, 
            f'{updated} juego(s) avanzado(s) a la siguiente ronda.'
        )
    advance_round.short_description = "Avanzar a siguiente ronda"