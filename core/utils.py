from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone


def generate_appointment_number() -> str:
    from .models import Appointment

    year = timezone.localdate().year
    prefix = f"KOC-{year}"
    existing_numbers = Appointment.objects.filter(appointment_number__startswith=prefix).values_list("appointment_number", flat=True)

    highest_sequence = 0
    for number in existing_numbers:
        try:
            sequence_text = str(number)[len(prefix):]
            highest_sequence = max(highest_sequence, int(sequence_text))
        except (TypeError, ValueError):
            continue

    return f"{prefix}{highest_sequence + 1:04d}"


def generate_appointment_letter_pdf(appointment):
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    from .models import CompanyInfo

    company_info = CompanyInfo.objects.order_by("-created_at").first()
    company_name = company_info.company_name if company_info else "Kaleem Overseas Consultants Pvt. Ltd."
    office_address = (
        company_info.office_address
        if company_info and company_info.office_address
        else "HFWQ+3F5 Kaleem Overseas Consultants New, New Rasool Rd, Shadman Town, Mandi Bahauddin, Pakistan"
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    margin_x = 18 * mm
    top_y = page_height - 20 * mm
    brand_blue = HexColor("#0b2b4c")
    brand_gold = HexColor("#b88a2f")

    def draw_wrapped_text(text, x, y, max_width, line_height=12, font_name="Helvetica", font_size=10, color=brand_blue):
        pdf.setFont(font_name, font_size)
        pdf.setFillColor(color)
        words = str(text).split()
        lines = []
        current_line = ""
        for word in words:
            candidate = f"{current_line} {word}".strip()
            if stringWidth(candidate, font_name, font_size) <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        cursor_y = y
        for line in lines:
            pdf.drawString(x, cursor_y, line)
            cursor_y -= line_height
        return cursor_y

    logo_path = Path(settings.MEDIA_ROOT) / "logo.png"
    header_bottom = page_height - 38 * mm
    pdf.setFillColor(HexColor("#f9f5ec"))
    pdf.rect(0, header_bottom, page_width, page_height - header_bottom, fill=1, stroke=0)

    if logo_path.exists():
        pdf.drawImage(str(logo_path), margin_x, page_height - 31 * mm, width=22 * mm, height=22 * mm, preserveAspectRatio=True, mask="auto")
    else:
        pdf.setFillColor(brand_blue)
        pdf.roundRect(margin_x, page_height - 31 * mm, 22 * mm, 22 * mm, 4 * mm, stroke=0, fill=1)
        pdf.setFillColor(HexColor("#ffffff"))
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(margin_x + 11 * mm, page_height - 22 * mm, "KOC")

    pdf.setFillColor(brand_blue)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin_x + 28 * mm, page_height - 18 * mm, company_name)
    pdf.setFont("Helvetica", 10.5)
    pdf.drawString(margin_x + 28 * mm, page_height - 24 * mm, "Professional Visa Consultancy and Travel Services")
    pdf.setStrokeColor(brand_gold)
    pdf.setLineWidth(1.5)
    pdf.line(margin_x, header_bottom + 5 * mm, page_width - margin_x, header_bottom + 5 * mm)

    pdf.setFillColor(brand_blue)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(margin_x, header_bottom - 10 * mm, "Appointment Letter")
    pdf.setFont("Helvetica", 10.5)
    pdf.drawString(page_width - 65 * mm, header_bottom - 10 * mm, f"Appointment ID: {appointment.appointment_number}")

    y = header_bottom - 22 * mm
    details = [
        ("Customer Name", appointment.full_name),
        ("Phone Number", appointment.phone_number),
        ("Email", appointment.email),
        ("Visa Type", appointment.get_visa_type_display()),
        ("Country", appointment.country),
        ("Appointment Date", appointment.preferred_date.strftime("%d %B %Y") if appointment.preferred_date else "Not selected"),
        ("Appointment Time", appointment.preferred_time.strftime("%I:%M %p") if appointment.preferred_time else "Not selected"),
        ("Office Address", office_address),
    ]

    pdf.setFillColor(brand_blue)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin_x, y, "Appointment Details")
    y -= 10 * mm

    for label, value in details:
        pdf.setFillColor(brand_gold)
        pdf.setFont("Helvetica-Bold", 10.5)
        pdf.drawString(margin_x, y, f"{label}:")
        y = draw_wrapped_text(value, margin_x + 42 * mm, y, page_width - margin_x - (margin_x + 42 * mm), line_height=11, font_size=10.2)
        y -= 3 * mm

    y -= 2 * mm
    pdf.setFillColor(brand_blue)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin_x, y, "Instructions")
    y -= 8 * mm

    instructions = [
        "Please bring this appointment letter and your original documents on the scheduled date.",
        "Arrive 15 minutes early to complete any required verification or consultation steps.",
        "If you need to reschedule, contact our office before the appointment time.",
    ]
    pdf.setFont("Helvetica", 10.2)
    for index, instruction in enumerate(instructions, start=1):
        y = draw_wrapped_text(f"{index}. {instruction}", margin_x, y, page_width - 2 * margin_x, line_height=12, font_size=10.2)
        y -= 1.5 * mm

    y -= 12 * mm
    pdf.setStrokeColor(brand_gold)
    pdf.line(margin_x, y, page_width - margin_x, y)
    y -= 12 * mm

    pdf.setFillColor(brand_blue)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, y, "Authorized Signature")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin_x, y - 6 * mm, "Kaleem Overseas Consultants Pvt. Ltd.")
    pdf.line(page_width - 70 * mm, y - 2 * mm, page_width - 25 * mm, y - 2 * mm)
    pdf.drawString(page_width - 67 * mm, y - 8 * mm, "Authorized Signatory")

    pdf.setFillColor(HexColor("#667085"))
    pdf.setFont("Helvetica-Oblique", 8.5)
    pdf.drawCentredString(page_width / 2, 12 * mm, "This is a computer-generated appointment letter issued by Kaleem Overseas Consultants Pvt. Ltd.")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return f"{appointment.appointment_number}.pdf", ContentFile(buffer.read())