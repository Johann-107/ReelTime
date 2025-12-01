# Generated manually to convert string genres to lists

from django.db import migrations
import json


def convert_string_to_list(apps, schema_editor):
    Movie = apps.get_model('movies', 'Movie')
    db_alias = schema_editor.connection.alias
    
    for movie in Movie.objects.using(db_alias).all():
        # Get the raw value
        genre_value = movie.genre
        
        # If it's already a list (JSON), skip
        if isinstance(genre_value, list):
            continue
            
        # If it's a string, convert to list
        if isinstance(genre_value, str):
            if genre_value:
                # Store as JSON list
                movie.genre = json.dumps([genre_value])
            else:
                movie.genre = json.dumps([])
        else:
            # For any other type, set to empty list
            movie.genre = json.dumps([])
            
        movie.save()


def reverse_convert(apps, schema_editor):
    Movie = apps.get_model('movies', 'Movie')
    db_alias = schema_editor.connection.alias
    
    for movie in Movie.objects.using(db_alias).all():
        if isinstance(movie.genre, str):
            try:
                genre_list = json.loads(movie.genre)
                if genre_list and len(genre_list) > 0:
                    movie.genre = genre_list[0]
                else:
                    movie.genre = ''
                movie.save()
            except:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_alter_movieadmindetails_poster'),
    ]

    operations = [
        migrations.RunPython(convert_string_to_list, reverse_convert),
    ]
