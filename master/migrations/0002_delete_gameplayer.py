 

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GamePlayer',
        ),
    ]
