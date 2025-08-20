 

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_player_chosen_symbol_alter_player_suit_symbol'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerGuess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('told_symbol', models.CharField(choices=[('♠', 'Picas (Spades)'), ('♥', 'Corazones (Hearts)'), ('♦', 'Diamantes (Diamonds)'), ('♣', 'Tréboles (Clubs)')], max_length=2)),
                ('round_number', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_guesses', to='players.player')),
                ('teller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_guesses', to='players.player')),
            ],
            options={
                'ordering': ['-timestamp'],
                'unique_together': {('player', 'teller', 'round_number')},
            },
        ),
    ]
