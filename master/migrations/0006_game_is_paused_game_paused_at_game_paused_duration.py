 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_alter_game_round_duration_seconds'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='is_paused',
            field=models.BooleanField(default=False, verbose_name='Ronda pausada'),
        ),
        migrations.AddField(
            model_name='game',
            name='paused_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Momento de pausa'),
        ),
        migrations.AddField(
            model_name='game',
            name='paused_duration',
            field=models.IntegerField(default=0, verbose_name='Duración total pausada (segundos)'),
        ),
    ]
