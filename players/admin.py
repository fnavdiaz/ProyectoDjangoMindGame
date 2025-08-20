from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player


class PlayerInline(admin.StackedInline):
    """Inline para mostrar el perfil del jugador en el admin de usuarios"""
    model = Player
    can_delete = False
    verbose_name_plural = 'Perfil de Jugador'
    fields = [
        'display_name', 'karma_score', 'suit_symbol', 
        'is_online', 'current_game_score', 'secrets_discovered_this_game'
    ]
    readonly_fields = ['current_game_score', 'secrets_discovered_this_game']


class UserAdmin(BaseUserAdmin):
    """Admin personalizado para usuarios con perfil de jugador"""
    inlines = (PlayerInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Administración de jugadores"""
    list_display = [
        'display_name', 'user_username', 'suit_symbol', 
        'karma_score', 'karma_level', 'is_online', 
        'current_game_score', 'last_activity'
    ]
    list_filter = [
        'suit_symbol', 'karma_score', 'is_online', 
        'created_at', 'last_activity'
    ]
    search_fields = [
        'display_name', 'user__username', 'user__first_name', 
        'user__last_name', 'user__email'
    ]
    readonly_fields = [
        'created_at', 'last_activity', 'karma_level', 
        'current_game_score', 'secrets_discovered_this_game'
    ]
    
    fieldsets = (
        ('Información del Jugador', {
            'fields': ('user', 'display_name')
        }),
        ('Características del Juego', {
            'fields': ('karma_score', 'karma_level', 'suit_symbol')
        }),
        ('Estado de Conexión', {
            'fields': ('is_online', 'last_activity')
        }),
        ('Estadísticas del Juego Actual', {
            'fields': (
                'current_game_score', 'secrets_discovered_this_game'
            ),
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ['collapse']
        })
    )
    
    actions = ['set_online', 'set_offline', 'reset_karma']
    
    def user_username(self, obj):
        """Muestra el username del usuario asociado"""
        return obj.user.username
    user_username.short_description = 'Usuario'
    user_username.admin_order_field = 'user__username'
    
    def set_online(self, request, queryset):
        """Acción para marcar jugadores como conectados"""
        updated = queryset.update(is_online=True)
        self.message_user(
            request, 
            f'{updated} jugador(es) marcado(s) como conectado(s).'
        )
    set_online.short_description = "Marcar como conectados"
    
    def set_offline(self, request, queryset):
        """Acción para marcar jugadores como desconectados"""
        updated = queryset.update(is_online=False)
        self.message_user(
            request, 
            f'{updated} jugador(es) marcado(s) como desconectado(s).'
        )
    set_offline.short_description = "Marcar como desconectados"
    
    def reset_karma(self, request, queryset):
        """Acción para resetear el karma a 3 (valor por defecto)"""
        updated = queryset.update(karma_score=3)
        self.message_user(
            request, 
            f'Karma reseteado para {updated} jugador(es).'
        )
    reset_karma.short_description = "Resetear karma a 3"


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
