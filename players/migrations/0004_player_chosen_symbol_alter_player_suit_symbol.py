 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_player_is_in_game_alter_player_is_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='chosen_symbol',
            field=models.CharField(blank=True, choices=[('♠', 'Picas (Spades)'), ('♥', 'Corazones (Hearts)'), ('♦', 'Diamantes (Diamonds)'), ('♣', 'Tréboles (Clubs)')], help_text='Símbolo que el jugador cree que le corresponde (su elección/adivinanza)', max_length=1, verbose_name='Símbolo elegido por el jugador'),
        ),
        migrations.AlterField(
            model_name='player',
            name='suit_symbol',
            field=models.CharField(blank=True, choices=[('♠', 'Picas (Spades)'), ('♥', 'Corazones (Hearts)'), ('♦', 'Diamantes (Diamonds)'), ('♣', 'Tréboles (Clubs)')], help_text='Símbolo correspondiente a los palos de la baraja (se asigna cada juego por el master)', max_length=1, verbose_name='Símbolo de palo (asignado por el master)'),
        ),
    ]
