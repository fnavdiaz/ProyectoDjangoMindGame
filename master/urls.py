from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'games', views.GameViewSet)

app_name = 'master'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path('api/dashboard/', views.MasterDashboardView.as_view(), name='api_dashboard'),
    
    # Web URLs para interfaz del master
    path('login/', views.master_login_view, name='login'),
    path('logout/', views.master_logout_view, name='logout'),
    path('dashboard/', views.master_dashboard_view, name='dashboard'),
    path('game/<uuid:game_id>/start/', views.start_game_view, name='start_game'),
    path('game/<uuid:game_id>/finish/', views.finish_game_view, name='finish_game'),
    path('game/<uuid:game_id>/results/', views.game_results_view, name='game_results'),
    path('game/create/', views.create_game_view, name='create_game'),
    path('game/<uuid:game_id>/', views.game_detail_view, name='game_detail'),
]
