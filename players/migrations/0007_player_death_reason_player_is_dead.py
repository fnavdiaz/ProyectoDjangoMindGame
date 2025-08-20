 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0006_player_lies_told_player_truths_told'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='death_reason',
            field=models.CharField(blank=True, help_text='Razón por la cual el jugador fue eliminado', max_length=100, verbose_name='Motivo de muerte'),
        ),
        migrations.AddField(
            model_name='player',
            name='is_dead',
            field=models.BooleanField(default=False, help_text='Indica si el jugador ha sido eliminado del juego actual', verbose_name='¿Está muerto?'),
        ),
    ]
