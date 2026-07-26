# Generated manually for the gallery success stories feature.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Gallery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_name", models.CharField(max_length=100)),
                ("country", models.CharField(max_length=100)),
                ("visa_type", models.CharField(choices=[("visit", "Visit Visa"), ("family", "Family Visa"), ("business", "Business Visa"), ("tour", "Tour Package")], max_length=20)),
                ("caption", models.TextField()),
                ("image", models.ImageField(upload_to="gallery/")),
                ("is_featured", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Gallery Success Story",
                "verbose_name_plural": "Gallery Success Stories",
                "ordering": ["-is_featured", "-created_at"],
            },
        ),
    ]