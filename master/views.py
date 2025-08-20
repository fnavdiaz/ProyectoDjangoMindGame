from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Game
from players.models import Player
from .serializers import GameSerializer

class GameViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar juegos"""
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Game.objects.all()  # Queryset base
    
    def get_queryset(self):
        """Devuelve todos los juegos (solo hay uno en el sistema local)"""
        return Game.objects.all()
    
    def perform_create(self, serializer):
        """Crea un nuevo juego"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def start_game(self, request, pk=None):
        """Inicia un juego"""
        game = self.get_object()
        if game.status != 'waiting':
            return Response(
                {'error': 'El juego ya ha sido iniciado o finalizado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if game.players_count < 1:  # Temporal para pruebas - era 3
            return Response(
                {'error': 'Se necesita al menos 1 jugador para iniciar (modo prueba)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not game.start_game():  # start_game() retorna True/False
            return Response(
                {'error': 'No se pudo iniciar el juego'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'message': 'Juego iniciado correctamente'})
    
    @action(detail=True, methods=['post'])
    def finish_game(self, request, pk=None):
        """Finaliza un juego"""
        game = self.get_object()
        if game.status != 'active':
            return Response(
                {'error': 'Solo se pueden finalizar juegos activos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game.finish_game()
        return Response({'message': 'Juego finalizado correctamente'})
    
    @action(detail=True, methods=['post'])
    def advance_round(self, request, pk=None):
        """Avanza a la siguiente ronda manualmente"""
        game = self.get_object()
        if game.status != 'active':
            return Response(
                {'error': 'Solo se puede avanzar ronda en juegos activos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game.advance_round()
        return Response({
            'message': 'Ronda avanzada correctamente',
            'current_round': game.current_round,
            'players_with_symbols': [
                {
                    'display_name': p.display_name, 
                    'suit_symbol': p.suit_symbol
                } 
                for p in game.connected_players
            ]
        })
    
    @action(detail=True, methods=['post'])
    def pause_round(self, request, pk=None):
        """Pausa o reanuda la ronda actual"""
        game = self.get_object()
        if game.status != 'active':
            return Response(
                {'error': 'Solo se puede pausar rondas en juegos activos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar request.data en lugar de request.body para DRF
        action = request.data.get('action', 'pause')
        
        if action == 'pause':
            if game.pause_round():
                return Response({
                    'message': 'Ronda pausada correctamente',
                    'is_paused': True
                })
            else:
                return Response(
                    {'error': 'No se pudo pausar la ronda'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:  # resume
            if game.resume_round():
                return Response({
                    'message': 'Ronda reanudada correctamente',
                    'is_paused': False
                })
            else:
                return Response(
                    {'error': 'No se pudo reanudar la ronda'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """Lista los jugadores conectados (ya que solo hay un juego activo)"""
        from players.serializers import OnlinePlayerSerializer
        from players.models import Player
        
        online_players = Player.objects.filter(is_online=True).order_by('display_name')
        serializer = OnlinePlayerSerializer(online_players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Estadísticas del juego"""
        game = self.get_object()
        stats = {
            'total_players': game.players_count,
            'current_round': game.current_round,
            'time_remaining': game.time_remaining_in_round,
            'status': game.status,
        }
        return Response(stats)


class MasterDashboardView(APIView):
    """Vista del panel de control del master"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Dashboard con resumen del juego actual"""
        current_game = Game.get_current_game()
        
        # Obtener jugadores en el juego
        players_in_game = Player.objects.filter(is_in_game=True).order_by('display_name')
        
        # Serializar jugadores manualmente para incluir más información
        players_data = []
        for player in players_in_game:
            players_data.append({
                'id': player.id,
                'display_name': player.display_name,
                'username': player.user.username,
                'karma_score': player.karma_score,
                'is_online': player.is_online,
                'is_in_game': player.is_in_game,
                'suit_emoji': player.suit_emoji,
                'suit_symbol': player.suit_symbol,
                'is_dead': player.is_dead,
                'death_reason': player.death_reason,
            })
        
        # Contar solo jugadores vivos para las estadísticas
        alive_players_count = players_in_game.filter(is_dead=False).count()
        
        dashboard_data = {
            'current_game': GameSerializer(current_game).data if current_game else None,
            'online_players': players_data,
            'stats': {
                'online_players': alive_players_count,  # Solo jugadores vivos
                'total_players': Player.objects.count(),
                'active_games': Game.objects.filter(status='active').count(),
            },
            'game_status': current_game.status if current_game else 'none',
        }
        
        return Response(dashboard_data)


# ============= VISTAS WEB PARA EL MASTER =============

def is_staff_user(user):
    """Verifica si el usuario es staff (master)"""
    return user.is_staff

def master_login_view(request):
    """Vista de login para el master"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('master:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('master:dashboard')
        else:
            context = {
                'error': 'Credenciales inválidas o no tiene permisos de master.'
            }
            return render(request, 'master/login.html', context)
    
    return render(request, 'master/login.html')

@login_required
@user_passes_test(is_staff_user)
def master_dashboard_view(request):
    """Dashboard principal del master"""
    # Obtener jugadores INSCRITOS EN EL JUEGO (tanto conectados como desconectados)
    online_players = Player.objects.filter(is_in_game=True).order_by('display_name')
    
    # Contar solo jugadores vivos para las estadísticas
    alive_players_count = online_players.filter(is_dead=False).count()
    
    # Obtener estadísticas
    stats = {
        'online_players': alive_players_count,  # Solo jugadores vivos
        'active_games': Game.objects.filter(status='active').count(),
    }
    
    # Obtener juego actual (activo o en espera)
    current_game = Game.get_current_game()
    
    context = {
        'online_players': online_players,
        'stats': stats,
        'current_game': current_game,
    }
    
    return render(request, 'master/dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def master_logout_view(request):
    """Logout del master"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('master:login')

@login_required
@user_passes_test(is_staff_user)
def start_game_view(request, game_id):
    """Inicia un juego"""
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        if game.status == 'waiting' and game.players_count >= 1:  # Temporal para pruebas
            if game.start_game():
                messages.success(request, f'Juego "{game.name}" iniciado correctamente.')
            else:
                messages.error(request, 'No se pudo iniciar el juego.')
        else:
            messages.error(request, 'No se puede iniciar el juego. Verifica el estado y número de jugadores.')
    
    return redirect('master:dashboard')

@login_required
@user_passes_test(is_staff_user)
def finish_game_view(request, game_id):
    """Finaliza un juego"""
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        if game.status == 'active':
            game.finish_game()
            
            # Redirigir a la pantalla de resultados
            return redirect('master:game_results', game_id=game.id)
        else:
            messages.error(request, 'Solo se pueden finalizar juegos activos.')
    
    return redirect('master:dashboard')

@login_required
@user_passes_test(is_staff_user)
def game_results_view(request, game_id):
    """Muestra los resultados del juego finalizado"""
    from players.models import Player
    
    game = get_object_or_404(Game, id=game_id)
    
    if game.status != 'finished':
        messages.error(request, 'Solo se pueden ver resultados de juegos finalizados.')
        return redirect('master:dashboard')
    
    # Obtener todos los jugadores que participaron en el juego
    all_players = Player.objects.filter(is_in_game=True).order_by('-lies_told', '-truths_told', 'display_name')
    
    # Determinar ganador usando la misma lógica que finish_game
    alive_players = all_players.filter(is_dead=False)
    alive_count = alive_players.count()
    
    winner = None
    winner_reason = ""
    
    if alive_count == 0:
        winner_reason = "Todos los jugadores han muerto. Nadie gana."
    elif alive_count == 1:
        winner = alive_players.first()
        winner_reason = f"{winner.display_name} es el ganador (único superviviente)"
    elif alive_count == 2:
        players_list = list(alive_players.order_by('-lies_told', '-truths_told'))
        player1, player2 = players_list[0], players_list[1]
        
        player1_interactions = player1.lies_told + player1.truths_told
        player2_interactions = player2.lies_told + player2.truths_told
        
        if player1_interactions > player2_interactions:
            winner = player1
            winner_reason = f"{winner.display_name} gana por más interacciones ({player1_interactions} vs {player2_interactions})"
        elif player2_interactions > player1_interactions:
            winner = player2
            winner_reason = f"{winner.display_name} gana por más interacciones ({player2_interactions} vs {player1_interactions})"
        else:
            if player1.lies_told > player2.lies_told:
                winner = player1
                winner_reason = f"{winner.display_name} gana por más mentiras en empate de interacciones ({player1.lies_told} vs {player2.lies_told})"
            elif player2.lies_told > player1.lies_told:
                winner = player2
                winner_reason = f"{winner.display_name} gana por más mentiras en empate de interacciones ({player2.lies_told} vs {player1.lies_told})"
            else:
                winner_reason = f"Empate entre {player1.display_name} y {player2.display_name} (mismas interacciones y mentiras)"
    else:
        winner_reason = f"Juego finalizado con {alive_count} supervivientes"
    
    context = {
        'game': game,
        'winner': winner,
        'winner_reason': winner_reason,
        'alive_count': alive_count,
        'all_players': all_players,
    }
    
    return render(request, 'master/game_results.html', context)

@login_required
@user_passes_test(is_staff_user) 
def create_game_view(request):
    """Crear e iniciar un nuevo juego directamente"""
    from players.models import Player
    
    # Verificar si ya existe un juego activo o en espera
    existing_game = Game.get_current_game()
    if existing_game:
        messages.warning(request, f'Ya existe un juego: {existing_game.name} ({existing_game.get_status_display()})')
        return redirect('master:dashboard')
    
    if request.method == 'POST':
        # LIMPIAR JUEGOS FINALIZADOS Y RESETEAR JUGADORES
        Game.cleanup_finished_games()
        Player.reset_all_for_new_game()
        print("[NEW_GAME] Juegos finalizados limpiados y jugadores reseteados")
        
        round_duration = request.POST.get('round_duration', 10)  # Por defecto 10 minutos
        try:
            round_duration = max(1, min(60, int(round_duration)))  # Entre 1 y 60 minutos
        except ValueError:
            round_duration = 10
        
        name = f'Juego de Deducción - {timezone.now().strftime("%d/%m %H:%M")}'
        description = f'Juego local con rondas de {round_duration} minutos'
        
        # Crear el juego
        game = Game.objects.create(
            name=name,
            description=description,
            status='waiting',
            round_duration_seconds=round_duration * 60  # Convertir a segundos
        )
        
        # Inscribir automáticamente a todos los jugadores conectados
        online_players = Player.objects.filter(is_online=True)
        for player in online_players:
            player.join_game()
        
        # Asignar símbolos automáticamente
        Player.assign_suits_to_online_players()
        
        # Iniciar el juego inmediatamente
        game.start_game()
        
        messages.success(request, f'¡Nuevo juego iniciado! Rondas de {round_duration} minutos.')
        return redirect('master:dashboard')
    
    return render(request, 'master/create_game.html')

@login_required
@user_passes_test(is_staff_user)
def game_detail_view(request, game_id):
    """Ver detalles de un juego (redirige al admin por ahora)"""
    return redirect('admin:master_game_change', game_id)
