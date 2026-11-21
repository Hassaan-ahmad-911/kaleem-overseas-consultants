import re
import shutil
import tempfile
from datetime import date
from unittest import mock

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Appointment
from .utils import phones_match

TEMP_MEDIA = tempfile.mkdtemp()


def make_appointment(**overrides):
    fields = {
        "full_name": "Test Client",
        "phone_number": "0308-1234567",
        "email": "client@example.com",
        "city": "Lahore",
        "visa_type": "visit",
        "country": "Turkey",
        "preferred_date": date(2026, 12, 1),
        "message": "Need help",
    }
    fields.update(overrides)
    return Appointment.objects.create(**fields)


class PhonesMatchTests(TestCase):
    def test_formats_of_same_number_match(self):
        self.assertTrue(phones_match("0308-1234567", "+92 308 1234567"))
        self.assertTrue(phones_match("+923081234567", "03081234567"))

    def test_different_numbers_do_not_match(self):
        self.assertFalse(phones_match("0308-1234567", "0308-7654321"))
        self.assertFalse(phones_match("0308-1234567", ""))


class AppointmentNumberTests(TestCase):
    def test_numbers_are_sequential_per_year(self):
        first = make_appointment()
        second = make_appointment()
        self.assertRegex(first.appointment_number, r"^KOC-\d{4}0001$")
        self.assertEqual(int(second.appointment_number[-4:]), 2)

    def test_retries_when_number_already_taken(self):
        existing = make_appointment()
        taken, fresh = existing.appointment_number, existing.appointment_number[:-4] + "0099"
        with mock.patch("core.models.generate_appointment_number", side_effect=[taken, fresh]):
            appointment = make_appointment()
        self.assertEqual(appointment.appointment_number, fresh)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class AppointmentPrivacyTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.appointment = make_appointment()
        self.status_url = reverse("appointment_status")
        self.letter_url = reverse("download_appointment_letter", args=[self.appointment.appointment_number])

    def lookup(self, phone):
        return self.client.post(self.status_url, {"appointment_number": self.appointment.appointment_number.lower(), "phone_number": phone})

    def test_number_alone_does_not_reveal_appointment(self):
        response = self.client.get(self.status_url, {"appointment_number": self.appointment.appointment_number})
        self.assertIsNone(response.context["appointment"])
        self.assertNotContains(response, "Test Client")

    def test_wrong_phone_is_rejected(self):
        response = self.lookup("0300-0000000")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["appointment"])
        self.assertIn("danger", [m.tags for m in get_messages(response.wsgi_request)])

    def test_correct_phone_in_any_format_shows_appointment(self):
        response = self.lookup("+92 308 1234567")
        self.assertRedirects(response, f"{self.status_url}?appointment_number={self.appointment.appointment_number}")
        response = self.client.get(response.url)
        self.assertEqual(response.context["appointment"], self.appointment)

    def test_booking_lets_the_booker_see_their_status(self):
        response = self.client.post(reverse("book_appointment"), {
            "full_name": "New Client", "phone_number": "0311-2223334", "email": "new@example.com", "city": "Multan",
            "visa_type": "business", "country": "China", "preferred_date": "2026-12-05", "preferred_time": "10:30",
            "message": "Business trip",
        })
        number = Appointment.objects.get(full_name="New Client").appointment_number
        response = self.client.get(response.url)
        self.assertContains(response, "New Client")
        self.assertContains(response, number)

    def test_letter_download_requires_verification(self):
        self.appointment.status = Appointment.STATUS_APPROVED
        self.appointment.save()
        response = self.client.get(self.letter_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.status_url))

        self.lookup("03081234567")
        response = self.client.get(self.letter_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(f'filename="{self.appointment.appointment_number}.pdf"', response["Content-Disposition"])

    def test_letter_file_name_is_not_guessable(self):
        self.appointment.status = Appointment.STATUS_APPROVED
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.assertTrue(re.search(r"-[0-9a-f]{16}\.pdf$", self.appointment.appointment_letter.name))
