from django.db import migrations, models


def clear_legacy_default_logo(apps, schema_editor):
    User = apps.get_model('user', 'User')
    User.objects.filter(
        photo='https://w7.pngwing.com/pngs/81/570/png-transparent-profile-logo-computer-icons-user-user-blue-heroes-logo.png'
    ).update(photo=None)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='user_photo'),
        ),
        migrations.RunPython(clear_legacy_default_logo, migrations.RunPython.noop),
    ]
