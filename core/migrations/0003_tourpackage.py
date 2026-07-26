from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_gallery"),
    ]

    operations = [
        migrations.CreateModel(
            name="TourPackage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="packages/")),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Tour Package",
                "verbose_name_plural": "Tour Packages",
                "ordering": ["-created_at"],
            },
        ),
    ]