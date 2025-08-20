 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_alter_player_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='is_in_game',
            field=models.BooleanField(default=False, help_text='Indica si el jugador está inscrito en el juego actual (independiente de conexión web)', verbose_name='¿Está participando en el juego?'),
        ),
        migrations.AlterField(
            model_name='player',
            name='is_online',
            field=models.BooleanField(default=False, help_text='Indica si el jugador está actualmente conectado a la interfaz web', verbose_name='¿Está conectado a la web?'),
        ),
    ]
