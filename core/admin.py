from django.contrib import admin
from django.utils.html import format_html

from .models import Appointment, CompanyInfo, ContactMessage, Country, Gallery, Service, SuccessStory, Testimonial, TourPackage


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "visa_category")
    list_filter = ("visa_category",)
    search_fields = ("name", "description", "requirements")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("appointment_number", "full_name", "country", "visa_type", "status", "preferred_date", "preferred_time", "created_at")
    list_display_links = ("appointment_number", "full_name")
    list_filter = ("status", "visa_type", "preferred_date", "created_at")
    search_fields = ("appointment_number", "full_name", "phone_number", "email", "city", "country", "visa_type", "message")
    readonly_fields = ("appointment_number", "appointment_letter", "approved_at", "created_at", "updated_at", "appointment_letter_preview")
    list_editable = ("status",)

    def appointment_letter_preview(self, obj):
        if obj and obj.appointment_letter:
            return format_html('<a href="{}" target="_blank" rel="noopener">Download current letter</a>', obj.appointment_letter.url)
        return "No appointment letter generated yet."

    appointment_letter_preview.short_description = "Appointment Letter"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "email", "phone", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "phone", "email", "subject", "message")
    readonly_fields = ("created_at",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("display_order", "name")


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("company_name", "director_name", "office_address", "created_at")
    search_fields = ("company_name", "tagline", "about_text", "director_name", "office_address")
    readonly_fields = ("created_at",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "has_video")
    search_fields = ("name", "country", "review")
    readonly_fields = ("video_preview",)

    def has_video(self, obj):
        return bool(obj.video)

    has_video.short_description = "Video"
    has_video.boolean = True

    def video_preview(self, obj):
        if obj and obj.video:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">Open uploaded video</a>',
                obj.video.url,
            )
        return "No video uploaded yet."

    video_preview.short_description = "Video Preview"


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "client_name", "country", "visa_type", "is_featured", "created_at")
    list_display_links = ("thumbnail", "client_name")
    list_filter = ("visa_type", "is_featured", "created_at")
    search_fields = ("client_name", "country", "caption")
    ordering = ("-created_at",)
    readonly_fields = ("image_preview", "created_at")
    list_editable = ("is_featured",)
    date_hierarchy = "created_at"
    save_on_top = True

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:64px;height:48px;object-fit:cover;border-radius:10px;box-shadow:0 6px 16px rgba(7,28,60,0.16);" />',
                obj.image.url,
            )
        return "-"

    thumbnail.short_description = "Preview"

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width:100%;height:auto;border-radius:16px;box-shadow:0 16px 36px rgba(7,28,60,0.18);" />',
                obj.image.url,
            )
        return "No image selected yet."

    image_preview.short_description = "Image Preview"


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "description_snippet", "created_at")
    list_display_links = ("thumbnail", "description_snippet")
    readonly_fields = ("image_preview", "created_at")
    ordering = ("-created_at",)
    save_on_top = True

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:72px;height:54px;object-fit:cover;border-radius:10px;box-shadow:0 6px 16px rgba(7,28,60,0.16);" />',
                obj.image.url,
            )
        return "-"

    thumbnail.short_description = "Preview"

    def description_snippet(self, obj):
        text = (obj.description or "").strip()
        return text[:90] + ("..." if len(text) > 90 else "")

    description_snippet.short_description = "Description"

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width:100%;height:auto;border-radius:16px;box-shadow:0 16px 36px rgba(7,28,60,0.18);" />',
                obj.image.url,
            )
        return "No image selected yet."

    image_preview.short_description = "Image Preview"


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_preview", "client_name", "country", "visa_type", "upload_date", "is_active")
    list_display_links = ("thumbnail_preview", "client_name")
    list_filter = ("visa_type", "is_active", "upload_date", "country")
    search_fields = ("client_name", "country", "description")
    list_editable = ("is_active",)
    readonly_fields = ("video_preview", "thumbnail_detail")
    ordering = ("-upload_date", "-pk")
    save_on_top = True

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:48px;height:64px;object-fit:cover;border-radius:8px;" />',
                obj.thumbnail.url,
            )
        return "-"

    thumbnail_preview.short_description = "Thumb"

    def thumbnail_detail(self, obj):
        if obj and obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width:220px;height:auto;border-radius:12px;" />',
                obj.thumbnail.url,
            )
        return "No thumbnail uploaded."

    thumbnail_detail.short_description = "Thumbnail Preview"

    def video_preview(self, obj):
        if obj and obj.video:
            return format_html(
                '<video controls style="max-width:100%;border-radius:12px;" preload="metadata"><source src="{}"></video>',
                obj.video.url,
            )
        return "No video uploaded yet."

    video_preview.short_description = "Video Preview"
