 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0005_playerguess'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='lies_told',
            field=models.IntegerField(default=0, help_text='Número de veces que este jugador ha mentido sobre símbolos de otros (se resetea cada juego)', verbose_name='Mentiras dichas'),
        ),
        migrations.AddField(
            model_name='player',
            name='truths_told',
            field=models.IntegerField(default=0, help_text='Número de veces que este jugador ha dicho la verdad sobre símbolos de otros (se resetea cada juego)', verbose_name='Verdades dichas'),
        ),
    ]
