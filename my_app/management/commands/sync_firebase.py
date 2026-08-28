from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from my_app.models import Question
from my_app.firebase_config import sync_firestore_to_sqlite, sync_all_sqlite_to_firestore


class Command(BaseCommand):
    help = "ซิงค์คำถามระหว่าง SQLite และ Firebase Firestore"

    def add_arguments(self, parser):
        parser.add_argument(
            "--push",
            action="store_true",
            help="ส่งข้อมูลจาก SQLite ขึ้น Firebase Firestore",
        )

    def handle(self, *args, **options):
        # ตรวจสอบและสร้าง Admin User พื้นฐานไว้เสมอ
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@csquiz.local", "admin1234")
            self.stdout.write(self.style.SUCCESS("[OK] Admin user ready: admin / admin1234"))

        if options.get("push"):
            self.stdout.write(self.style.NOTICE("Pushing questions from SQLite to Firebase Firestore..."))
            count = sync_all_sqlite_to_firestore()
            self.stdout.write(self.style.SUCCESS(f"[OK] Pushed {count} questions to Firestore."))
        else:
            self.stdout.write(self.style.NOTICE("Pulling questions from Firebase Firestore to SQLite..."))
            count = sync_firestore_to_sqlite()
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"[OK] Successfully synced {count} questions from Firestore!"))
            else:
                self.stdout.write(self.style.WARNING("[NOTICE] No questions found in Firestore or connection failed."))
