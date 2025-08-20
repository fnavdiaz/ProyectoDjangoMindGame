 

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['display_name'], 'verbose_name': 'Jugador', 'verbose_name_plural': 'Jugadores'},
        ),
        migrations.RemoveField(
            model_name='player',
            name='total_games_played',
        ),
        migrations.RemoveField(
            model_name='player',
            name='total_secrets_discovered',
        ),
        migrations.AddField(
            model_name='player',
            name='current_game_score',
            field=models.IntegerField(default=0, help_text='Puntos obtenidos en el juego actual (se resetea cada juego)', verbose_name='Puntuación del juego actual'),
        ),
        migrations.AddField(
            model_name='player',
            name='secrets_discovered_this_game',
            field=models.IntegerField(default=0, help_text='Número de secretos descubiertos en el juego actual (se resetea cada juego)', verbose_name='Secretos descubiertos este juego'),
        ),
        migrations.AlterField(
            model_name='player',
            name='karma_score',
            field=models.IntegerField(default=3, help_text='Valor entre 0 y 6 que representa el karma del jugador (se resetea cada juego)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)], verbose_name='Puntuación de Karma'),
        ),
        migrations.AlterField(
            model_name='player',
            name='suit_symbol',
            field=models.CharField(blank=True, choices=[('♠', 'Picas (Spades)'), ('♥', 'Corazones (Hearts)'), ('♦', 'Diamantes (Diamonds)'), ('♣', 'Tréboles (Clubs)')], help_text='Símbolo correspondiente a los palos de la baraja (se asigna cada juego)', max_length=1, verbose_name='Símbolo de palo'),
        ),
        migrations.DeleteModel(
            name='PlayerGameSession',
        ),
    ]
