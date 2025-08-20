 

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_remove_secretinfo_discovered_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='max_players',
        ),
        migrations.RemoveField(
            model_name='game',
            name='max_rounds',
        ),
    ]
