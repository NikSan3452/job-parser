# Generated by Django 4.1.5 on 2023-01-20 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parser", "0002_alter_vacancy_city"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vacancy",
            name="description",
            field=models.TextField(
                max_length=5000, null=True, verbose_name="Описание вакансии"
            ),
        ),
        migrations.AlterField(
            model_name="vacancy",
            name="salary_from",
            field=models.CharField(max_length=50, null=True, verbose_name="Зарплата от"),
        ),
        migrations.AlterField(
            model_name="vacancy",
            name="salary_to",
            field=models.CharField(max_length=50, null=True, verbose_name="Зарплата до"),
        ),
    ]
