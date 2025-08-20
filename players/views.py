from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Player, PlayerGuess
from .serializers import PlayerSerializer, OnlinePlayerSerializer, LeaderboardSerializer
from master.models import Game


class PlayerViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar perfiles de jugadores"""
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Player.objects.all()
    
    def get_queryset(self):
        """Filtra jugadores según el usuario"""
        if self.request.user.is_staff:
            return Player.objects.all()
        
        return Player.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_online(self, request, pk=None):
        """Marca al jugador como conectado"""
        player = self.get_object()
        player.set_online()
        return Response({'message': 'Jugador marcado como conectado'})
    
    @action(detail=True, methods=['post'])
    def set_offline(self, request, pk=None):
        """Marca al jugador como desconectado"""
        player = self.get_object()
        player.set_offline()
        return Response({'message': 'Jugador marcado como desconectado'})
    
    @action(detail=True, methods=['post'])
    def update_karma(self, request, pk=None):
        """Actualiza el karma del jugador"""
        player = self.get_object()
        action_type = request.data.get('action')  # 'increase' o 'decrease'
        amount = int(request.data.get('amount', 1))
        
        if action_type == 'increase':
            player.increase_karma(amount)
        elif action_type == 'decrease':
            player.decrease_karma(amount)
        else:
            return Response(
                {'error': 'Acción inválida. Use "increase" o "decrease"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': f'Karma {action_type}d en {amount}',
            'new_karma': player.karma_score,
            'karma_level': player.karma_level
        })


class OnlinePlayersView(APIView):
    """Vista para obtener jugadores conectados"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Devuelve la lista de jugadores conectados"""
        online_players = Player.objects.filter(is_online=True).order_by('display_name')
        serializer = OnlinePlayerSerializer(online_players, many=True)
        
        return Response({
            'count': online_players.count(),
            'players': serializer.data
        })


class LeaderboardView(APIView):
    """Vista para el ranking de jugadores"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Devuelve el ranking de jugadores"""
        
        top_players = Player.objects.order_by(
            '-karma_score', 
            '-current_game_score', 
            '-secrets_discovered_this_game',
            'display_name'
        )[:20]  # Top 20
        
        serializer = LeaderboardSerializer(top_players, many=True)
        
        return Response({
            'leaderboard': serializer.data
        })


# ============= VISTAS WEB PARA JUGADORES =============

