from django import forms

from .models import Appointment, ContactMessage


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["full_name", "phone_number", "email", "city", "visa_type", "country", "preferred_date", "preferred_time", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "visa_type": forms.Select(attrs={"class": "form-select"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
            "preferred_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Tell us what you need help with"}),
        }


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Your message"}),
        }


class AppointmentStatusLookupForm(forms.Form):
    appointment_number = forms.CharField(
        label="Appointment Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. KOC-20260001"}),
    )
    phone_number = forms.CharField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your phone number (optional)"}),
    )

    def clean_appointment_number(self):
        return self.cleaned_data["appointment_number"].strip().upper()

    def clean_phone_number(self):
        return self.cleaned_data["phone_number"].strip()
