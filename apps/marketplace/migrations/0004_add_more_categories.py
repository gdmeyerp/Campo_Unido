from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0003_add_destacado_field'),
    ]

    operations = [
        # This file previously had no Migration class, which caused errors
        # Empty operations list as we're just fixing the file structure
    ] 