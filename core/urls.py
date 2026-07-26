from django.urls import path

from .views import (
	about,
	business_visa,
	book_appointment,
	countries_view,
	contact,
	appointment_status,
	download_appointment_letter,
	gallery,
	gallery_detail,
	home,
	stories,
	packages,
	package_detail,
	services,
	visit_visa,
	visa_guidance,
)

urlpatterns = [
	path("", home, name="home"),
	path("about/", about, name="about"),
	path("services/", services, name="services"),
	path("packages/", packages, name="packages"),
	path("packages/<int:pk>/", package_detail, name="package_detail"),
	path("stories/", stories, name="stories"),
	path("gallery/", gallery, name="gallery"),
	path("gallery/<int:pk>/", gallery_detail, name="gallery_detail"),
	path("visit-visa/", visit_visa, name="visit_visa"),
	path("business-visa/", business_visa, name="business_visa"),
	path("visa-guidance/", visa_guidance, name="visa_guidance"),
	path("countries/", countries_view, name="countries"),
	path("contact/", contact, name="contact"),
	path("book-appointment/", book_appointment, name="book_appointment"),
	path("appointment-status/", appointment_status, name="appointment_status"),
	path("appointment-letter/<str:appointment_number>/", download_appointment_letter, name="download_appointment_letter"),
]
