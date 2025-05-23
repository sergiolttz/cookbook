# Generated by Django 5.1.7 on 2025-05-05 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0022_alter_recipeingredient_measurement_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipeingredient",
            name="measurement",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "---------"),
                    ("gr", "Gramo(s)"),
                    ("kg", "Kilogramo(s)"),
                    ("ml", "Mililitros"),
                    ("l", "Litro(s)"),
                    ("tz", "Taza(s)"),
                    ("cdta", "Cucharadita(s)"),
                    ("cda", "Cucharada(s)"),
                    ("u", "Unidad(es)"),
                    ("pizca", "Pizca(s)"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