def player_login_view(request):
    """Vista de login para jugadores"""
    if request.user.is_authenticated:
        try:
            
            player = request.user.player_profile
            return redirect('players:dashboard')
        except Player.DoesNotExist:
            
            Player.objects.create(
                user=request.user,
                display_name=request.user.username
            )
            return redirect('players:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            
            player, created = Player.objects.get_or_create(
                user=user,
                defaults={'display_name': user.username}
            )
            
            
            player.set_online()
            player.join_game()  # Inscribirse automáticamente en el juego
            
            messages.success(request, f'¡Bienvenido, {player.display_name}!')
            return redirect('players:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'players/login.html')

def player_register_view(request):
    """Vista de registro para jugadores"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        display_name = request.POST.get('display_name')
        
        # Verificar que no exista el username
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ya existe un usuario con ese nombre.')
            return render(request, 'players/register.html')
        
        # Verificar que no exista el display_name
        if Player.objects.filter(display_name=display_name).exists():
            messages.error(request, 'Ya existe un jugador con ese nombre para mostrar.')
            return render(request, 'players/register.html')
        
        # Crear usuario
        user = User.objects.create_user(username=username, password=password)
        
        # Crear perfil de jugador
        player = Player.objects.create(
            user=user,
            display_name=display_name
        )
        
        # Login automático
        login(request, user)
        player.set_online()
        player.join_game()  # Inscribirse automáticamente en el juego
        
        messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {player.display_name}!')
        return redirect('players:dashboard')
    
    return render(request, 'players/register.html')

@login_required
def player_dashboard_view(request):
    """Vista del dashboard para jugadores"""
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        
        player = Player.objects.create(
            user=request.user,
            display_name=request.user.username
        )
    
    # Marcar como online (pero mantenerse en el juego)
    player.set_online()
    
    # Obtener juego actual
    current_game = Game.get_current_game()
    
    # Verificar si hay un juego finalizado Y el jugador participó en él
    finished_game = Game.objects.filter(status='finished').order_by('-created_at').first()
    if finished_game and player.is_in_game:
        
        # Verificar que este juego finalizado sea más reciente que cualquier juego activo
        if not current_game or finished_game.created_at > current_game.created_at:
            return redirect('players:game_results', game_id=finished_game.id)
    
    # Verificar si el jugador está muerto
    if player.is_dead:
        
        context = {
            'player': player,
            'is_dead': True,
            'death_reason': player.death_reason,
        }
        return render(request, 'players/death_screen.html', context)
    
    # Obtener todos los jugadores INSCRITOS EN EL JUEGO
    online_players = Player.objects.filter(is_in_game=True).order_by('display_name')
    
    # Obtener comunicaciones guardadas para evitar el parpadeo visual
    player_communications = {}
    if current_game and current_game.status == 'active':
        saved_guesses = PlayerGuess.objects.filter(
            player=player,
            round_number=current_game.current_round
        ).select_related('teller')
        
        for guess in saved_guesses:
            player_communications[guess.teller.id] = guess.told_symbol
    
    context = {
        'player': player,
        'current_game': current_game,
        'online_players': online_players,
        'is_dead': False,
        'player_communications': player_communications,  # Añadir comunicaciones al contexto
    }
    
    return render(request, 'players/dashboard.html', context)

@login_required
def player_logout_view(request):
    """Vista de logout para jugadores - SOLO desconecta de la web, NO del juego"""
    try:
        player = request.user.player_profile
        # Solo marcar como offline de la web, pero MANTENER en el juego
        player.set_offline()
        # NO llamar a player.leave_game() - el jugador sigue participando
    except Player.DoesNotExist:
        pass
    
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente. Sigues participando en el juego.')
    return redirect('players:login')

@login_required
def player_game_results_view(request, game_id):
    """Muestra los resultados del juego para el jugador"""
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        messages.error(request, 'No tienes un perfil de jugador.')
        return redirect('players:dashboard')
    
    game = get_object_or_404(Game, id=game_id)
    
    if game.status != 'finished':
        messages.error(request, 'Solo se pueden ver resultados de juegos finalizados.')
        return redirect('players:dashboard')
    
    # Verificar que el jugador participó en este juego
    if not player.is_in_game:
        messages.error(request, 'No participaste en este juego.')
        return redirect('players:dashboard')
    
    # Determinar ganador usando la misma lógica que finish_game
    alive_players = Player.objects.filter(is_in_game=True, is_dead=False)
    alive_count = alive_players.count()
    
    winner = None
    winner_reason = ""
    is_winner = False
    is_tie = False
    
    if alive_count == 0:
        winner_reason = "Todos los jugadores han muerto. Nadie gana."
    elif alive_count == 1:
        winner = alive_players.first()
        winner_reason = f"{winner.display_name} es el ganador (único superviviente)"
        is_winner = (winner.id == player.id)
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
                is_tie = True
        
        if winner:
            is_winner = (winner.id == player.id)
    else:
        winner_reason = f"Juego finalizado con {alive_count} supervivientes"
    
    context = {
        'game': game,
        'player': player,
        'winner': winner,
        'winner_reason': winner_reason,
        'is_winner': is_winner,
        'is_tie': is_tie,
        'alive_count': alive_count,
    }
    
    return render(request, 'players/game_results.html', context)

@login_required
@require_http_methods(["GET"])
def check_new_game_view(request):
    """Verifica si hay un nuevo juego disponible (AJAX)"""
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return JsonResponse({'new_game_available': True})  # Redirigir al dashboard
    
    # Verificar si hay un juego activo o en espera
    current_game = Game.get_current_game()
    
    # Verificar si hay juegos finalizados
    finished_games_exist = Game.objects.filter(status='finished').exists()
    
    # Si hay un juego nuevo y no hay juegos finalizados, hay un nuevo juego
    new_game_available = bool(current_game and not finished_games_exist)
    
    return JsonResponse({
        'new_game_available': new_game_available,
        'game_status': current_game.status if current_game else None,
        'finished_games_exist': finished_games_exist
    })


# ============= VISTAS AJAX PARA MECÁNICAS DEL JUEGO =============

@login_required
def choose_symbol_view(request):
    """Vista AJAX para que un jugador elija qué símbolo cree que tiene"""
    if request.method == 'POST':
        try:
            player = request.user.player_profile
            chosen_symbol = request.POST.get('symbol')
            
            if chosen_symbol not in ['♠', '♥', '♦', '♣']:
                return JsonResponse({'success': False, 'message': 'Símbolo inválido'})
            
            player.chosen_symbol = chosen_symbol
            player.save()
            
            # NO verificar muerte aquí - solo al cambiar de ronda
            return JsonResponse({
                'success': True, 
                'message': f'Has elegido {chosen_symbol}',
                'chosen_symbol': chosen_symbol
            })
        except Player.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Perfil de jugador no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def tell_player_symbol_view(request):
    """Vista AJAX para registrar lo que otro jugador te dijo sobre tu símbolo"""
    if request.method == 'POST':
        try:
            from .models import PlayerGuess
            from master.models import Game
            
            receiver = request.user.player_profile  # Quien recibe la información (yo)
            teller_player_id = request.POST.get('target_player_id')  # Quien me dijo algo
            told_symbol = request.POST.get('symbol')  # Lo que me dijo sobre mi símbolo
            
            # Validaciones
            if told_symbol not in ['♠', '♥', '♦', '♣']:
                return JsonResponse({'success': False, 'message': 'Símbolo inválido'})
            
            teller_player = get_object_or_404(Player, id=teller_player_id)
            current_game = Game.get_current_game()
            
            if not current_game:
                return JsonResponse({'success': False, 'message': 'No hay juego activo'})
            
            # No puedes registrar que te dijiste a ti mismo
            if receiver == teller_player:
                return JsonResponse({'success': False, 'message': 'No puedes registrar que te dijiste a ti mismo'})
            
            # Crear o actualizar la adivinanza
            # player = quien recibió la información (yo)
            # teller = quien dijo la información (el otro jugador)
            guess, created = PlayerGuess.objects.get_or_create(
                player=receiver,  # YO recibo la información
                teller=teller_player,  # EL OTRO me dijo algo
                round_number=current_game.current_round,
                defaults={'told_symbol': told_symbol}
            )
            
            if not created:
                guess.told_symbol = told_symbol
                guess.save()
            
            action = 'registrado' if created else 'actualizado'
            print(f"[COMMUNICATION] {receiver.display_name} {action} que {teller_player.display_name} le dijo que tiene {told_symbol} (Ronda {current_game.current_round})")
            print(f"[COMMUNICATION] DEBUG: PlayerGuess guardado con ID {guess.id}, ronda {guess.round_number}")
            
            # Verificar que se guardó correctamente
            verification = PlayerGuess.objects.filter(
                player=receiver, 
                teller=teller_player, 
                round_number=current_game.current_round
            ).first()
            if verification:
                print(f"[COMMUNICATION] VERIFICADO: Comunicación guardada correctamente en la base de datos")
            else:
                print(f"[COMMUNICATION] ERROR: No se pudo verificar la comunicación en la base de datos")
            
            return JsonResponse({
                'success': True, 
                'message': f'Has registrado que {teller_player.display_name} te dijo que tienes {told_symbol}',
                'action': action
            })
            
        except Player.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Jugador no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@require_http_methods(["GET"])
def get_player_guesses_view(request):
    """Obtener las comunicaciones que otros jugadores le han dicho al jugador actual"""
    try:
        player = request.user.player_profile
        
        # Obtener el juego actual
        current_game = Game.objects.filter(status='active').first()
        if not current_game:
            return JsonResponse({'success': True, 'guesses': [], 'count': 0})
        
        # Obtener todas las comunicaciones donde este jugador es el receptor
        # en la ronda actual
        guesses = PlayerGuess.objects.filter(
            player=player,  # Quien recibe la comunicación
            round_number=current_game.current_round
        ).select_related('teller')
        
        guesses_data = []
        for guess in guesses:
            # Usar un campo de fecha que exista en el modelo, o manejarlo sin fecha
            timestamp = 'N/A'
            if hasattr(guess, 'created_at'):
                timestamp = guess.created_at.strftime('%H:%M:%S')
            elif hasattr(guess, 'timestamp'):
                timestamp = guess.timestamp.strftime('%H:%M:%S')
            
            guesses_data.append({
                'teller_id': guess.teller.id,
                'teller_name': guess.teller.display_name,
                'told_symbol': guess.told_symbol,
                'timestamp': timestamp
            })
        
        return JsonResponse({
            'success': True,
            'guesses': guesses_data,
            'count': len(guesses_data)
        })
        
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Jugador no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})