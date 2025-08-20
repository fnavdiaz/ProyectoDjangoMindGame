 

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del juego')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('status', models.CharField(choices=[('waiting', 'Esperando jugadores'), ('active', 'En curso'), ('finished', 'Finalizada'), ('cancelled', 'Cancelada')], default='waiting', max_length=20)),
                ('max_players', models.IntegerField(default=6, verbose_name='Máximo de jugadores')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('duration_hours', models.IntegerField(default=24, verbose_name='Duración en horas')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='master_games', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Juego',
                'verbose_name_plural': 'Juegos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SecretInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título del secreto')),
                ('description', models.TextField(verbose_name='Descripción del secreto')),
                ('secret_data', models.JSONField(help_text='Información en formato JSON', verbose_name='Datos secretos')),
                ('difficulty', models.CharField(choices=[('easy', 'Fácil'), ('medium', 'Medio'), ('hard', 'Difícil')], default='medium', max_length=10)),
                ('points_value', models.IntegerField(default=100, verbose_name='Valor en puntos')),
                ('is_discovered', models.BooleanField(default=False, verbose_name='¿Descubierto?')),
                ('discovered_at', models.DateTimeField(blank=True, null=True)),
                ('hints_given', models.IntegerField(default=0, verbose_name='Pistas dadas')),
                ('max_hints', models.IntegerField(default=3, verbose_name='Máximo de pistas')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discovered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discovered_secrets', to=settings.AUTH_USER_MODEL)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secrets', to='master.game')),
            ],
            options={
                'verbose_name': 'Información Secreta',
                'verbose_name_plural': 'Información Secreta',
                'ordering': ['difficulty', '-points_value'],
            },
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Contenido de la pista')),
                ('order', models.IntegerField(verbose_name='Orden de la pista')),
                ('is_given', models.BooleanField(default=False, verbose_name='¿Ya fue dada?')),
                ('given_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('secret', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hints', to='master.secretinfo')),
            ],
            options={
                'verbose_name': 'Pista',
                'verbose_name_plural': 'Pistas',
                'ordering': ['secret', 'order'],
                'unique_together': {('secret', 'order')},
            },
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('score', models.IntegerField(default=0, verbose_name='Puntuación')),
                ('is_active', models.BooleanField(default=True, verbose_name='¿Activo?')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='master.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_games', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Jugador del Juego',
                'verbose_name_plural': 'Jugadores del Juego',
                'ordering': ['-score', 'joined_at'],
                'unique_together': {('game', 'player')},
            },
        ),
    ]
