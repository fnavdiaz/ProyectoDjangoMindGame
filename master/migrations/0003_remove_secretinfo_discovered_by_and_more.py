 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0002_delete_gameplayer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='secretinfo',
            name='discovered_by',
        ),
        migrations.RemoveField(
            model_name='secretinfo',
            name='game',
        ),
        migrations.RemoveField(
            model_name='game',
            name='duration_hours',
        ),
        migrations.RemoveField(
            model_name='game',
            name='finished_at',
        ),
        migrations.RemoveField(
            model_name='game',
            name='master',
        ),
        migrations.AddField(
            model_name='game',
            name='current_round',
            field=models.IntegerField(default=1, verbose_name='Ronda actual'),
        ),
        migrations.AddField(
            model_name='game',
            name='max_rounds',
            field=models.IntegerField(default=10, verbose_name='Máximo de rondas'),
        ),
        migrations.AddField(
            model_name='game',
            name='round_duration_seconds',
            field=models.IntegerField(default=300, verbose_name='Duración de ronda (segundos)'),
        ),
        migrations.AddField(
            model_name='game',
            name='round_ends_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fin de ronda actual'),
        ),
        migrations.AddField(
            model_name='game',
            name='round_started_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Inicio de ronda actual'),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.CharField(choices=[('waiting', 'Esperando jugadores'), ('active', 'En curso'), ('finished', 'Finalizada')], default='waiting', max_length=20),
        ),
        migrations.DeleteModel(
            name='Hint',
        ),
        migrations.DeleteModel(
            name='SecretInfo',
        ),
    ]
