from django.db import migrations


def seed_content(apps, schema_editor):
    CompanyInfo = apps.get_model("core", "CompanyInfo")
    Country = apps.get_model("core", "Country")
    Service = apps.get_model("core", "Service")

    CompanyInfo.objects.update_or_create(
        id=1,
        defaults={
            "company_name": "Kaleem Overseas Consultants Pvt. Ltd.",
            "tagline": "Professional Visa Consultancy and Travel Services",
            "about_text": "Trusted visit visa, business visa, appointment booking, and travel support for clients who want a smooth overseas journey.",
            "mission": "To provide reliable visa consultancy and professional travel services with honesty, clarity, and care.",
            "vision": "To be a trusted name in visit visa and business visa consultancy, travel planning, and customer support.",
            "why_choose_us": "Professional guidance, fast communication, accurate documentation, and premium support.",
            "director_name": "Kaleem Ahmed",
            "director_title": "Owner & Director",
            "director_message": "We focus on practical guidance, honest communication, and dependable service for every client.",
        },
    )

    services = [
        ("Visit Visa Consultancy", "Complete assistance for tourist and short-stay visit visa applications with smooth documentation support.", "fa-solid fa-passport", 1),
        ("Family Visit Visa", "Guidance for family-based travel, invitation letters, and supportive documentation.", "fa-solid fa-people-roof", 2),
        ("Business Visit Visa", "Support for meetings, trade visits, and business travel applications.", "fa-solid fa-briefcase", 3),
        ("Travel Consultation", "Practical advice on destinations, timelines, documents, and the best travel route.", "fa-solid fa-suitcase-rolling", 4),
        ("Documentation Support", "Preparation and verification of required travel and visa documents.", "fa-solid fa-file-signature", 5),
        ("Flight Bookings", "International flight reservation and travel arrangement services.", "fa-solid fa-plane-departure", 6),
        ("Hotel Reservations", "Worldwide hotel booking services according to client budget and requirements.", "fa-solid fa-hotel", 7),
        ("International Tour Packages", "Customized international tours for families, couples, groups, and individuals.", "fa-solid fa-earth-asia", 8),
    ]
    for name, description, icon, order in services:
        Service.objects.update_or_create(
            name=name,
            defaults={"description": description, "icon": icon, "display_order": order, "is_active": True},
        )

    visit_countries = [
        ("USA", "Visit", "Tourism, family visits, and short stays.", "Passport copy, photo, bank statement, travel history, and supporting documents."),
        ("Canada", "Visit", "Visit visa guidance for tourism and family trips.", "Passport copy, photo, proof of funds, itinerary, and supporting documents."),
        ("Serbia", "Visit", "Short-stay travel and tourism support.", "Passport copy, photo, itinerary, and supporting documents."),
        ("Albania", "Visit", "Tourism and short visit guidance.", "Passport copy, photo, hotel booking, and travel plan."),
        ("Turkey", "Visit", "Popular destination for tours and short stays.", "Passport copy, photo, booking details, and financial proof."),
        ("New Zealand", "Visit", "Travel assistance for tourism and family visits.", "Passport copy, photo, financial documents, and itinerary."),
        ("Belgium", "Visit", "Short-stay Schengen visit support.", "Passport copy, photo, travel insurance, and supporting documents."),
        ("Switzerland", "Visit", "Visit and tourism visa guidance.", "Passport copy, photo, hotel bookings, and proof of funds."),
        ("Australia", "Visit", "Visit visa support for travel and family visits.", "Passport copy, photo, bank statement, and itinerary."),
        ("Sri Lanka", "Visit", "Holiday and short-stay travel support.", "Passport copy, photo, and travel details."),
        ("Malaysia", "Visit", "Tourism and family travel guidance.", "Passport copy, photo, and booking details."),
        ("Thailand", "Visit", "Holiday and tourism assistance.", "Passport copy, photo, itinerary, and booking proof."),
        ("Indonesia", "Visit", "Travel planning for short visits and tours.", "Passport copy, photo, and travel plan."),
        ("Azerbaijan", "Visit", "Short trip and tourism support.", "Passport copy, photo, and supporting documents."),
    ]

    business_countries = [
        ("China", "Business", "Business travel and trade visit guidance.", "Passport copy, invitation letter, company documents, and supporting papers."),
        ("Netherlands", "Business", "Professional visit and business meeting support.", "Passport copy, invitation letter, company profile, and supporting documents."),
        ("Germany", "Business", "Business trips and scheduled professional visits.", "Passport copy, invitation letter, company details, and supporting documents."),
    ]

    for name, category, description, requirements in visit_countries + business_countries:
        Country.objects.update_or_create(
            name=name,
            defaults={
                "visa_category": "visit" if category == "Visit" else "business",
                "description": description,
                "requirements": requirements,
            },
        )


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_companyinfo_contactmessage_service_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_content, reverse_code=noop_reverse),
    ]
