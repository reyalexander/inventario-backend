# Generated by Django 4.2.2 on 2024-06-18 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('documentType', models.IntegerField(blank=True, default=3, null=True)),
                ('document', models.CharField(blank=True, max_length=25, null=True)),
                ('address', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('phone', models.CharField(blank=True, default='', max_length=25, null=True)),
                ('mail', models.CharField(blank=True, default='', max_length=60, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
