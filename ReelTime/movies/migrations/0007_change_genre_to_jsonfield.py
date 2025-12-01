# Generated manually for genre field type change

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_convert_genre_to_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='genre',
            field=models.JSONField(default=list, blank=True),
        ),
    ]
