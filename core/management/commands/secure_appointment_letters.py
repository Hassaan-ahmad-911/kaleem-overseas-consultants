import re
import secrets

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from core.models import Appointment

LETTER_DIR = "appointment_letters"
SECURE_NAME = re.compile(r"-[0-9a-f]{16}\.pdf$")


class Command(BaseCommand):
    help = (
        "Give existing appointment letter PDFs unguessable file names and remove letter files that no "
        "appointment uses. Letters used to be saved as appointment_letters/<number>.pdf, which anyone could "
        "download from /media/ by guessing the number. Lists the changes only, unless --apply is given."
    )

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Rename and delete files instead of only listing them.")

    def handle(self, *args, **options):
        apply = options["apply"]
        referenced = set()
        renamed = 0

        for appointment in Appointment.objects.exclude(appointment_letter="").exclude(appointment_letter__isnull=True):
            old_name = appointment.appointment_letter.name
            if SECURE_NAME.search(old_name):
                referenced.add(old_name)
                continue
            if not default_storage.exists(old_name):
                self.stdout.write(self.style.WARNING(f"missing file, skipped: {old_name} ({appointment.appointment_number})"))
                continue

            new_name = f"{LETTER_DIR}/{appointment.appointment_number}-{secrets.token_hex(8)}.pdf"
            self.stdout.write(f"rename: {old_name} -> {new_name}")
            if apply:
                with default_storage.open(old_name, "rb") as handle:
                    saved_name = default_storage.save(new_name, ContentFile(handle.read()))
                # update() avoids Appointment.save(), which could regenerate the letter.
                Appointment.objects.filter(pk=appointment.pk).update(appointment_letter=saved_name)
                default_storage.delete(old_name)
                referenced.add(saved_name)
            else:
                referenced.add(old_name)
            renamed += 1

        orphans = []
        if default_storage.exists(LETTER_DIR):
            _, files = default_storage.listdir(LETTER_DIR)
            orphans = [f"{LETTER_DIR}/{name}" for name in files if f"{LETTER_DIR}/{name}" not in referenced]
        for name in orphans:
            self.stdout.write(f"delete unused letter: {name}")
            if apply:
                default_storage.delete(name)

        summary = f"{renamed} letter(s) to rename, {len(orphans)} unused letter file(s) to delete."
        if apply:
            self.stdout.write(self.style.SUCCESS("Done. " + summary))
        else:
            self.stdout.write(self.style.NOTICE("Dry run. " + summary + " Run again with --apply to make these changes."))
