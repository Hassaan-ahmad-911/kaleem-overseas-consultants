from urllib.parse import quote

# Single source of truth for the contact details shown across the site
# (top bar, footer, contact page, booking page, WhatsApp button). Edit them here.
OFFICE_ADDRESS = "HFWQ+3F5 Kaleem Overseas Consultants New, New Rasool Rd, Shadman Town, Mandi Bahauddin, Pakistan"
WHATSAPP_NUMBER = "923086898079"

SITE_INFO = {
    "company_name": "Kaleem Overseas Consultants Pvt. Ltd.",
    "phone_display": "+92 308 6898079",
    "phone_tel": "+923086898079",
    "email": "kaleemoverseasconsultants@gmail.com",
    "whatsapp_number": WHATSAPP_NUMBER,
    "whatsapp_url": f"https://wa.me/{WHATSAPP_NUMBER}?text=" + quote("Hello I want to book a visa consultation"),
    "office_address": OFFICE_ADDRESS,
    "office_area": "Shadman Town, Mandi Bahauddin",
    "branch_office": "Bahria Town (RWP)",
    "hours_days": "Mon - Sat",
    "hours_time": "9:00 AM - 7:00 PM",
    "maps_url": "https://www.google.com/maps/search/?api=1&query=" + quote(OFFICE_ADDRESS),
    "maps_embed_url": "https://www.google.com/maps?q=" + quote(OFFICE_ADDRESS) + "&output=embed",
    "instagram_url": "https://www.instagram.com/kaleemoverseasconsultants?igsh=b3V5cHg0Z2VkeDF5",
    "tiktok_url": "https://www.tiktok.com/@kaleemahmad984?_r=1&_t=ZS-97ZIcIKYRLZ",
    "youtube_url": "https://youtube.com/@kaleemoverseasconsultant?si=p-AouvFgj16iy3ah",
}


def site_info(request):
    return {"site": SITE_INFO}
