# Generated by Django 4.2.2 on 2024-06-18 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=150)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, default='', max_length=250)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('stock', models.IntegerField(default=0)),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='products')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('id_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.category')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
