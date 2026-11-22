import re
import shutil
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock
from zoneinfo import ZoneInfo

from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Offer
from .templatetags.formatting import pkr
from .utils import phones_match
from .validators import validate_video_size, youtube_video_id

# Smallest valid GIF, used as a stand-in banner image.
TINY_GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"

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


OFFER_MEDIA = tempfile.mkdtemp()
YOUTUBE_LINK = "https://youtu.be/dQw4w9WgXcQ"


def make_offer(**overrides):
    fields = {
        "title": "Dubai Visit Visa",
        "short_description": "Fast processing for families",
        "media_type": Offer.MEDIA_IMAGE,
        "banner_image": SimpleUploadedFile("banner.gif", TINY_GIF, content_type="image/gif"),
    }
    fields.update(overrides)
    return Offer.objects.create(**fields)


def video_offer(**overrides):
    fields = {"title": "Video offer", "short_description": "Watch this", "media_type": Offer.MEDIA_VIDEO}
    fields.update(overrides)
    return Offer(**fields)


@override_settings(MEDIA_ROOT=OFFER_MEDIA)
class OfferTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(OFFER_MEDIA, ignore_errors=True)

    def test_visible_hides_inactive_and_expired_offers(self):
        today = timezone.localdate()
        no_expiry = make_offer(title="No expiry")
        ends_today = make_offer(title="Ends today", valid_until=today)
        make_offer(title="Expired", valid_until=today - timedelta(days=1))
        make_offer(title="Inactive", is_active=False)
        self.assertEqual(set(Offer.objects.visible()), {no_expiry, ends_today})

    def test_ordering_is_display_order_then_newest(self):
        older = make_offer(title="Older", display_order=1)
        newer = make_offer(title="Newer", display_order=1)
        first = make_offer(title="First", display_order=0)
        Offer.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))
        self.assertEqual(list(Offer.objects.all()), [first, newer, older])

    def test_image_offer_requires_banner(self):
        offer = Offer(title="T", short_description="S", media_type=Offer.MEDIA_IMAGE)
        with self.assertRaises(ValidationError) as raised:
            offer.full_clean()
        self.assertIn("banner_image", raised.exception.message_dict)

    def test_video_offer_needs_exactly_one_video_source(self):
        neither = video_offer()
        both = video_offer(video_url=YOUTUBE_LINK, video_file=SimpleUploadedFile("clip.mp4", b"0000", content_type="video/mp4"))
        for offer in (neither, both):
            with self.assertRaises(ValidationError):
                offer.full_clean()
        video_offer(video_url=YOUTUBE_LINK).full_clean()
        video_offer(video_file=SimpleUploadedFile("clip.mp4", b"0000", content_type="video/mp4")).full_clean()

    def test_rejects_non_youtube_links_and_other_video_formats(self):
        with self.assertRaises(ValidationError) as raised:
            video_offer(video_url="https://vimeo.com/123456").full_clean()
        self.assertIn("video_url", raised.exception.message_dict)
        with self.assertRaises(ValidationError) as raised:
            video_offer(video_file=SimpleUploadedFile("clip.avi", b"0000")).full_clean()
        self.assertIn("video_file", raised.exception.message_dict)

    def test_video_size_limit_is_50_mb(self):
        validate_video_size(SimpleNamespace(size=50 * 1024 * 1024))
        with self.assertRaises(ValidationError):
            validate_video_size(SimpleNamespace(size=50 * 1024 * 1024 + 1))

    def test_offer_price_cannot_exceed_original_price(self):
        offer = Offer(title="T", short_description="S", banner_image="offers/banners/x.gif", original_price=Decimal("100"), offer_price=Decimal("120"))
        with self.assertRaises(ValidationError) as raised:
            offer.full_clean()
        self.assertIn("offer_price", raised.exception.message_dict)

    def test_youtube_links_become_embed_urls(self):
        for url in [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
            "https://youtu.be/dQw4w9WgXcQ?si=abc123",
            "https://youtube.com/shorts/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        ]:
            self.assertEqual(Offer(video_url=url).youtube_embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")
        self.assertIsNone(youtube_video_id("https://example.com/watch?v=dQw4w9WgXcQ"))
        self.assertEqual(Offer(video_url="").youtube_embed_url, "")

    def test_ends_at_is_end_of_valid_until_day_in_pakistan_time(self):
        offer = Offer(valid_until=date(2026, 12, 31))
        self.assertEqual(offer.ends_at, datetime(2026, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("Asia/Karachi")))
        self.assertEqual(offer.ends_at.utcoffset(), timedelta(hours=5))
        self.assertEqual(offer.ends_at.isoformat(), "2026-12-31T23:59:59+05:00")
        self.assertIsNone(Offer(valid_until=None).ends_at)

    def test_countdown_rendered_only_for_offers_with_valid_until(self):
        dated = make_offer(title="Dated Offer", valid_until=timezone.localdate() + timedelta(days=10))
        make_offer(title="Open-ended Offer")
        expected = f'data-ends-at="{dated.ends_at.isoformat()}"'
        for url in (reverse("home"), reverse("offers")):
            response = self.client.get(url)
            self.assertContains(response, "Open-ended Offer")
            self.assertContains(response, expected, count=1)
            self.assertContains(response, "data-ends-at=", count=1)
            # The date stays visible without JavaScript; the countdown is revealed by offers.js.
            self.assertContains(response, f"Valid until {dated.valid_until.day} ")
            self.assertContains(response, "js/offers.js")

    def test_pkr_formatting(self):
        self.assertEqual(pkr(Decimal("45000")), "PKR 45,000")
        self.assertEqual(pkr(Decimal("1250.50")), "PKR 1,250.50")
        self.assertEqual(pkr(None), "")

    def test_home_slider_shows_visible_offers_only(self):
        deal = make_offer(title="Turkey Tour Deal", discount_label="20% OFF", original_price=Decimal("60000"), offer_price=Decimal("45000"))
        make_offer(title="Old Deal", valid_until=timezone.localdate() - timedelta(days=3))
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="offersCarousel"')
        self.assertContains(response, "Latest Offers")
        self.assertContains(response, "Turkey Tour Deal")
        self.assertContains(response, f'href="{reverse("offers")}#offer-{deal.pk}"')
        self.assertContains(response, "20% OFF")
        self.assertContains(response, "PKR 60,000")
        self.assertContains(response, "PKR 45,000")
        self.assertNotContains(response, "Old Deal")
        # Booking / WhatsApp buttons are only on the Offers page now.
        self.assertNotContains(response, "Ask on WhatsApp")
        self.assertNotContains(response, "offer-actions")

    def test_home_hides_slider_when_no_offers(self):
        self.assertNotContains(self.client.get(reverse("home")), 'id="offersCarousel"')

    def test_single_offer_is_static_without_controls(self):
        make_offer(title="Only Offer")
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="carousel-item offer-slide', count=1)
        self.assertNotContains(response, "offers-carousel--multi")
        self.assertNotContains(response, 'data-bs-slide="next"')
        self.assertNotContains(response, 'data-bs-slide-to=')
        self.assertContains(response, "View all")

    def test_three_offers_render_three_slides_with_controls(self):
        for number in range(3):
            make_offer(title=f"Offer {number}", display_order=number)
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="carousel-item offer-slide', count=3)
        self.assertContains(response, "offers-carousel--multi")
        # Each slide carries its own controls row: prev, next and one dot per offer.
        self.assertContains(response, 'data-bs-slide="prev"', count=3)
        self.assertContains(response, 'data-bs-slide="next"', count=3)
        self.assertContains(response, 'data-bs-slide-to=', count=9)
        self.assertContains(response, 'class="offer-dot is-current"', count=3)

    def test_offers_page_and_old_package_links(self):
        offer = make_offer(title="Visit Visa Bundle", description="Includes hotel booking.")
        response = self.client.get(reverse("offers"))
        self.assertContains(response, "Visit Visa Bundle")
        self.assertContains(response, "Includes hotel booking.")
        self.assertContains(response, f'id="offer-{offer.pk}"')
        self.assertContains(response, "btn btn-sm btn-offer-whatsapp")
        self.assertContains(response, "wa.me/923086898079?text=")
        self.assertRedirects(self.client.get("/packages/"), reverse("offers"))
        self.assertRedirects(self.client.get("/packages/5/"), reverse("offers"))
