from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para las vistas de la API REST
router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)

app_name = 'players'

urlpatterns = [
    # Rutas de la interfaz web
    path('', views.player_login_view, name='login'),
    path('login/', views.player_login_view, name='login'),
    path('register/', views.player_register_view, name='register'),
    path('dashboard/', views.player_dashboard_view, name='dashboard'),
    path('logout/', views.player_logout_view, name='logout'),
    path('game/<uuid:game_id>/results/', views.player_game_results_view, name='game_results'),
    
    # Rutas AJAX para mecánicas del juego
    path('ajax/choose-symbol/', views.choose_symbol_view, name='ajax_choose_symbol'),
    path('ajax/tell-player-symbol/', views.tell_player_symbol_view, name='ajax_tell_player_symbol'),
    path('ajax/get-player-guesses/', views.get_player_guesses_view, name='ajax_get_player_guesses'),
    path('ajax/check-new-game/', views.check_new_game_view, name='ajax_check_new_game'),
    
    # Rutas de la API REST
    path('api/', include(router.urls)),
    path('api/online/', views.OnlinePlayersView.as_view(), name='api_online_players'),
    path('api/leaderboard/', views.LeaderboardView.as_view(), name='api_leaderboard'),
]
