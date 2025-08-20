 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0004_remove_game_max_players_remove_game_max_rounds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='round_duration_seconds',
            field=models.IntegerField(default=5, verbose_name='Duración de ronda (segundos)'),
        ),
    ]
