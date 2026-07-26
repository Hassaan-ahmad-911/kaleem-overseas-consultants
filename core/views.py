from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AppointmentForm, AppointmentStatusLookupForm, ContactMessageForm
from .models import Appointment, CompanyInfo, ContactMessage, Country, Gallery, Service, SuccessStory, Testimonial, TourPackage


def home(request):
    countries = Country.objects.all()[:6]
    testimonials = Testimonial.objects.all()[:3]
    services = Service.objects.filter(is_active=True)[:8]
    gallery_items = Gallery.objects.filter(is_featured=True)[:6]
    if not gallery_items.exists():
        gallery_items = Gallery.objects.all()[:6]
    company_info = CompanyInfo.objects.order_by("-created_at").first()
    appointments_count = Appointment.objects.count()
    return render(
        request,
        "core/home.html",
        {
            "countries": countries,
            "testimonials": testimonials,
            "services": services,
            "gallery_items": gallery_items,
            "company_info": company_info,
            "appointments_count": appointments_count,
        },
    )


def about(request):
    company_info = CompanyInfo.objects.order_by("-created_at").first()
    return render(request, "core/about.html", {"company_info": company_info})


def services(request):
    services_list = Service.objects.filter(is_active=True)
    return render(request, "core/services.html", {"services_list": services_list})


def packages(request):
    tour_packages = TourPackage.objects.all()
    return render(request, "core/packages.html", {"tour_packages": tour_packages})


def package_detail(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    related_packages = TourPackage.objects.exclude(pk=pk)[:3]
    return render(
        request,
        "core/package_detail.html",
        {
            "package": package,
            "related_packages": related_packages,
        },
    )


def stories(request):
    success_stories = SuccessStory.objects.filter(is_active=True)
    return render(
        request,
        "core/stories.html",
        {
            "success_stories": success_stories,
        },
    )


def gallery(request):
    visa_type = request.GET.get("visa_type", "all")
    galleries = Gallery.objects.all()

    if visa_type in {choice[0] for choice in Gallery.VISA_CHOICES}:
        galleries = galleries.filter(visa_type=visa_type)

    featured_gallery = galleries.filter(is_featured=True)
    total_success_stories = Gallery.objects.count()
    featured_count = Gallery.objects.filter(is_featured=True).count()

    return render(
        request,
        "core/gallery.html",
        {
            "gallery_items": galleries,
            "featured_gallery": featured_gallery,
            "visa_choices": Gallery.VISA_CHOICES,
            "active_filter": visa_type,
            "total_success_stories": total_success_stories,
            "featured_count": featured_count,
        },
    )


def gallery_detail(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    related_items = Gallery.objects.exclude(pk=pk)[:4]
    return render(
        request,
        "core/gallery_detail.html",
        {
            "gallery_item": gallery_item,
            "related_items": related_items,
        },
    )


def countries_view(request):
    countries = Country.objects.all()
    return render(request, "core/countries.html", {"countries": countries})


def visit_visa(request):
    countries = Country.objects.filter(visa_category="visit")
    return render(request, "core/visit_visa.html", {"countries": countries})


def business_visa(request):
    countries = Country.objects.filter(visa_category="business")
    return render(request, "core/business_visa.html", {"countries": countries})


def visa_guidance(request):
    company_info = CompanyInfo.objects.order_by("-created_at").first()
    return render(request, "core/visa_guidance.html", {"company_info": company_info})


def contact(request):
    contact_form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and contact_form.is_valid():
        contact_form.save()
        messages.success(request, "Thanks for your message. Our team will contact you shortly.")
        return redirect("contact")
    company_info = CompanyInfo.objects.order_by("-created_at").first()
    return render(request, "core/contact.html", {"contact_form": contact_form, "company_info": company_info})


def book_appointment(request):
    appointment_form = AppointmentForm(request.POST or None)
    if request.method == "POST" and appointment_form.is_valid():
        appointment = appointment_form.save()
        messages.success(request, "Your appointment request has been submitted successfully and is awaiting approval.")
        return redirect(f"{reverse('appointment_status')}?appointment_number={appointment.appointment_number}")
    return render(request, "core/book_appointment.html", {"appointment_form": appointment_form})


def appointment_status(request):
    lookup_form = AppointmentStatusLookupForm(request.GET or None)
    appointment = None

    if lookup_form.is_valid():
        appointment_number = lookup_form.cleaned_data["appointment_number"]
        phone_number = lookup_form.cleaned_data["phone_number"]
        appointments = Appointment.objects.filter(appointment_number=appointment_number)
        if phone_number:
            appointments = appointments.filter(phone_number=phone_number)
        appointment = appointments.first()

        if not appointment:
            messages.error(request, "No appointment was found for the provided details.")

    return render(
        request,
        "core/appointment_status.html",
        {
            "lookup_form": lookup_form,
            "appointment": appointment,
        },
    )


def download_appointment_letter(request, appointment_number):
    appointment = get_object_or_404(Appointment, appointment_number=appointment_number)
    if appointment.status != Appointment.STATUS_APPROVED:
        raise Http404("Appointment letter is only available after approval.")

    if not appointment.appointment_letter:
        from .utils import generate_appointment_letter_pdf

        pdf_name, pdf_content = generate_appointment_letter_pdf(appointment)
        appointment.appointment_letter.save(pdf_name, pdf_content, save=False)
        appointment.save(update_fields=["appointment_letter", "updated_at"])

    file_handle = appointment.appointment_letter.open("rb")
    return FileResponse(file_handle, as_attachment=True, filename=appointment.appointment_letter.name.split("/")[-1])
