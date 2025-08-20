from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Player(models.Model):
    """Modelo extendido para jugadores del juego"""
    
    # Símbolos de los palos de la baraja
    SUIT_CHOICES = [
        ('♠', 'Picas (Spades)'),
        ('♥', 'Corazones (Hearts)'),
        ('♦', 'Diamantes (Diamonds)'),
        ('♣', 'Tréboles (Clubs)'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='player_profile'
    )
    display_name = models.CharField(
        max_length=50, 
        verbose_name="Nombre para mostrar",
        help_text="Nombre que se mostrará en el juego"
    )
    
    # DATOS DEL JUEGO ACTUAL (se resetean cada partida)
    karma_score = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        verbose_name="Puntuación de Karma",
        help_text="Valor entre 0 y 6 que representa el karma del jugador (se resetea cada juego)"
    )
    suit_symbol = models.CharField(
        max_length=1,
        choices=SUIT_CHOICES,
        blank=True,
        verbose_name="Símbolo de palo (asignado por el master)",
        help_text="Símbolo correspondiente a los palos de la baraja (se asigna cada juego por el master)"
    )
    chosen_symbol = models.CharField(
        max_length=1,
        choices=SUIT_CHOICES,
        blank=True,
        verbose_name="Símbolo elegido por el jugador",
        help_text="Símbolo que el jugador cree que le corresponde (su elección/adivinanza)"
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name="¿Está conectado a la web?",
        help_text="Indica si el jugador está actualmente conectado a la interfaz web"
    )
    is_in_game = models.BooleanField(
        default=False,
        verbose_name="¿Está participando en el juego?",
        help_text="Indica si el jugador está inscrito en el juego actual (independiente de conexión web)"
    )
    current_game_score = models.IntegerField(
        default=0,
        verbose_name="Puntuación del juego actual",
        help_text="Puntos obtenidos en el juego actual (se resetea cada juego)"
    )
    secrets_discovered_this_game = models.IntegerField(
        default=0,
        verbose_name="Secretos descubiertos este juego",
        help_text="Número de secretos descubiertos en el juego actual (se resetea cada juego)"
    )
    
    # CONTADORES DE MENTIRAS/VERDADES (se resetean cada juego)
    truths_told = models.IntegerField(
        default=0,
        verbose_name="Verdades dichas",
        help_text="Número de veces que este jugador ha dicho la verdad sobre símbolos de otros (se resetea cada juego)"
    )
    lies_told = models.IntegerField(
        default=0,
        verbose_name="Mentiras dichas",
        help_text="Número de veces que este jugador ha mentido sobre símbolos de otros (se resetea cada juego)"
    )
    
    # ESTADO DE MUERTE (se resetea cada juego)
    is_dead = models.BooleanField(
        default=False,
        verbose_name="¿Está muerto?",
        help_text="Indica si el jugador ha sido eliminado del juego actual"
    )
    death_reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Motivo de muerte",
        help_text="Razón por la cual el jugador fue eliminado"
    )
    
    # DATOS PERSISTENTES (se mantienen entre juegos)
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actividad"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ['display_name']
    
    def __str__(self):
        return f"{self.display_name} ({self.get_suit_symbol_display() if self.suit_symbol else 'Sin palo'}) - Karma: {self.karma_score}"
    
    @property
    def karma_level(self):
        """Devuelve el nivel de karma como texto"""
        levels = {
            0: "Muy Bajo",
            1: "Bajo", 
            2: "Regular",
            3: "Normal",
            4: "Bueno",
            5: "Alto",
            6: "Excelente"
        }
        return levels.get(self.karma_score, "Desconocido")
    
    @property
    def suit_emoji(self):
        """Devuelve el emoji del palo para mejor visualización"""
        return self.suit_symbol if self.suit_symbol else "❓"
    
    def decrease_karma(self, amount=1):
        """Decrementa el karma del jugador sin bajar del mínimo"""
        old_karma = self.karma_score
        self.karma_score = max(0, self.karma_score - amount)
        
        # Verificar si el jugador muere por karma 0
        if not self.is_dead and self.karma_score == 0 and old_karma > 0:
            self.kill_player("has llegado a karma 0")
        
        self.save()
    
    def increase_karma(self, amount=1):
        """Incrementa el karma del jugador sin exceder el máximo"""
        old_karma = self.karma_score
        self.karma_score = min(6, self.karma_score + amount)
        
        # Verificar si el jugador muere por karma 6
        if not self.is_dead and self.karma_score == 6 and old_karma < 6:
            self.kill_player("has llegado a karma 6")
        
        self.save()
    
    def kill_player(self, reason):
        """Mata al jugador por el motivo especificado"""
        if not self.is_dead:
            self.is_dead = True
            self.death_reason = reason
            self.save()
            print(f"{self.display_name} ha muerto: {reason}")
    
    def revive_player(self):
        """Revive al jugador (para nuevos juegos)"""
        self.is_dead = False
        self.death_reason = ""
        self.save()
    
    def check_symbol_death(self):
        """Verifica si el jugador debe morir por elegir mal su símbolo"""
        if not self.is_dead and self.suit_symbol:
            if (self.chosen_symbol != self.suit_symbol) or (not self.chosen_symbol):
                print(f"  - MUERTE: {self.chosen_symbol} != {self.suit_symbol}")
                self.kill_player("No has elegido tu símbolo correctamente")
                return True
        
        return False
    
    def set_online(self):
        """Marca al jugador como conectado a la web"""
        self.is_online = True
        self.save()
    
    def set_offline(self):
        """Marca al jugador como desconectado de la web (pero sigue en el juego si estaba)"""
        self.is_online = False
        self.save()
    
    def join_game(self):
        """Inscribe al jugador en el juego actual"""
        self.is_in_game = True
        self.save()
    
    def leave_game(self):
        """Saca al jugador del juego actual"""
        self.is_in_game = False
        self.suit_symbol = ''  # Quitar símbolo cuando sale del juego
        self.save()
    
    def reset_for_new_game(self):
        """Reinicia el jugador para un nuevo juego - SOLO conserva user y display_name"""
        self.karma_score = 3  # Valor por defecto
        self.suit_symbol = ''  # Se asignará cuando se una al juego
        self.chosen_symbol = ''  # Limpiar elección del símbolo
        self.is_in_game = False  # No está en ningún juego hasta que se inscriba
        self.current_game_score = 0
        self.secrets_discovered_this_game = 0
        self.truths_told = 0  # Resetear verdades
        self.lies_told = 0  # Resetear mentiras
        self.is_dead = False  # Revivir para nuevo juego
        self.death_reason = ''  # Limpiar motivo de muerte
        self.save()
        
        # Limpiar todas las adivinanzas de este jugador
        PlayerGuess.objects.filter(player=self).delete()
        PlayerGuess.objects.filter(teller=self).delete()
    
    def reset_for_new_round(self, round_number):
        """Reinicia el jugador para una nueva ronda"""
        self.chosen_symbol = ''  # Limpiar elección del símbolo para la nueva ronda
        self.save()
        
        # Limpiar adivinanzas de rondas anteriores (mantener solo la ronda actual)
        PlayerGuess.objects.filter(player=self).exclude(round_number=round_number).delete()
        PlayerGuess.objects.filter(teller=self).exclude(round_number=round_number).delete()
    
    def assign_suit(self, suit_symbol):
        """Asigna un palo al jugador para el juego actual"""
        self.suit_symbol = suit_symbol
        self.save()
    
    def add_score(self, points):
        """Agrega puntos al jugador en el juego actual"""
        self.current_game_score += points
        self.save()
    
    def discover_secret(self):
        """Incrementa el contador de secretos descubiertos en este juego"""
        self.secrets_discovered_this_game += 1
        self.save()
    
    @classmethod
    def reset_all_for_new_game(cls):
        """Reinicia todos los jugadores para un nuevo juego"""
        cls.objects.all().update(
            karma_score=3,
            suit_symbol='',
            chosen_symbol='',
            is_online=False,
            current_game_score=0,
            secrets_discovered_this_game=0,
            truths_told=0,
            lies_told=0,
            is_dead=False,
            death_reason=''
        )
        # Limpiar todas las adivinanzas
        PlayerGuess.objects.all().delete()
    
    @classmethod
    def reset_all_for_new_round(cls, round_number):
        """Reinicia todos los jugadores para una nueva ronda"""
        cls.objects.all().update(chosen_symbol='')
        # Limpiar adivinanzas de rondas anteriores
        PlayerGuess.objects.exclude(round_number=round_number).delete()
    
    @classmethod
    def assign_suits_to_online_players(cls):
        """Asigna palos automáticamente a jugadores conectados"""
        online_players = cls.objects.filter(is_online=True, suit_symbol='')
        suits = ['♠', '♥', '♦', '♣']
        
        for i, player in enumerate(online_players):
            if i < len(suits):
                player.assign_suit(suits[i])
            else:
                # Si hay más de 4 jugadores, reutilizar palos
                player.assign_suit(suits[i % len(suits)])
    
    @classmethod
    def check_game_end_condition(cls):
        """
        Verifica si el juego debe terminar automáticamente.
        El juego termina cuando quedan 2 o menos jugadores vivos en el juego.
        
        Returns:
            bool: True si el juego debe terminar, False en caso contrario
        """
        alive_players_count = cls.objects.filter(
            is_in_game=True,
            is_dead=False
        ).count()
        
        if alive_players_count <= 2:
            print(f"CONDICIÓN DE FIN DE JUEGO: Solo quedan {alive_players_count} jugador(es) vivo(s)")
            return True
        
        return False
    
    @classmethod
    def get_survivors(cls):
        """
        Obtiene la lista de jugadores supervivientes del juego.
        
        Returns:
            QuerySet: Jugadores que siguen vivos en el juego
        """
        return cls.objects.filter(
            is_in_game=True,
            is_dead=False
        ).order_by('display_name')


class PlayerGuess(models.Model):
    """Modelo para rastrear lo que otros jugadores le dicen a un jugador sobre su símbolo"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_guesses')
    teller = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='given_guesses')
    told_symbol = models.CharField(max_length=2, choices=Player.SUIT_CHOICES)
    round_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['player', 'teller', 'round_number']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.teller.username} told {self.player.username}: {self.told_symbol} (Round {self.round_number})"
