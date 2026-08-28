from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from my_app.models import Category, Question, QuizLog
from my_app.firebase_config import sync_question_to_firestore, delete_question_from_firestore, fetch_all_questions_from_firestore


class Command(BaseCommand):
    help = "สร้างชุดคำถามระดับ ป.3 - ม.3 คำตอบสั้นกระชับทุกข้อ 100 ข้อ ซิงค์เข้า Firebase Firestore และ SQLite"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("=== เริ่มกระบวนการสร้างชุดคำถามระดับ ป.3 - ม.3 (ตัวเลือกสั้นกระชับทุกข้อ 100 ข้อ) ==="))

        # 1. เคลียร์คำถามเดิมทั้งหมดบน Firebase Firestore
        try:
            self.stdout.write(self.style.NOTICE("1. เคลียร์คำถามเดิมบน Firebase Firestore..."))
            old_docs = fetch_all_questions_from_firestore()
            deleted_count = 0
            if old_docs:
                from concurrent.futures import ThreadPoolExecutor
                def _del_doc(doc):
                    d_id = doc.get("name", "").split("/")[-1]
                    return delete_question_from_firestore(d_id) if d_id else False

                with ThreadPoolExecutor(max_workers=15) as executor:
                    results = list(executor.map(_del_doc, old_docs))
                    deleted_count = sum(1 for r in results if r)
            self.stdout.write(self.style.SUCCESS(f"[OK] ล้างคำถามเดิมใน Firebase เรียบร้อย ({deleted_count} ข้อ)"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[Firebase Notice] {e}"))

        # 2. ล้างข้อมูลเดิมใน Local Database (SQLite)
        QuizLog.objects.all().delete()
        Question.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("[OK] ล้างข้อมูลใน Local Database (SQLite) เรียบร้อย"))

        # 3. ตรวจสอบ/สร้าง Superuser Admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@csquiz.local", "admin1234")
            self.stdout.write(self.style.SUCCESS("[OK] Superuser: admin / admin1234"))

        # 4. สร้างหมวดหมู่
        cat_basic = Category.objects.create(
            name="คอมพิวเตอร์เบื้องต้น",
            color="#0ea5e9"
        )
        cat_cs = Category.objects.create(
            name="สาขาวิทยาการคอมพิวเตอร์เบื้องต้น",
            color="#8b5cf6"
        )
        self.stdout.write(self.style.SUCCESS("[OK] สร้าง 2 หมวดหมู่เรียบร้อย:"))
        self.stdout.write(f"  - หมวด 1: {cat_basic.name} (90 ข้อ: ง่าย 40, ปานกลาง 25, ยาก 25)")
        self.stdout.write(f"  - หมวด 2: {cat_cs.name} (10 ข้อ)")

        # 5. ชุดคำถาม 100 ข้อ ระดับ ป.3 - ม.3 (ตัวเลือกสั้นกระชับทุกข้อ)
        raw_questions = [
            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับง่าย (ป.3 - ป.6) 40 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดทำหน้าที่เหมือน 'หนู' ใช้เลื่อนลูกศรและคลิกบนหน้าจอ?",
                "choice_a": "เมาส์ (Mouse)", "choice_b": "คีย์บอร์ด", "choice_c": "ลำโพง", "choice_d": "พัดลม",
                "correct_choice": "A", "explanation": "เมาส์ (Mouse) ใช้เลื่อนเคอร์เซอร์และคลิกเลือกเมนูบนจอภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพิมพ์ข้อความหรือตัวหนังสือเข้าคอมพิวเตอร์ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "คีย์บอร์ด (Keyboard)", "choice_b": "สแกนเนอร์", "choice_c": "จอภาพ", "choice_d": "ไมโครโฟน",
                "correct_choice": "A", "explanation": "คีย์บอร์ดใช้พิมพ์ตัวอักษรและตัวเลขเข้าสู่คอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัดสากล 'Ctrl + C' มีไว้ใช้ทำอะไร?",
                "choice_a": "คัดลอก (Copy)", "choice_b": "ตัด (Cut)", "choice_c": "วาง (Paste)", "choice_d": "ลบ (Delete)",
                "correct_choice": "A", "explanation": "Ctrl + C คือปุ่มลัด Copy สำหรับคัดลอกข้อความหรือไฟล์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + V' ใช้งานคู่กับ Ctrl + C เพื่อทำอะไร?",
                "choice_a": "วางข้อมูล (Paste)", "choice_b": "ย้อนกลับ (Undo)", "choice_c": "เลือกทั้งหมด (All)", "choice_d": "สั่งพิมพ์ (Print)",
                "correct_choice": "A", "explanation": "Ctrl + V ใช้สำหรับวาง (Paste) สิ่งที่คัดลอกไว้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากพิมพ์ข้อความผิดพลาด สามารถกดย้อนกลับ (Undo) ด้วยปุ่มใด?",
                "choice_a": "Ctrl + Z", "choice_b": "Ctrl + S", "choice_c": "Ctrl + O", "choice_d": "Ctrl + N",
                "correct_choice": "A", "explanation": "Ctrl + Z คือคำสั่ง Undo เพื่อย้อนกลับการกระทำล่าสุด"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + S' นิยมกดเป็นประจำเพื่อทำอะไร?",
                "choice_a": "บันทึกงาน (Save)", "choice_b": "ปิดคอมพิวเตอร์", "choice_c": "เปิดเพลง", "choice_d": "เพิ่มเสียง",
                "correct_choice": "A", "explanation": "Ctrl + S ใช้บันทึกงาน (Save) เพื่อป้องกันงานสูญหาย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มที่ยาวที่สุดบนแป้นพิมพ์แถวล่างสุด เรียกว่าอะไร?",
                "choice_a": "Spacebar", "choice_b": "Enter", "choice_c": "Shift", "choice_d": "Caps Lock",
                "correct_choice": "A", "explanation": "Spacebar ใช้สำหรับเคาะเว้นวรรคช่องว่างระหว่างตัวอักษร"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มใดใช้สำหรับ 'ขึ้นบรรทัดใหม่' หรือ 'ตกลง/ยืนยัน' คำสั่ง?",
                "choice_a": "Enter", "choice_b": "Esc", "choice_c": "Tab", "choice_d": "Alt",
                "correct_choice": "A", "explanation": "ปุ่ม Enter ใช้ยืนยันคำสั่ง หรือขึ้นบรรทัดใหม่ในการพิมพ์งาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มใดที่เมื่อกดค้างไว้ จะช่วยให้พิมพ์ตัวพิมพ์ใหญ่ภาษาอังกฤษได้?",
                "choice_a": "Shift", "choice_b": "Ctrl", "choice_c": "Alt", "choice_d": "Tab",
                "correct_choice": "A", "explanation": "กด Shift ค้างไว้แล้วกดตัวอักษรจะได้ตัวพิมพ์ใหญ่"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่ม 'Caps Lock' มีหน้าที่อะไรในการพิมพ์งาน?",
                "choice_a": "ล็อกพิมพ์ตัวใหญ่ตลอด", "choice_b": "ล็อกหน้าจอคอม", "choice_c": "ล็อกไม่ให้ลบไฟล์", "choice_d": "ปิดเสียงลำโพง",
                "correct_choice": "A", "explanation": "Caps Lock ช่วยให้พิมพ์ตัวพิมพ์ใหญ่ต่อเนื่องโดยไม่ต้องกด Shift ค้าง"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ชิ้นใดเปรียบเหมือน 'สมอง' ของคอมพิวเตอร์?",
                "choice_a": "ซีพียู (CPU)", "choice_b": "เมาส์ (Mouse)", "choice_c": "คีย์บอร์ด (Keyboard)", "choice_d": "จอภาพ (Monitor)",
                "correct_choice": "A", "explanation": "CPU ทำหน้าที่ประมวลผลกลางเปรียบเหมือนสมองของคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพิมพ์รูปวาดหรือการบ้านออกมาบนกระดาษ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "เครื่องพิมพ์ (Printer)", "choice_b": "สแกนเนอร์", "choice_c": "จอภาพ", "choice_d": "ลำโพง",
                "correct_choice": "A", "explanation": "Printer (เครื่องพิมพ์) ใช้พิมพ์เอกสารและรูปลงบนกระดาษ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพูดคุยเสียงกับคุณครูหรือเพื่อนออนไลน์ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "ไมโครโฟน", "choice_b": "ลำโพง", "choice_c": "หูฟัง", "choice_d": "เมาส์",
                "correct_choice": "A", "explanation": "ไมโครโฟนทำหน้าที่รับเสียงพูดของเราส่งเข้าคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์พกพาขนาดเล็กที่ใช้เสียบช่อง USB เก็บการบ้านคืออะไร?",
                "choice_a": "แฟลชไดรฟ์ (Flash Drive)", "choice_b": "พัดลมเคส", "choice_c": "สายไฟคอม", "choice_d": "แรม (RAM)",
                "correct_choice": "A", "explanation": "Flash Drive เป็นอุปกรณ์เก็บข้อมูลสำรองแบบพกพาสะดวก"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "Google Chrome และ Microsoft Edge จัดเป็นโปรแกรมประเภทใด?",
                "choice_a": "เว็บบราวเซอร์ (Web Browser)", "choice_b": "โปรแกรมวาดภาพ", "choice_c": "เครื่องคิดเลข", "choice_d": "โปรแกรมพิมพ์งาน",
                "correct_choice": "A", "explanation": "Web Browser ใช้สำหรับเปิดดูเว็บไซต์และเล่นอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรมใดบน Windows ที่เด็ก ๆ นิยมใช้ฝึกวาดภาพและระบายสี?",
                "choice_a": "Paint", "choice_b": "Excel", "choice_c": "Word", "choice_d": "Calculator",
                "correct_choice": "A", "explanation": "Paint เป็นโปรแกรมวาดภาพและระบายสีรูปทรงพื้นฐาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรม Microsoft Word เหมาะสำหรับใช้งานประเภทใด?",
                "choice_a": "พิมพ์เอกสารและรายงาน", "choice_b": "ตัดต่อภาพยนตร์", "choice_c": "ฟังวิทยุ", "choice_d": "สแกนหาฝุ่น",
                "correct_choice": "A", "explanation": "Microsoft Word ใช้สำหรับพิมพ์งานเอกสารและทำรายงาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรม Microsoft PowerPoint นิยมใช้ทำอะไรมากที่สุด?",
                "choice_a": "ทำสไลด์นำเสนองาน", "choice_b": "เล่นเกมต่อสู้", "choice_c": "สร้างตารางสูตรคูณ", "choice_d": "ดูคลิปการ์ตูน",
                "correct_choice": "A", "explanation": "PowerPoint ออกแบบมาสำหรับสร้างสไลด์นำเสนอข้อความและรูปภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไอคอนรูปถังขยะ 'Recycle Bin' บนหน้าจอ มีไว้เพื่ออะไร?",
                "choice_a": "เก็บไฟล์ที่เพิ่งลบชั่วคราว", "choice_b": "เก็บเพลงใหม่ล่าสุด", "choice_c": "ทำลายคอมพิวเตอร์", "choice_d": "เก็บรูปภาพโปรด",
                "correct_choice": "A", "explanation": "Recycle Bin เก็บไฟล์ที่เพิ่งลบ สามารถกู้คืน (Restore) กลับมาได้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่ม 'Backspace' บนแป้นพิมพ์ มีไว้ใช้ทำอะไรเวลาพิมพ์งาน?",
                "choice_a": "ลบตัวอักษรทางซ้าย", "choice_b": "เพิ่มเสียงลำโพง", "choice_c": "เปิดหน้าต่างใหม่", "choice_d": "ปิดเครื่องทันที",
                "correct_choice": "A", "explanation": "Backspace ใช้ลบตัวอักษรที่อยู่ข้างหน้า (ซ้าย) ของเคอร์เซอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่ม 'Esc' (Escape) มุมบนซ้ายของคีย์บอร์ด มักใช้เพื่อทำอะไร?",
                "choice_a": "ยกเลิก / ออกจากเต็มจอ", "choice_b": "บันทึกงาน", "choice_c": "พิมพ์ตัวใหญ่", "choice_d": "เปิดเครื่องคอม",
                "correct_choice": "A", "explanation": "ปุ่ม Esc ใช้กดยกเลิก หรือออกจากโหมดเต็มหน้าจอ / ออกจากเกม"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มฟังก์ชันใดบนแป้นพิมพ์ที่ใช้กดเพื่อ 'รีเฟรช' (Refresh) หน้าเว็บ?",
                "choice_a": "F5", "choice_b": "F1", "choice_c": "F12", "choice_d": "F4",
                "correct_choice": "A", "explanation": "F5 เป็นปุ่มลัดมาตรฐานสำหรับโหลดหน้าเว็บใหม่ (Refresh)"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "การคลิกปุ่มซ้ายของเมาส์ 2 ครั้งติดกันอย่างรวดเร็ว เรียกว่าอะไร?",
                "choice_a": "ดับเบิลคลิก (Double Click)", "choice_b": "คลิกขวา", "choice_c": "สกอร์เมาส์", "choice_d": "แดร็กเมาส์",
                "correct_choice": "A", "explanation": "Double Click คือการคลิก 2 ครั้งติดกันเพื่อเปิดโปรแกรมหรือเปิดไฟล์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดใช้กระจายสัญญาณอินเทอร์เน็ตไร้สาย (Wi-Fi) ในบ้าน?",
                "choice_a": "เราเตอร์ (Router)", "choice_b": "เครื่องคิดเลข", "choice_c": "แฟลชไดรฟ์", "choice_d": "พาวเวอร์แบงก์",
                "correct_choice": "A", "explanation": "Wi-Fi Router ทำหน้าที่กระจายสัญญาณอินเทอร์เน็ตไร้สาย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "รหัสผ่าน (Password) ที่ปลอดภัย ควรตั้งแบบใด?",
                "choice_a": "ผสมตัวหนังสือและตัวเลข", "choice_b": "ใช้ตัวเลข 123456", "choice_c": "ใช้วันเกิดตัวเอง", "choice_d": "บอกเพื่อนทุกคน",
                "correct_choice": "A", "explanation": "รหัสผ่านที่ดีควรเดายากและผสมตัวอักษรกับตัวเลข"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ข้อมูลใดที่ไม่ควรบอกคนแปลกหน้าบนอินเทอร์เน็ตอย่างเด็ดขาด?",
                "choice_a": "รหัสผ่านและที่อยู่บ้าน", "choice_b": "การ์ตูนที่ชอบดู", "choice_c": "สีที่ชอบ", "choice_d": "วิชาที่ชอบเรียน",
                "correct_choice": "A", "explanation": "รหัสผ่านและข้อมูลส่วนตัวเป็นความลับ ห้ามบอกคนอื่นเพื่อความปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์รูปภาพทั่วไป มักมีนามสกุลไฟล์ลงท้ายด้วยอะไร?",
                "choice_a": ".jpg หรือ .png", "choice_b": ".mp3", "choice_c": ".mp4", "choice_d": ".exe",
                "correct_choice": "A", "explanation": ".jpg และ .png คือนามสกุลไฟล์รูปภาพยอดนิยม"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์เพลงที่เปิดฟังในคอมพิวเตอร์ มักเป็นไฟล์นามสกุลใด?",
                "choice_a": ".mp3", "choice_b": ".jpg", "choice_c": ".pdf", "choice_d": ".docx",
                "correct_choice": "A", "explanation": ".mp3 เป็นรูปแบบไฟล์เสียงและเพลงมาตรฐาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์เอกสารใบงานที่เปิดอ่านแล้วตัวหนังสือไม่เลื่อนเพี้ยน คือไฟล์ใด?",
                "choice_a": ".pdf", "choice_b": ".mp3", "choice_c": ".avi", "choice_d": ".exe",
                "correct_choice": "A", "explanation": ".pdf เป็นไฟล์เอกสารที่คงรูปแบบหน้ากระดาษเดิมทุกอุปกรณ์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หูฟังไร้สายเชื่อมต่อกับคอมพิวเตอร์ด้วยสัญญาณใด?",
                "choice_a": "บลูทูธ (Bluetooth)", "choice_b": "สัญญาณ GPS", "choice_c": "คลื่นไมโครเวฟ", "choice_d": "สายไฟบ้าน",
                "correct_choice": "A", "explanation": "Bluetooth เป็นคลื่นสัญญาณไร้สายระยะใกล้สำหรับหูฟังและเมาส์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + A' มีประโยชน์อย่างไร?",
                "choice_a": "เลือกทั้งหมด (Select All)", "choice_b": "ลบไฟล์ทั้งหมด", "choice_c": "ปิดหน้าต่าง", "choice_d": "บันทึกงานทันที",
                "correct_choice": "A", "explanation": "Ctrl + A ใช้เลือกคลุมข้อความหรือไฟล์ทั้งหมดในครั้งเดียว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Alt + Tab' บนคอมพิวเตอร์ ใช้สำหรับทำอะไร?",
                "choice_a": "สลับหน้าต่างโปรแกรม", "choice_b": "ปิดคอมพิวเตอร์", "choice_c": "แคปหน้าจอ", "choice_d": "เพิ่มเสียงลำโพง",
                "correct_choice": "A", "explanation": "Alt + Tab ใช้สลับเปลี่ยนหน้าต่างโปรแกรมที่เปิดอยู่ได้อย่างรวดเร็ว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "เว็บไซต์ 'Google' ทำหน้าที่หลักเป็นอะไร?",
                "choice_a": "ค้นหาข้อมูล (Search Engine)", "choice_b": "โปรแกรมวาดภาพ", "choice_c": "เครื่องคิดเลข", "choice_d": "เกมออนไลน์",
                "correct_choice": "A", "explanation": "Google เป็น Search Engine ใช้ค้นหาข้อมูล รูปภาพ และวิดีโอบนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "การดึงรูปหรือเกมจากอินเทอร์เน็ตมาเก็บไว้ในเครื่อง เรียกว่าอะไร?",
                "choice_a": "ดาวน์โหลด (Download)", "choice_b": "อัปโหลด (Upload)", "choice_c": "รีสตาร์ท", "choice_d": "ดีลีต",
                "correct_choice": "A", "explanation": "Download คือการดึงไฟล์จากเน็ตมาบันทึกในเครื่องของเรา"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "การส่งรูปหรือการบ้านขึ้นไปบนเว็บไซต์ เรียกว่าอะไร?",
                "choice_a": "อัปโหลด (Upload)", "choice_b": "ดาวน์โหลด (Download)", "choice_c": "สแกน", "choice_d": "ปรินต์",
                "correct_choice": "A", "explanation": "Upload คือการส่งไฟล์จากเครื่องเราขึ้นไปบนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "คำว่า 'WWW' หน้าชื่อเว็บไซต์ ย่อมาจากอะไร?",
                "choice_a": "World Wide Web", "choice_b": "World Wide Windows", "choice_c": "Web World Wide", "choice_d": "Wifi World Web",
                "correct_choice": "A", "explanation": "World Wide Web คือเครือข่ายใยแมงมุมที่เชื่อมต่อเว็บไซต์ทั่วโลก"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดทำหน้าที่แสดงภาพและตัวหนังสือให้เรามองเห็น?",
                "choice_a": "จอภาพ (Monitor)", "choice_b": "ฮาร์ดดิสก์", "choice_c": "คีย์บอร์ด", "choice_d": "เคสคอมพิวเตอร์",
                "correct_choice": "A", "explanation": "Monitor (จอภาพ) ทำหน้าที่แสดงผลลัพธ์รูปภาพและวิดีโอ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ข้อใดเป็นท่านั่งใช้งานคอมพิวเตอร์ที่ถูกต้องที่สุด?",
                "choice_a": "นั่งหลังตรงพักสายตา", "choice_b": "นอนคว่ำเล่นในที่มืด", "choice_c": "วางแก้วน้ำบนเคสคอม", "choice_d": "จ้องจอนาน 10 ชม.ติด",
                "correct_choice": "A", "explanation": "การนั่งหลังตรงและพักสายตาทุก 20-30 นาทีช่วยถนอมสายตาและสุขภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากหน้าจอคอมพิวเตอร์มีฝุ่นเกาะ ควรทำความสะอาดอย่างไร?",
                "choice_a": "ใช้ผ้านุ่มไมโครไฟเบอร์", "choice_b": "เอาน้ำสาดใส่หน้าจอ", "choice_c": "ใช้แปรงลวดขัด", "choice_d": "เอาน้ำยาล้างจานราด",
                "correct_choice": "A", "explanation": "ควรใช้ผ้าไมโครไฟเบอร์แห้งนุ่มเช็ดหน้าจอเบา ๆ หลังปิดจอแล้ว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "กล่องสี่เหลี่ยมที่รวมชิ้นส่วนข้างในของคอมพิวเตอร์ไว้ เรียกว่าอะไร?",
                "choice_a": "เคส (Computer Case)", "choice_b": "เมาส์", "choice_c": "แผ่นรองเมาส์", "choice_d": "แฟลชไดรฟ์",
                "correct_choice": "A", "explanation": "เคส (Case) คือตัวถังที่บรรจุอุปกรณ์ภายในคอมพิวเตอร์ทั้งหมด"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับปานกลาง (ป.5 - ม.2) 25 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยความจำ 'RAM' ทำหน้าที่เปรียบเสมือนอะไร?",
                "choice_a": "โต๊ะทำงานชั่วคราว", "choice_b": "ตู้เก็บของถาวร", "choice_c": "หลอดไฟส่องสว่าง", "choice_d": "ลำโพงส่งเสียง",
                "correct_choice": "A", "explanation": "RAM เปรียบเหมือนโต๊ะทำงานชั่วคราว ยิ่งโต๊ะใหญ่ยิ่งเปิดหลายโปรแกรมได้ลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยความจำ 'SSD' มีจุดเด่นเหนือกว่าฮาร์ดดิสก์จานหมุนแบบเดิมอย่างไร?",
                "choice_a": "อ่านเขียนเร็วกว่ามาก", "choice_b": "ราคาถูกกว่ามาก", "choice_c": "รับสัญญาณวิทยุได้", "choice_d": "มีความจุไม่จำกัด",
                "correct_choice": "A", "explanation": "SSD บันทึกข้อมูลลงชิปอิเล็กทรอนิกส์ จึงเปิดเครื่องและโหลดเกมเร็วกว่าฮาร์ดดิสก์มาก"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ในระบบคอมพิวเตอร์ 1 ไบต์ (Byte) มีค่าเท่ากับกี่บิต (Bit)?",
                "choice_a": "8 บิต", "choice_b": "4 บิต", "choice_c": "16 บิต", "choice_d": "100 บิต",
                "correct_choice": "A", "explanation": "1 Byte เท่ากับ 8 Bits ซึ่งพอดีสำหรับเก็บตัวอักษร 1 ตัว"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยวัดความจุข้อใดมีขนาดใหญ่ที่สุด?",
                "choice_a": "1 Terabyte (TB)", "choice_b": "1 Gigabyte (GB)", "choice_c": "1 Megabyte (MB)", "choice_d": "1 Kilobyte (KB)",
                "correct_choice": "A", "explanation": "เรียงจากเล็กไปใหญ่: KB -> MB -> GB -> TB (1 TB เท่ากับประมาณ 1,024 GB)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ความจุ 1 Gigabyte (GB) มีค่าเท่ากับกี่ Megabyte (MB)?",
                "choice_a": "1,024 MB", "choice_b": "100 MB", "choice_c": "10 MB", "choice_d": "1,000,000 MB",
                "correct_choice": "A", "explanation": "ในระบบเลขฐานสอง 1 GB มีค่าเท่ากับ 1,024 MB"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "การ์ดจอ หรือ 'GPU' มีหน้าที่หลักเน้นไปที่งานประเภทใด?",
                "choice_a": "ประมวลผลภาพและเกม 3D", "choice_b": "จ่ายไฟเข้าเมนบอร์ด", "choice_c": "เก็บไฟล์เสียง", "choice_d": "ป้องกันฝุ่นเข้าเคส",
                "correct_choice": "A", "explanation": "GPU ทำหน้าที่ประมวลผลกราฟิก วิดีโอ และเกม 3 มิติให้สวยงามลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "สายเคเบิล 'HDMI' ส่งสัญญาณอะไรไปยังจอภาพ?",
                "choice_a": "ส่งทั้งภาพและเสียง", "choice_b": "ส่งเฉพาะกระแสไฟ", "choice_c": "ส่งเฉพาะเสียงเพลง", "choice_d": "ส่งคลื่นวิทยุ",
                "correct_choice": "A", "explanation": "HDMI ส่งสัญญาณภาพความละเอียดสูงและเสียงพร้อมกันในสายเส้นเดียว"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ไวรัสคอมพิวเตอร์ (Computer Virus) คืออะไร?",
                "choice_a": "โปรแกรมทำลายข้อมูล", "choice_b": "เชื้อโรคที่ทำให้คนป่วย", "choice_c": "ฝุ่นในพัดลมซีพียู", "choice_d": "สายไฟที่ขาดในเครื่อง",
                "correct_choice": "A", "explanation": "ไวรัสคอมพิวเตอร์คือซอฟต์แวร์ไม่พึงประสงค์ที่มุ่งทำลายหรือขโมยข้อมูล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โปรแกรมแอนติไวรัส (Antivirus) มีหน้าที่หลักคืออะไร?",
                "choice_a": "ตรวจจับและกำจัดไวรัส", "choice_b": "ช่วยให้เล่นเกมชนะ", "choice_c": "เพิ่มความเร็วพิมพ์งาน", "choice_d": "ปรับหน้าจอให้สว่าง",
                "correct_choice": "A", "explanation": "Antivirus ช่วยตรวจจับ ป้องกัน และกำจัดภัยคุกคามในคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "Google Drive และ iCloud จัดเป็นบริการประเภทใด?",
                "choice_a": "คลาวด์สตอเรจ (Cloud Storage)", "choice_b": "เกมออนไลน์", "choice_c": "โปรแกรมตัดต่อเพลง", "choice_d": "การ์ดจอเสริม",
                "correct_choice": "A", "explanation": "Cloud Storage ให้บริการเก็บไฟล์ออนไลน์ สามารถเปิดอ่านได้ทุกที่"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ภัยคุกคามแบบ 'Phishing' (ฟิชชิ่ง) มีลักษณะการหลอกลวงอย่างไร?",
                "choice_a": "ส่งลิงก์ปลอมหลอกเอาข้อมูล", "choice_b": "ปาหินใส่หน้าจอคอม", "choice_c": "พิมพ์แป้นพิมพ์เร็วไป", "choice_d": "เปิดเพลงเสียงดังไป",
                "correct_choice": "A", "explanation": "Phishing คือการทำหน้าเว็บหรืออีเมลปลอมเพื่อหลอกให้เหยื่อกรอกรหัสผ่าน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบยืนยันตัวตน 2 ชั้น (2FA) ช่วยเพิ่มความปลอดภัยอย่างไร?",
                "choice_a": "ใส่รหัสผ่านคู่กับ OTP", "choice_b": "ล็อกอินพร้อมกัน 2 คน", "choice_c": "พิมพ์รหัสเดิม 2 รอบ", "choice_d": "เปิดคอม 2 เครื่องพร้อมกัน",
                "correct_choice": "A", "explanation": "2FA เพิ่มความปลอดภัยโดยต้องใช้รหัส OTP จากมือถือร่วมกับรหัสผ่าน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ไฟล์บีบอัดนามสกุล '.zip' มีประโยชน์อย่างไร?",
                "choice_a": "รวมไฟล์และย่อขนาดลง", "choice_b": "แปลงรูปภาพเป็นเพลง", "choice_c": "เพิ่มความเร็วพัดลม", "choice_d": "ทำให้ภาพคมชัด 10 เท่า",
                "correct_choice": "A", "explanation": "ไฟล์ Zip ช่วยรวมหลาย ๆ ไฟล์เข้าด้วยกันและลดขนาดไฟล์ให้ส่งต่อง่าย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ที่อยู่เว็บไซต์ เช่น 'https://www.google.com' มีชื่อเรียกว่าอะไร?",
                "choice_a": "URL", "choice_b": "CPU", "choice_c": "RAM", "choice_d": "PDF",
                "correct_choice": "A", "explanation": "URL (Uniform Resource Locator) คือที่อยู่ระบุตำแหน่งเว็บไซต์บนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบปฏิบัติการยอดนิยมสำหรับเครื่องคอมพิวเตอร์ PC คือข้อใด?",
                "choice_a": "Microsoft Windows", "choice_b": "Photoshop", "choice_c": "Google Chrome", "choice_d": "Roblox",
                "correct_choice": "A", "explanation": "Windows เป็นระบบปฏิบัติการยอดนิยมสำหรับเครื่องคอมพิวเตอร์ทั่วไป"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบปฏิบัติการหลักบนสมาร์ตโฟนในปัจจุบันคือข้อใด?",
                "choice_a": "Android และ iOS", "choice_b": "Windows 95 และ DOS", "choice_c": "Word และ Excel", "choice_d": "Paint และ Notepad",
                "correct_choice": "A", "explanation": "สมาร์ตโฟนส่วนใหญ่ใช้ระบบปฏิบัติการ Android หรือ iOS (iPhone)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "สัญลักษณ์แม่กุญแจและ 'https://' บนเว็บเบราว์เซอร์ หมายถึงอะไร?",
                "choice_a": "เว็บมีการเข้ารหัสปลอดภัย", "choice_b": "เว็บนี้ต้องเสียเงินเข้าชม", "choice_c": "เว็บสำหรับเล่นเกมเท่านั้น", "choice_d": "เว็บกำลังถูกไวรัสโจมตี",
                "correct_choice": "A", "explanation": "HTTPS มีการเข้ารหัสความปลอดภัย ป้องกันข้อมูลถูกแอบดักจับ"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "แผงวงจรหลักที่เชื่อมต่ออุปกรณ์ทุกชิ้นในคอมพิวเตอร์เข้าด้วยกันคืออะไร?",
                "choice_a": "เมนบอร์ด (Motherboard)", "choice_b": "การ์ดเสียง", "choice_c": "สายไฟบ้าน", "choice_d": "เว็บแคม",
                "correct_choice": "A", "explanation": "Motherboard คือแผงวงจรพิมพ์หลักที่เป็นศูนย์กลางเชื่อมต่ออุปกรณ์ทุกชิ้น"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "พาวเวอร์ซัพพลาย (Power Supply Unit : PSU) มีหน้าที่อะไร?",
                "choice_a": "แปลงและจ่ายไฟให้เครื่อง", "choice_b": "เปิดเสียงเพลงเมื่อเปิดเครื่อง", "choice_c": "ทำความสะอาดหน้าจอ", "choice_d": "บันทึกรูปภาพ",
                "correct_choice": "A", "explanation": "PSU ทำหน้าที่แปลงไฟฟ้าบ้านและจ่ายพลังงานไฟฟ้าไปเลี้ยงทุกชิ้นส่วนในคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "เครือข่าย 'LAN' หมายถึงการเชื่อมต่อแบบใด?",
                "choice_a": "เครือข่ายระยะใกล้ในห้อง", "choice_b": "เครือข่ายดาวเทียมรอบโลก", "choice_c": "เครือข่ายใต้มหาสมุทร", "choice_d": "เครือข่ายสถานีอวกาศ",
                "correct_choice": "A", "explanation": "LAN (Local Area Network) คือเครือข่ายท้องถิ่นระยะใกล้ เช่น ในห้องคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "สัญลักษณ์ใดที่ต้องมีคั่นในที่อยู่อีเมลเสมอ เช่น student...gmail.com?",
                "choice_a": "@ (เครื่องหมายแอท)", "choice_b": "# (แฮชแท็ก)", "choice_c": "$ (ดอลลาร์)", "choice_d": "& (แอนด์)",
                "correct_choice": "A", "explanation": "สัญลักษณ์ @ ใช้คั่นระหว่างชื่อผู้ใช้กับชื่อโดเมนอีเมล เช่น user@gmail.com"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "กล้องเว็บแคม (Webcam) จัดเป็นอุปกรณ์ประเภทใด?",
                "choice_a": "อุปกรณ์รับข้อมูล (Input)", "choice_b": "อุปกรณ์แสดงผล (Output)", "choice_c": "อุปกรณ์ประมวลผล", "choice_d": "อุปกรณ์จ่ายไฟ",
                "correct_choice": "A", "explanation": "Webcam รับภาพจากภายนอกเข้าสู่ระบบคอมพิวเตอร์ จึงเป็นอุปกรณ์ Input"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โปรแกรมแบบ 'Open Source' มีความหมายว่าอย่างไร?",
                "choice_a": "เปิดเผยโค้ดให้พัฒนาฟรี", "choice_b": "ต้องเปิดฝาเครื่องเวลาใช้", "choice_c": "โปรแกรมราคาแพงที่สุด", "choice_d": "ห้ามคนอื่นดูโค้ด",
                "correct_choice": "A", "explanation": "Open Source คือซอฟต์แวร์ที่เปิดเผยซอร์สโค้ดให้ทุกคนนำไปพัฒนาต่อยอดได้ฟรี"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยวัดความเร็วเน็ต 'Mbps' คำว่า 'M' ย่อมาจากอะไร?",
                "choice_a": "Mega (ล้าน)", "choice_b": "Minute", "choice_c": "Mouse", "choice_d": "Music",
                "correct_choice": "A", "explanation": "Mbps ย่อมาจาก Megabits per second (ล้านบิตต่อวินาที)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ปุ่ม 'Ctrl + Shift + Esc' ใน Windows ใช้เปิดโปรแกรมใดเพื่อดูว่าโปรแกรมไหนค้าง?",
                "choice_a": "Task Manager", "choice_b": "Paint", "choice_c": "Recycle Bin", "choice_d": "Calculator",
                "correct_choice": "A", "explanation": "Task Manager ใช้ตรวจสอบโปรแกรมที่ทำงานอยู่และสามารถสั่งปิดโปรแกรมที่ค้างได้"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับยาก (ม.1 - ม.3) 25 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หมายเลข 'IP Address' ในเครือข่ายอินเทอร์เน็ตทำหน้าที่เปรียบเหมือนสิ่งใด?",
                "choice_a": "บ้านเลขที่ระบุตำแหน่งเครื่อง", "choice_b": "รหัสผ่านเกม", "choice_c": "ยี่ห้อจอภาพ", "choice_d": "ความสว่างหน้าจอ",
                "correct_choice": "A", "explanation": "IP Address ทำหน้าที่เป็นหมายเลขระบุตัวตนและตำแหน่งของอุปกรณ์ในเครือข่าย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'DNS' (Domain Name System) ในอินเทอร์เน็ตมีหน้าที่อะไร?",
                "choice_a": "แปลงชื่อเว็บเป็นเลข IP", "choice_b": "ล้างไวรัสในอีเมล", "choice_c": "ปรับพัดลมเคส", "choice_d": "ดาวน์โหลดเกม",
                "correct_choice": "A", "explanation": "DNS แปลงชื่อเว็บไซต์ที่จำง่ายให้กลายเป็นหมายเลข IP Address"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 64-bit ดีกว่าระบบ 32-bit ในเรื่องการรองรับขนาดแรม (RAM) อย่างไร?",
                "choice_a": "รองรับแรมได้เกิน 4 GB", "choice_b": "ทำงานเร็วกว่าเสมอ 10 เท่า", "choice_c": "ใช้ได้เฉพาะเครื่องไม่มีดิสก์", "choice_d": "รองรับแรมได้เท่ากัน",
                "correct_choice": "A", "explanation": "ระบบ 32-bit รองรับ RAM สูงสุดเพียง 4 GB ส่วน 64-bit รองรับ RAM ได้มหาศาล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "อาการจอฟ้า 'Blue Screen of Death' (BSOD) มักเกิดจากสาเหตุใด?",
                "choice_a": "ฮาร์ดแวร์/ไดรเวอร์มีปัญหา", "choice_b": "หน้าจอเปลี่ยนสีตามอากาศ", "choice_c": "เปิดโปรแกรมเกิน 3 หน้า", "choice_d": "ปุ่มแป้นพิมพ์หลุด",
                "correct_choice": "A", "explanation": "BSOD คือหน้าจอแจ้งเตือนข้อผิดพลาดรุนแรงระดับฮาร์ดแวร์หรือไดรเวอร์ระบบ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "โปรแกรมประเภท 'Driver' (ไดรเวอร์) มีความสำคัญอย่างไร?",
                "choice_a": "ตัวกลางสั่งการฮาร์ดแวร์", "choice_b": "เป็นเกมแข่งรถ", "choice_c": "เป็นโปรแกรมฟังเพลง", "choice_d": "เป็นสายไฟเครื่องพิมพ์",
                "correct_choice": "A", "explanation": "Driver ทำหน้าที่เป็นตัวแปลคำสั่งให้ระบบปฏิบัติการสั่งการฮาร์ดแวร์ได้ถูกต้อง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ซิลิโคนระบายความร้อน (Thermal Paste) ทาไว้เพื่ออะไร?",
                "choice_a": "ส่งความร้อนจาก CPU ไปพัดลม", "choice_b": "ติดกาวไม่ให้ CPU หลุด", "choice_c": "เพิ่มแรมให้คอมพิวเตอร์", "choice_d": "ป้องกันไฟฟ้าลัดวงจร",
                "correct_choice": "A", "explanation": "Thermal Paste ช่วยส่งผ่านความร้อนจากหน้าสัมผัสของ CPU ไปยังพัดลมระบายความร้อน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หน่วยความจำแคช 'Cache Memory' ใน CPU มีประโยชน์อย่างไร?",
                "choice_a": "ส่งข้อมูลที่ใช้บ่อยให้ CPU เร็วขึ้น", "choice_b": "เก็บไฟล์หนังขนาดใหญ่", "choice_c": "ทำความสะอาดเคส", "choice_d": "ลดการกินไฟของจอ",
                "correct_choice": "A", "explanation": "Cache Memory ใน CPU มีความเร็วสูงมาก ช่วยพักข้อมูลที่ใช้บ่อยเพื่อลดเวลาเรียกใช้งาน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "มัลแวร์ประเภท 'Ransomware' (มัลแวร์เรียกค่าไถ่) ทำร้ายผู้ใช้อย่างไร?",
                "choice_a": "ล็อกไฟล์เพื่อเรียกเงิน", "choice_b": "เปิดเพลงเสียงดังตลอด", "choice_c": "เปลี่ยนภาพหน้าจอเป็นสีดำ", "choice_d": "ปิดเครื่องทุก 5 นาที",
                "correct_choice": "A", "explanation": "Ransomware จะเข้ารหัสล็อกไฟล์ในเครื่องแล้วขู่เรียกเงินเพื่อแลกกับรหัสปลดล็อก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การทำ 'RAID 1' มีประโยชน์อย่างไรในการเก็บข้อมูล?",
                "choice_a": "สำรอง 2 ดิสก์กันข้อมูลหาย", "choice_b": "ดูหนังได้ชัดขึ้น 2 เท่า", "choice_c": "ทำให้เสียงเพลงดังขึ้น", "choice_d": "ลดขนาดไฟล์ลงครึ่งหนึ่ง",
                "correct_choice": "A", "explanation": "RAID 1 (Mirroring) เขียนข้อมูลเหมือนกันลงดิสก์ 2 ตัว ช่วยป้องกันข้อมูลหายหากตัวใดตัวหนึ่งเสีย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "เหตุใด SSD แบบ 'M.2 NVMe' จึงเร็วกว่า SSD แบบ SATA?",
                "choice_a": "เชื่อมต่อตรงผ่านบัส PCIe", "choice_b": "มีขนาดตัวที่ใหญ่กว่า", "choice_c": "มีพัดลมในตัว 5 ตัว", "choice_d": "ใช้สายไฟบ้านโดยตรง",
                "correct_choice": "A", "explanation": "NVMe เชื่อมต่อผ่านบัส PCIe ตรงเข้าสู่ระบบ จึงอ่านเขียนข้อมูลได้ไวกว่า SATA มาก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "อาการ 'Bottleneck' (คอขวด) ในการจัดสเปกคอมพิวเตอร์คืออะไร?",
                "choice_a": "ชิ้นส่วนหนึ่งช้าจนฉุดเครื่อง", "choice_b": "มัดสายไฟในเคสแน่นเกิน", "choice_c": "ช่องพัดลมมีขนาดเล็ก", "choice_d": "เปิดโปรแกรมพร้อมกันมาก",
                "correct_choice": "A", "explanation": "Bottleneck เกิดขึ้นเมื่ออุปกรณ์ชิ้นใดชิ้นหนึ่งช้าเกินไปจนฉุดประสิทธิภาพของระบบรวม"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'UEFI' มีข้อดีกว่าระบบ 'BIOS' ดั้งเดิมอย่างไร?",
                "choice_a": "บูตเร็วกว่า รองรับดิสก์เกิน 2TB", "choice_b": "ทำให้ไม่ต้องใช้แรม", "choice_c": "เล่นเกมไม่กระตุกเลย", "choice_d": "ไม่ต้องเสียบปลั๊กไฟ",
                "correct_choice": "A", "explanation": "UEFI บูตเครื่องได้เร็วขึ้น มีหน้าตาเมนูทันสมัย และรองรับฮาร์ดดิสก์ความจุสูง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'Firewall' (ไฟร์วอลล์) มีหน้าที่อะไรในคอมพิวเตอร์?",
                "choice_a": "บล็อกการบุกรุกเครือข่าย", "choice_b": "ดับเพลิงเมื่อคอมร้อน", "choice_c": "ป้องกันไฟกระชาก", "choice_d": "เพิ่มแสงสว่างหน้าจอ",
                "correct_choice": "A", "explanation": "Firewall ทำหน้าที่เป็นประตูด่านตรวจ คัดกรองทราฟฟิกข้อมูลเพื่อป้องกันผู้บุกรุก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'VPN' ช่วยเพิ่มความปลอดภัยอย่างไรเวลาเล่นเน็ตสาธารณะ?",
                "choice_a": "ซ่อน IP และเข้ารหัสข้อมูล", "choice_b": "ล้างไวรัสในเครื่อง", "choice_c": "เพิ่มความเร็วเน็ต 10 เท่า", "choice_d": "ประหยัดแบตเตอรี่",
                "correct_choice": "A", "explanation": "VPN สร้างช่องทางส่งข้อมูลแบบเข้ารหัส ช่วยปกป้องความเป็นส่วนตัวบน Wi-Fi สาธารณะ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "สัญลักษณ์ '80 PLUS' บนพาวเวอร์ซัพพลาย (PSU) หมายถึงอะไร?",
                "choice_a": "ประสิทธิภาพแปลงไฟเกิน 80%", "choice_b": "รับประกันการใช้งาน 80 ปี", "choice_c": "รองรับอุณหภูมิ 80 องศา", "choice_d": "จ่ายไฟได้ 80 วัตต์",
                "correct_choice": "A", "explanation": "80 PLUS คือมาตรฐานรับรองประสิทธิภาพการแปลงพลังงานไฟฟ้าที่สูญเสียความร้อนน้อย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หน่วยความจำเสมือน 'Virtual Memory' ทำงานอย่างไรเมื่อ RAM เต็ม?",
                "choice_a": "ดึงพื้นที่ดิสก์มาช่วยพักแรม", "choice_b": "ส่งข้อมูลไปเก็บในมือถือ", "choice_c": "ปิดคอมพิวเตอร์ทันที", "choice_d": "ลบไฟล์รูปภาพทิ้ง",
                "correct_choice": "A", "explanation": "Virtual Memory นำพื้นที่จัดเก็บบนดิสก์มาช่วยพักข้อมูลชั่วคราวเพื่อป้องกันโปรแกรมค้าง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การทำ 'Overclock' (โอเวอร์คล็อก) คืออะไร?",
                "choice_a": "เร่งความเร็วเกินสเปกเดิม", "choice_b": "ตั้งเวลาเปิด-ปิดตามนาฬิกา", "choice_c": "การเปลี่ยนเคสใหม่", "choice_d": "การลดความเร็วพัดลม",
                "correct_choice": "A", "explanation": "Overclock คือการปรับเร่งความเร็วของ CPU หรือ GPU ให้ทำงานสูงกว่าค่ามาตรฐานโรงงาน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "กฎสำรองข้อมูล '3-2-1 Backup' มีหลักการง่าย ๆ อย่างไร?",
                "choice_a": "เก็บ 3 ชุด 2 สื่อ 1 คลาวด์", "choice_b": "สำรองสัปดาห์ละ 3 ครั้ง", "choice_c": "ใช้คอม 3 เครื่อง ดิสก์ 2 ตัว", "choice_d": "นับ 3 2 1 ก่อนกดบันทึก",
                "correct_choice": "A", "explanation": "3-2-1 Backup คือวิธีสำรองข้อมูลที่ดีที่สุด: 3 ชุดข้อมูล, 2 รูปแบบสื่อ, 1 ชุดบนคลาวด์"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ความละเอียดหน้าจอแบบ 'Full HD' (1080p) มีขนาดเท่าใด?",
                "choice_a": "1920 x 1080 พิกเซล", "choice_b": "1280 x 720 พิกเซล", "choice_c": "3840 x 2160 พิกเซล", "choice_d": "800 x 600 พิกเซล",
                "correct_choice": "A", "explanation": "Full HD มาตรฐานมีความละเอียด 1920 x 1080 พิกเซล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "อัตราการรีเฟรช 'Refresh Rate' 144Hz บนจอมอนิเตอร์ มีประโยชน์อย่างไร?",
                "choice_a": "ภาพเคลื่อนไหวลื่นไหลเนียนตา", "choice_b": "จอภาพประหยัดไฟขึ้น 2 เท่า", "choice_c": "เสียงเพลงดังขึ้น", "choice_d": "แป้นพิมพ์กดง่ายขึ้น",
                "correct_choice": "A", "explanation": "Refresh Rate 144Hz แสดงผล 144 ภาพต่อวินาที ทำให้ภาพเคลื่อนไหวเนียนตาลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หมายเลข 'MAC Address' แตกต่างจาก 'IP Address' อย่างไร?",
                "choice_a": "MAC ฝังติดการ์ดเน็ตถาวร", "choice_b": "MAC ใช้เฉพาะเครื่อง Apple", "choice_c": "IP เปลี่ยนแปลงไม่ได้", "choice_d": "ทั้งคู่เหมือนกันทุกอย่าง",
                "correct_choice": "A", "explanation": "MAC Address เป็นเลขประจำตัวฮาร์ดแวร์ถาวร ส่วน IP Address กำหนดตามเครือข่ายที่เชื่อมต่อ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'Multi-Core' (เช่น Quad-Core) ใน CPU หมายถึงอะไร?",
                "choice_a": "มีหลายแกนสมองในชิปเดียว", "choice_b": "มีพัดลมระบายความร้อน 4 ตัว", "choice_c": "มีสายไฟต่อเข้า 2 เส้น", "choice_d": "ทำให้หน้าจอมีหลายสี",
                "correct_choice": "A", "explanation": "Multi-Core คือการรวมหน่วยประมวลผลหลายแกนไว้ในชิป CPU เดียวกันเพื่อแบ่งงานกันทำ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "แรมมาตรฐาน 'DDR5' มีข้อดีกว่า 'DDR4' อย่างไร?",
                "choice_a": "ส่งข้อมูลไวกว่าและประหยัดไฟ", "choice_b": "มีขนาดแผงใหญ่กว่าเดิม 2 เท่า", "choice_c": "ไม่ต้องใช้กระแสไฟฟ้า", "choice_d": "เสียบลงช่อง DDR4 ได้ทันที",
                "correct_choice": "A", "explanation": "DDR5 มีความเร็วถ่ายโอนข้อมูลสูงกว่าและใช้พลังงานน้อยกว่า DDR4"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การโจมตีแบบ 'DDoS' บนเว็บไซต์ มีลักษณะอย่างไร?",
                "choice_a": "ยิงข้อมูลจนเว็บล่ม", "choice_b": "แอบขโมยแป้นพิมพ์", "choice_c": "ตัดสายไฟ", "choice_d": "ส่งสติกเกอร์ในแชท",
                "correct_choice": "A", "explanation": "DDoS มุ่งยิงทราฟฟิกปริมาณมหาศาลจากหลายเครื่องจนทำให้เซิร์ฟเวอร์เป้าหมายล่ม"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "เหตุใดจึงไม่ควรนำแฟลชไดรฟ์ของคนแปลกหน้ามาเสียบเครื่อง?",
                "choice_a": "เสี่ยงติดไวรัสหรือมัลแวร์", "choice_b": "ทำให้พอร์ต USB ละลาย", "choice_c": "ทำให้หน้าจอเปลี่ยนสี", "choice_d": "ทำให้ค่าไฟบ้านเพิ่มขึ้น",
                "correct_choice": "A", "explanation": "Flash Drive ที่ไม่ทราบที่มาอาจมีไวรัสแฝงอยู่เพื่อแพร่กระจายหรือขโมยข้อมูล"
            },

            # =========================================================================
            # [หมวด: สาขาวิทยาการคอมพิวเตอร์เบื้องต้น] (สำหรับน้อง ๆ ป.3 - ม.3) 10 ข้อ
            # =========================================================================
            {
                "category": cat_cs, "difficulty": "ง่าย", "is_active": True,
                "text": "สาขาวิทยาการคอมพิวเตอร์ (Computer Science) เรียนเน้นเรื่องอะไร?",
                "choice_a": "เขียนโค้ด สร้างเกม เว็บ และ AI", "choice_b": "ซ่อมพัดลมและเดินสายไฟ", "choice_c": "พิมพ์ดีดเอกสารอย่างเดียว", "choice_d": "เล่นเกมไม่ต้องเรียน",
                "correct_choice": "A", "explanation": "วิทยาการคอมพิวเตอร์ (CS) เรียนการคิดเป็นระบบ เขียนโค้ด สร้างเกม เว็บไซต์ และนวัตกรรม AI"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรมต่อบล็อกคำสั่งสีสันสดใสที่เด็ก ๆ นิยมใช้ฝึกสร้างเกมคือโปรแกรมใด?",
                "choice_a": "Scratch", "choice_b": "Excel", "choice_c": "Word", "choice_d": "Calculator",
                "correct_choice": "A", "explanation": "Scratch เป็นโปรแกรมเขียนโค้ดแบบต่อบล็อกที่สนุกและเข้าใจง่ายสำหรับน้อง ๆ"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย", "is_active": True,
                "text": "คำว่า 'อัลกอริทึม' (Algorithm) หมายถึงอะไร?",
                "choice_a": "ลำดับขั้นตอนการแก้ปัญหา", "choice_b": "ชื่อยี่ห้อคอมพิวเตอร์", "choice_c": "ภาษาต่างดาว", "choice_d": "ชื่อตัวละครในเกม",
                "correct_choice": "A", "explanation": "Algorithm คือลำดับขั้นตอนที่ชัดเจนในการแก้ปัญหาทีละสเต็ป"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย", "is_active": True,
                "text": "ในวงการเขียนโปรแกรม หากโค้ดทำงานผิดพลาด เราจะเรียกข้อผิดพลาดนั้นว่าอะไร?",
                "choice_a": "บั๊ก (Bug)", "choice_b": "มด (Ant)", "choice_c": "นก (Bird)", "choice_d": "ปลา (Fish)",
                "correct_choice": "A", "explanation": "Bug หมายถึงจุดบกพร่องหรือข้อผิดพลาดในโปรแกรมคอมพิวเตอร์"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ภาษาเขียนโปรแกรมยอดนิยมที่มีโลโก้รูป 'งู' และอ่านเข้าใจง่ายคือภาษาใด?",
                "choice_a": "Python (ไพทอน)", "choice_b": "Photoshop", "choice_c": "PowerPoint", "choice_d": "Paint",
                "correct_choice": "A", "explanation": "Python เป็นภาษาเขียนโปรแกรมที่อ่านง่ายและนิยมใช้สร้าง AI มากที่สุด"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "อาชีพใดเป็นสายงานตรงของคนที่จบสาขาวิทยาการคอมพิวเตอร์?",
                "choice_a": "โปรแกรมเมอร์และนักสร้างเกม", "choice_b": "ช่างซ่อมมอเตอร์ไซค์", "choice_c": "คนขับรถบรรทุก", "choice_d": "พนักงานพิมพ์ดีด",
                "correct_choice": "A", "explanation": "บัณฑิต CS สามารถเป็นนักพัฒนาซอฟต์แวร์ ผู้สร้างเกม และผู้เชี่ยวชาญด้านข้อมูล/AI"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "คำสั่ง 'If...Else' ในการเขียนโปรแกรม มีไว้ใช้ทำอะไร?",
                "choice_a": "เช็คเงื่อนไขเพื่อตัดสินใจ", "choice_b": "การวนทำซ้ำไม่รู้จบ", "choice_c": "ปิดเครื่องคอมพิวเตอร์", "choice_d": "ลบโค้ดทิ้ง",
                "correct_choice": "A", "explanation": "If-Else ใช้ตรวจสอบเงื่อนไข เช่น 'ถ้าคะแนนถึง 50 ให้ผ่าน มิฉะนั้น ให้ปรับปรุง'"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "คำสั่งประเภท 'Loop' ในการเขียนโปรแกรมมีประโยชน์อย่างไร?",
                "choice_a": "ทำงานซ้ำตามรอบที่สั่ง", "choice_b": "เปิดเพลงวนซ้ำ", "choice_c": "สุ่มตัวเลข", "choice_d": "ปิดหน้าต่างโปรแกรม",
                "correct_choice": "A", "explanation": "Loop หรือการวนซ้ำ ใช้สั่งให้คอมพิวเตอร์ทำงานเดิมซ้ำ ๆ โดยไม่ต้องเขียนโค้ดซ้ำหลายบรรทัด"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "โครงสร้างข้อมูลแบบ 'Stack' (สแต็ก) มีหลักการทำงานคล้ายสิ่งใด?",
                "choice_a": "กองจานซ้อนกัน (ใบบนออกก่อน)", "choice_b": "การต่อแถวซื้อขนม", "choice_c": "การโยนเหรียญ", "choice_d": "การหมุนวงล้อ",
                "correct_choice": "A", "explanation": "Stack ทำงานแบบ LIFO (Last-In First-Out) เปรียบเหมือนกองจานที่ใบบนสุดจะถูกหยิบออกก่อน"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "สาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยราชภัฏศรีสะเกษ มีตัวย่อว่าอะไร?",
                "choice_a": "CS (Computer Science)", "choice_b": "AI", "choice_c": "IT", "choice_d": "SE",
                "correct_choice": "A", "explanation": "CS ย่อมาจาก Computer Science คือสาขาวิชาวิทยาการคอมพิวเตอร์ มรภ.ศรีสะเกษ"
            },
        ]

        # 6. บันทึกคำถามลงใน SQLite
        self.stdout.write(self.style.NOTICE(f"3. บันทึกคำถาม {len(raw_questions)} ข้อลง SQLite..."))
        created_questions = []
        for i, q_data in enumerate(raw_questions, start=1):
            question = Question.objects.create(
                id=i,
                category=q_data["category"],
                text=q_data["text"],
                choice_a=q_data["choice_a"],
                choice_b=q_data["choice_b"],
                choice_c=q_data["choice_c"],
                choice_d=q_data["choice_d"],
                correct_choice=q_data["correct_choice"],
                explanation=q_data["explanation"],
                difficulty=q_data["difficulty"],
                is_active=q_data["is_active"],
            )
            created_questions.append(question)
        success_db = len(created_questions)
        self.stdout.write(self.style.SUCCESS(f"[OK] บันทึกลง SQLite เรียบร้อย ({success_db} ข้อ)"))

        # 7. ซิงค์ไปยัง Firebase Firestore แบบขนาน
        self.stdout.write(self.style.NOTICE(f"4. ซิงค์คำถาม {success_db} ข้อไปยัง Firebase Firestore..."))
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=15) as executor:
            sync_results = list(executor.map(sync_question_to_firestore, created_questions))
            success_fb = sum(1 for r in sync_results if r)
        self.stdout.write(self.style.SUCCESS(f"[OK] ซิงค์ขึ้น Firebase Firestore สำเร็จ ({success_fb}/{success_db} ข้อ)"))

        # สรุปผล
        self.stdout.write(self.style.SUCCESS(f"\n======================================================="))
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] คำถาม ป.3 - ม.3 (ตัวเลือกสั้นกระชับทุกข้อ 100 ข้อ) พร้อมใช้งาน 100%!"))
        self.stdout.write(self.style.SUCCESS(f"  - บันทึกลง SQLite: {success_db}/{len(raw_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - ซิงค์ขึ้น Firebase: {success_fb}/{len(raw_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวดคอมพิวเตอร์เบื้องต้น: ง่าย 40 ข้อ, ปานกลาง 25 ข้อ, ยาก 25 ข้อ (รวม 90 ข้อ)"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวดสาขาวิทยาการคอมพิวเตอร์เบื้องต้น: 10 ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - รวมทั้งหมด: 100 ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"======================================================="))
