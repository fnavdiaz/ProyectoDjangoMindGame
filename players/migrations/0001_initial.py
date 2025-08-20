 

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(help_text='Nombre que se mostrará en el juego', max_length=50, verbose_name='Nombre para mostrar')),
                ('karma_score', models.IntegerField(default=3, help_text='Valor entre 0 y 6 que representa el karma del jugador', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)], verbose_name='Puntuación de Karma')),
                ('suit_symbol', models.CharField(choices=[('♠', 'Picas (Spades)'), ('♥', 'Corazones (Hearts)'), ('♦', 'Diamantes (Diamonds)'), ('♣', 'Tréboles (Clubs)')], help_text='Símbolo correspondiente a los palos de la baraja', max_length=1, verbose_name='Símbolo de palo')),
                ('is_online', models.BooleanField(default=False, help_text='Indica si el jugador está actualmente conectado', verbose_name='¿Está conectado?')),
                ('last_activity', models.DateTimeField(auto_now=True, verbose_name='Última actividad')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('total_games_played', models.IntegerField(default=0, help_text='Número total de juegos en los que ha participado', verbose_name='Juegos jugados')),
                ('total_secrets_discovered', models.IntegerField(default=0, help_text='Número total de secretos que ha descubierto', verbose_name='Secretos descubiertos')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Jugador',
                'verbose_name_plural': 'Jugadores',
                'ordering': ['-karma_score', 'display_name'],
            },
        ),
        migrations.CreateModel(
            name='PlayerGameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('session_score', models.IntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_sessions', to='master.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_sessions', to='players.player')),
            ],
            options={
                'verbose_name': 'Sesión de Jugador',
                'verbose_name_plural': 'Sesiones de Jugadores',
                'ordering': ['-joined_at'],
                'unique_together': {('player', 'game')},
            },
        ),
    ]
