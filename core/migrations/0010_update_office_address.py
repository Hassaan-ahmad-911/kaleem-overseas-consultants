from django.db import migrations, models

NEW_OFFICE_ADDRESS = (
    "HFWQ+3F5 Kaleem Overseas Consultants New, New Rasool Rd, Shadman Town, Mandi Bahauddin, Pakistan"
)


def update_office_address(apps, schema_editor):
    CompanyInfo = apps.get_model("core", "CompanyInfo")
    CompanyInfo.objects.filter(office_address="Islamabad, Pakistan").update(office_address=NEW_OFFICE_ADDRESS)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_successstory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="companyinfo",
            name="office_address",
            field=models.TextField(default=NEW_OFFICE_ADDRESS),
        ),
        migrations.RunPython(update_office_address, reverse_code=noop_reverse),
    ]
