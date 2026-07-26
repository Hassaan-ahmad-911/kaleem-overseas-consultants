from django.db import models
from django.utils import timezone

from .utils import generate_appointment_letter_pdf, generate_appointment_number


class CompanyInfo(models.Model):
    company_name = models.CharField(max_length=200, default="Kaleem Overseas Consultants Pvt. Ltd.")
    tagline = models.CharField(max_length=255, default="Professional Visa Consultancy and Travel Services")
    about_text = models.TextField(default="Trusted visa guidance, appointments, and travel support for clients who want a smooth overseas journey.")
    mission = models.TextField(default="To provide reliable visa consultancy and professional travel services with honesty, clarity, and care.")
    vision = models.TextField(default="To be a trusted name in visit visa and business visa consultancy, travel planning, and customer support.")
    why_choose_us = models.TextField(default="Professional guidance, fast communication, accurate documentation, and premium support.")
    office_address = models.TextField(
        default="HFWQ+3F5 Kaleem Overseas Consultants New, New Rasool Rd, Shadman Town, Mandi Bahauddin, Pakistan"
    )
    director_name = models.CharField(max_length=120, default="Kaleem Ahmed")
    director_title = models.CharField(max_length=120, default="Owner & Director")
    director_message = models.TextField(default="We focus on practical guidance, honest communication, and dependable service for every client.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def __str__(self):
        return self.company_name


class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Country(models.Model):
    CATEGORY_CHOICES = [
        ("visit", "Visit Visa"),
        ("business", "Business Visa"),
    ]

    name = models.CharField(max_length=120, unique=True)
    visa_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="visit")
    description = models.TextField()
    requirements = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_visa_category_display()})"


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    VISA_TYPE_CHOICES = [
        ("visit", "Visit Visa"),
        ("business", "Business Visa"),
        ("tour", "Tour Package"),
        ("consultation", "Travel Consultation"),
        ("other", "Other"),
    ]

    appointment_number = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    full_name = models.CharField(max_length=120, default="")
    phone_number = models.CharField(max_length=25, default="")
    email = models.EmailField(default="")
    city = models.CharField(max_length=120, default="")
    visa_type = models.CharField(max_length=120, choices=VISA_TYPE_CHOICES, default="visit")
    country = models.CharField(max_length=120, default="")
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    appointment_letter = models.FileField(upload_to="appointment_letters/", blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.appointment_number or f"Appointment: {self.full_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None

        if not self.appointment_number:
            self.appointment_number = generate_appointment_number()

        if not is_new:
            previous_status = Appointment.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        super().save(*args, **kwargs)

        should_generate_letter = self.status == self.STATUS_APPROVED and (
            is_new or previous_status != self.STATUS_APPROVED or not self.appointment_letter
        )

        if should_generate_letter:
            pdf_name, pdf_content = generate_appointment_letter_pdf(self)
            self.appointment_letter.save(pdf_name, pdf_content, save=False)
            if self.approved_at is None:
                self.approved_at = timezone.now()
            super().save(update_fields=["appointment_letter", "approved_at", "updated_at"])


class ContactMessage(models.Model):
    name = models.CharField(max_length=120, default="")
    phone = models.CharField(max_length=25, default="")
    email = models.EmailField(default="")
    subject = models.CharField(max_length=160, default="")
    message = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    review = models.TextField()
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    video = models.FileField(upload_to="testimonials/videos/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.country})"


class Gallery(models.Model):
    VISA_CHOICES = [
        ("visit", "Visit Visa"),
        ("family", "Family Visa"),
        ("business", "Business Visa"),
        ("tour", "Tour Package"),
    ]

    client_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    visa_type = models.CharField(max_length=20, choices=VISA_CHOICES)
    caption = models.TextField()
    image = models.ImageField(upload_to="gallery/")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "Gallery Success Story"
        verbose_name_plural = "Gallery Success Stories"

    def __str__(self):
        return f"{self.client_name} - {self.country}"


class TourPackage(models.Model):
    image = models.ImageField(upload_to="packages/")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tour Package"
        verbose_name_plural = "Tour Packages"

    def __str__(self):
        return f"Tour Package #{self.pk}"


class SuccessStory(models.Model):
    VISA_TYPE_CHOICES = [
        ("visit", "Visit Visa"),
        ("family", "Family Visa"),
        ("business", "Business Visa"),
        ("tour", "Tour Package"),
    ]

    client_name = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    visa_type = models.CharField(max_length=20, choices=VISA_TYPE_CHOICES)
    video = models.FileField(upload_to="success_stories/videos/")
    thumbnail = models.ImageField(upload_to="success_stories/thumbnails/", blank=True, null=True)
    description = models.TextField()
    upload_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-upload_date", "-pk"]
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return f"{self.client_name} - {self.country}"
