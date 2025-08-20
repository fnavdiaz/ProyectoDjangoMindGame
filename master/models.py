from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Game(models.Model):
    """Modelo que representa una partida del juego local"""
    GAME_STATUS_CHOICES = [
        ('waiting', 'Esperando jugadores'),
        ('active', 'En curso'),
        ('finished', 'Finalizada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre del juego")
    description = models.TextField(blank=True, verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=GAME_STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    
    
    current_round = models.IntegerField(default=1, verbose_name="Ronda actual")
    round_duration_seconds = models.IntegerField(default=30, verbose_name="Duración de ronda (segundos)")  # Cambiado a 30 segundos para pruebas
    round_started_at = models.DateTimeField(null=True, blank=True, verbose_name="Inicio de ronda actual")
    round_ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin de ronda actual")
    
    
    is_paused = models.BooleanField(default=False, verbose_name="Ronda pausada")
    paused_at = models.DateTimeField(null=True, blank=True, verbose_name="Momento de pausa")
    paused_duration = models.IntegerField(default=0, verbose_name="Duración total pausada (segundos)")
    
    class Meta:
        verbose_name = "Juego"
        verbose_name_plural = "Juegos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - Ronda {self.current_round} - {self.get_status_display()}"
    
    def start_game(self):
        """Inicia el juego y la primera ronda"""
        
        if self.players_count < 1:  # Temporal para pruebas - era 3
            return False  # No se puede iniciar
        
        
        from players.models import Player
        Player.reset_all_for_new_game()
        print("[GAME_START] Contadores de mentiras/verdades reseteados para nuevo juego")
            
        self.status = 'active'
        self.started_at = timezone.now()
        self.start_new_round()
        
        
        self.update_players_for_new_round()
        
        self.save()
        return True
    
    def start_new_round(self):
        """Inicia una nueva ronda"""
        now = timezone.now()
        self.round_started_at = now
        self.round_ends_at = now + timezone.timedelta(seconds=self.round_duration_seconds)
        
        
        self.is_paused = False
        self.paused_at = None
        self.paused_duration = 0
        
        self.save()
    
    def advance_round(self):
        """Avanza a la siguiente ronda o termina el juego si solo quedan 0-2 jugadores"""
        print(f"[ADVANCE_ROUND] Llamado para ronda {self.current_round}")
        
        
        self.calculate_truths_and_lies(self.current_round)
        
        self.current_round += 1
        self.start_new_round()
        self.update_players_for_new_round()
    
    def finish_game(self):
        """Finaliza el juego y determina el ganador"""
        from players.models import Player
        
        
        alive_players = Player.objects.filter(is_in_game=True, is_dead=False)
        alive_count = alive_players.count()
        
        print(f"\n=== FINALIZANDO JUEGO ===")
        print(f"Jugadores vivos: {alive_count}")
        
        winner = None
        winner_reason = ""
        
        if alive_count == 0:
            
            print("🚫 RESULTADO: Todos los jugadores han muerto. NADIE GANA.")
            winner_reason = "Todos los jugadores han muerto. Nadie gana."
            
        elif alive_count == 1:
            
            winner = alive_players.first()
            print(f"🏆 GANADOR: {winner.display_name} (único superviviente)")
            winner_reason = f"{winner.display_name} es el ganador (único superviviente)"
            
        elif alive_count == 2:
            
            players_list = list(alive_players.order_by('-lies_told', '-truths_told'))
            player1, player2 = players_list[0], players_list[1]
            
            
            player1_interactions = player1.lies_told + player1.truths_told
            player2_interactions = player2.lies_told + player2.truths_told
            
            print(f"🎯 DESEMPATE ENTRE DOS SUPERVIVIENTES:")
            print(f"  {player1.display_name}: {player1_interactions} interacciones ({player1.lies_told} mentiras + {player1.truths_told} verdades)")
            print(f"  {player2.display_name}: {player2_interactions} interacciones ({player2.lies_told} mentiras + {player2.truths_told} verdades)")
            
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
                    
                    print("🤝 EMPATE: Mismas interacciones y mismas mentiras")
                    winner_reason = f"Empate entre {player1.display_name} y {player2.display_name} (mismas interacciones y mentiras)"
            
            if winner:
                print(f" GANADOR: {winner.display_name}")
                print(f" RAZÓN: {winner_reason}")
            else:
                print(f" RESULTADO: {winner_reason}")
        
        else:
            
            print(f" ADVERTENCIA: Juego finalizado con {alive_count} jugadores vivos")
            winner_reason = f"Juego finalizado con {alive_count} supervivientes"
        
        
        self._game_result = {
            'winner': winner,
            'winner_reason': winner_reason,
            'alive_count': alive_count
        }
        
        print("=" * 50)
        
        self.status = 'finished'
        self.save()
    
    def pause_round(self):
        """Pausa la ronda actual"""
        if self.status != 'active' or self.is_paused:
            return False
        
        self.is_paused = True
        self.paused_at = timezone.now()
        self.save()
        return True
    
    def resume_round(self):
        """Reanuda la ronda pausada"""
        if self.status != 'active' or not self.is_paused:
            return False
        
        
        if self.paused_at:
            pause_time = (timezone.now() - self.paused_at).total_seconds()
            self.paused_duration += int(pause_time)
        
        self.is_paused = False
        self.paused_at = None
        self.save()
        return True
    
    def update_players_for_new_round(self):
        """Actualiza los datos de jugadores para la nueva ronda"""
        import random
        from players.models import Player
        
        players = Player.objects.filter(is_in_game=True)
        
        
        available_symbols = [choice[0] for choice in Player.SUIT_CHOICES]  # ['♠', '♥', '♦', '♣']
        
        for player in players:
            
            random_symbol = random.choice(available_symbols)
            player.suit_symbol = random_symbol
            
            player.chosen_symbol = ''
            player.save()
            
        
        from players.models import PlayerGuess
        PlayerGuess.objects.filter(round_number__lt=self.current_round).delete()
            
        print(f"Ronda {self.current_round}: Símbolos asignados a {players.count()} jugadores")
    
    def calculate_truths_and_lies(self, finished_round):
        """Calcula las mentiras y verdades de la ronda que acaba de terminar"""
        from players.models import Player, PlayerGuess
        
        print(f"\n=== ANÁLISIS RONDA {finished_round} ===")
        
        
        all_guesses = PlayerGuess.objects.all()
        print(f"DEBUG: Total de comunicaciones en base de datos: {all_guesses.count()}")
        for guess in all_guesses:
            print(f"  - Ronda {guess.round_number}: {guess.teller.display_name} -> {guess.player.display_name} ({guess.told_symbol})")
        
        
        round_guesses = PlayerGuess.objects.filter(round_number=finished_round)
        
        print(f"Total de comunicaciones en la ronda {finished_round}: {round_guesses.count()}")
        
        
        players = Player.objects.filter(is_in_game=True)
        print(f"\n💀 VERIFICACIÓN DE MUERTES POR SÍMBOLO INCORRECTO:")
        for player in players:
            if not player.is_dead:  # Solo verificar jugadores vivos
                death_occurred = player.check_symbol_death()
                if death_occurred:
                    print(f"  💀 {player.display_name} eliminado: eligió {player.chosen_symbol} pero tenía {player.suit_symbol}")
                else:
                    if player.chosen_symbol and player.suit_symbol:
                        print(f"  ✅ {player.display_name} eligió correctamente: {player.chosen_symbol}")
                    else:
                        print(f"  ⚠️ {player.display_name} no eligió símbolo o no tiene símbolo asignado")
        
        
        if round_guesses.count() == 0:
            print("No hay comunicaciones para analizar en esta ronda.")
            print("=" * 40)
            print(" NOTA: Los contadores se resetearán automáticamente al iniciar un nuevo juego")
            print("=" * 40)
            return
        
        
        round_truths = {}  # Contador de verdades por jugador en esta ronda
        round_lies = {}    # Contador de mentiras por jugador en esta ronda
        
        
        for player in Player.objects.filter(is_in_game=True):
            round_truths[player.id] = 0
            round_lies[player.id] = 0
        
        for guess in round_guesses:
            
            
            actual_symbol = guess.player.suit_symbol
            told_symbol = guess.told_symbol
            
            print(f"  Analizando: {guess.teller.display_name} le dijo a {guess.player.display_name}")
            print(f"    Símbolo real de {guess.player.display_name}: {actual_symbol}")
            print(f"    Lo que le dijo {guess.teller.display_name}: {told_symbol}")
            
            if actual_symbol == told_symbol:
                
                guess.teller.truths_told += 1  # Contador global del juego
                round_truths[guess.teller.id] += 1  # Contador de esta ronda
                print(f"    ✓ VERDAD - {guess.teller.display_name} ahora tiene {guess.teller.truths_told} verdades")
            else:
                
                guess.teller.lies_told += 1  # Contador global del juego
                round_lies[guess.teller.id] += 1  # Contador de esta ronda
                print(f"    ✗ MENTIRA - {guess.teller.display_name} ahora tiene {guess.teller.lies_told} mentiras")
            
            guess.teller.save()
        
        
        players = Player.objects.filter(is_in_game=True)
        print(f"\nRESUMEN RONDA {finished_round}:")
        for player in players:
            print(f"  {player.display_name} -> mentiras: {player.lies_told}, verdades: {player.truths_told}")
        
        
        print(f"\n📊 AJUSTE DE KARMA RONDA {finished_round}:")
        for player in players:
            old_karma = player.karma_score
            
            
            player_round_lies = round_lies[player.id]
            player_round_truths = round_truths[player.id]
            
            if player_round_lies > player_round_truths:
                
                player.increase_karma(1)  # Usar método que verifica muerte
                change = f"📈 +1 (más mentiras: {player_round_lies} vs {player_round_truths})"
            elif player_round_truths > player_round_lies:
                
                player.decrease_karma(1)  # Usar método que verifica muerte
                change = f"📉 -1 (más verdades: {player_round_truths} vs {player_round_lies})"
            else:
                
                if player_round_lies == 0 and player_round_truths == 0:
                    change = "➡️ sin cambio (no comunicó)"
                else:
                    change = f"➡️ sin cambio (equilibrado: {player_round_truths} vs {player_round_lies})"
            
            
            
            if old_karma != player.karma_score:
                print(f"  {player.display_name}: Karma {old_karma} → {player.karma_score} {change}")
                if player.is_dead:
                    print(f"    💀 {player.display_name} ha sido eliminado: {player.death_reason}")
            else:
                print(f"  {player.display_name}: Karma {player.karma_score} {change}")
        
        print("=" * 40)
        print("💡 NOTA: Los contadores se resetearán automáticamente al iniciar un nuevo juego")
        print("=" * 40)
    

    
    @property
    def time_remaining_in_round(self):
        """Devuelve el tiempo restante en la ronda actual en segundos"""
        if not self.round_ends_at or self.status != 'active':
            return 0
        
        now = timezone.now()
        
        
        if self.is_paused and self.paused_at:
            return int((self.round_ends_at - self.paused_at).total_seconds())
        
        
        adjusted_end_time = self.round_ends_at + timezone.timedelta(seconds=self.paused_duration)
        
        if now >= adjusted_end_time:
            return 0
        
        return int((adjusted_end_time - now).total_seconds())
    
    @property
    def is_round_finished(self):
        """Verifica si la ronda actual ha terminado"""
        if not self.round_ends_at or self.is_paused:
            return False
        
        now = timezone.now()
        
        adjusted_end_time = self.round_ends_at + timezone.timedelta(seconds=self.paused_duration)
        return now >= adjusted_end_time
    
    def finish_and_cleanup(self):
        """Finaliza el juego y limpia los datos"""
        from players.models import Player
        
        
        self.finish_game()
        
        # Resetear jugadores para el próximo juego
        Player.reset_all_for_new_game()
    
    @classmethod
    def get_current_game(cls):
        """Devuelve el juego actual (activo o en espera)"""
        return cls.objects.filter(
            status__in=['waiting', 'active']
        ).first()
    
    @classmethod 
    def cleanup_finished_games(cls):
        """Limpia juegos finalizados"""
        finished_games = cls.objects.filter(status='finished')
        finished_games.delete()
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def players_count(self):
        """Cuenta jugadores INSCRITOS EN EL JUEGO"""
        from players.models import Player
        return Player.objects.filter(is_in_game=True).count()
    
    @property
    def connected_players(self):
        """Devuelve los jugadores INSCRITOS EN EL JUEGO"""
        from players.models import Player
        return Player.objects.filter(is_in_game=True)
