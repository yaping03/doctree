# Generated by Django 2.0 on 2018-01-10 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctree', '0008_knowledge_is_alone'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.IntegerField()),
                ('book_info', models.TextField()),
                ('chapters', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]