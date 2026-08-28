import random
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from my_app.models import Category, Question, QuizLog
from my_app.firebase_config import (
    sync_question_to_firestore, 
    delete_question_from_firestore, 
    fetch_all_questions_from_firestore
)


class Command(BaseCommand):
    help = "สร้างชุดคำถามระดับ ป.3 - ม.ปลาย 150 ข้อ (เพิ่มข้อยาก 50 ข้อ พร้อมสุ่มกระจายตัวเลือก A, B, C, D) ซิงค์เข้า Firebase Firestore และ SQLite"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("=== เริ่มกระบวนการสร้างชุดคำถาม 150 ข้อ (สุ่มกระจายเฉลย A, B, C, D ครบทุกข้อ) ==="))

        # 1. เคลียร์คำถามเดิมทั้งหมดบน Firebase Firestore
        try:
            self.stdout.write(self.style.NOTICE("1. เคลียร์คำถามเดิมบน Firebase Firestore..."))
            old_docs = fetch_all_questions_from_firestore()
            deleted_count = 0
            if old_docs:
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
        self.stdout.write(self.style.SUCCESS(f"[OK] สร้าง 2 หมวดหมู่เรียบร้อย:"))
        self.stdout.write(f"  - หมวด 1: {cat_basic.name}")
        self.stdout.write(f"  - หมวด 2: {cat_cs.name}")

        # 5. ข้อมูลคำถามดิบ 150 ข้อ (ระบุคำตอบที่ถูกต้องและตัวเลือกหลอก เพื่อสุ่มตำแหน่ง A, B, C, D อัตโนมัติ)
        raw_items = [
            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับง่าย (ป.3 - ป.6) 40 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "อุปกรณ์ใดทำหน้าที่เหมือน 'หนู' ใช้เลื่อนลูกศรและคลิกบนหน้าจอ?",
                "correct": "เมาส์ (Mouse)", "distractors": ["คีย์บอร์ด", "ลำโพง", "พัดลม"],
                "explanation": "เมาส์ (Mouse) ใช้เลื่อนเคอร์เซอร์และคลิกเลือกเมนูบนจอภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หากต้องการพิมพ์ข้อความหรือตัวหนังสือเข้าคอมพิวเตอร์ ต้องใช้อุปกรณ์ใด?",
                "correct": "คีย์บอร์ด (Keyboard)", "distractors": ["สแกนเนอร์", "จอภาพ", "ไมโครโฟน"],
                "explanation": "คีย์บอร์ดใช้พิมพ์ตัวอักษรและตัวเลขเข้าสู่คอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มลัดสากล 'Ctrl + C' มีไว้ใช้ทำอะไร?",
                "correct": "คัดลอก (Copy)", "distractors": ["ตัด (Cut)", "วาง (Paste)", "ลบ (Delete)"],
                "explanation": "Ctrl + C คือปุ่มลัด Copy สำหรับคัดลอกข้อความหรือไฟล์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มลัด 'Ctrl + V' ใช้งานคู่กับ Ctrl + C เพื่อทำอะไร?",
                "correct": "วางข้อมูล (Paste)", "distractors": ["ย้อนกลับ (Undo)", "เลือกทั้งหมด (All)", "สั่งพิมพ์ (Print)"],
                "explanation": "Ctrl + V ใช้สำหรับวาง (Paste) สิ่งที่คัดลอกไว้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หากพิมพ์ข้อความผิดพลาด สามารถกดย้อนกลับ (Undo) ด้วยปุ่มใด?",
                "correct": "Ctrl + Z", "distractors": ["Ctrl + S", "Ctrl + O", "Ctrl + N"],
                "explanation": "Ctrl + Z คือคำสั่ง Undo เพื่อย้อนกลับการกระทำล่าสุด"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มลัด 'Ctrl + S' นิยมกดเป็นประจำเพื่อทำอะไร?",
                "correct": "บันทึกงาน (Save)", "distractors": ["ปิดคอมพิวเตอร์", "เปิดเพลง", "เพิ่มเสียง"],
                "explanation": "Ctrl + S ใช้บันทึกงาน (Save) เพื่อป้องกันงานสูญหาย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มที่ยาวที่สุดบนแป้นพิมพ์แถวล่างสุด เรียกว่าอะไร?",
                "correct": "Spacebar", "distractors": ["Enter", "Shift", "Caps Lock"],
                "explanation": "Spacebar ใช้สำหรับเคาะเว้นวรรคช่องว่างระหว่างตัวอักษร"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มใดใช้สำหรับ 'ขึ้นบรรทัดใหม่' หรือ 'ตกลง/ยืนยัน' คำสั่ง?",
                "correct": "Enter", "distractors": ["Esc", "Tab", "Alt"],
                "explanation": "ปุ่ม Enter ใช้ยืนยันคำสั่ง หรือขึ้นบรรทัดใหม่ในการพิมพ์งาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มใดที่เมื่อกดค้างไว้ จะช่วยให้พิมพ์ตัวพิมพ์ใหญ่ภาษาอังกฤษได้?",
                "correct": "Shift", "distractors": ["Ctrl", "Alt", "Tab"],
                "explanation": "กด Shift ค้างไว้แล้วกดตัวอักษรจะได้ตัวพิมพ์ใหญ่"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่ม 'Caps Lock' มีหน้าที่อะไรในการพิมพ์งาน?",
                "correct": "ล็อกพิมพ์ตัวใหญ่ตลอด", "distractors": ["ล็อกหน้าจอคอม", "ล็อกไม่ให้ลบไฟล์", "ปิดเสียงลำโพง"],
                "explanation": "Caps Lock ช่วยให้พิมพ์ตัวพิมพ์ใหญ่ต่อเนื่องโดยไม่ต้องกด Shift ค้าง"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "อุปกรณ์ชิ้นใดเปรียบเหมือน 'สมอง' ของคอมพิวเตอร์?",
                "correct": "ซีพียู (CPU)", "distractors": ["เมาส์ (Mouse)", "คีย์บอร์ด (Keyboard)", "จอภาพ (Monitor)"],
                "explanation": "CPU ทำหน้าที่ประมวลผลกลางเปรียบเหมือนสมองของคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หากต้องการพิมพ์รูปวาดหรือการบ้านออกมาบนกระดาษ ต้องใช้อุปกรณ์ใด?",
                "correct": "เครื่องพิมพ์ (Printer)", "distractors": ["สแกนเนอร์", "จอภาพ", "ลำโพง"],
                "explanation": "Printer (เครื่องพิมพ์) ใช้พิมพ์เอกสารและรูปลงบนกระดาษ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หากต้องการพูดคุยเสียงกับคุณครูหรือเพื่อนออนไลน์ ต้องใช้อุปกรณ์ใด?",
                "correct": "ไมโครโฟน", "distractors": ["ลำโพง", "หูฟัง", "เมาส์"],
                "explanation": "ไมโครโฟนทำหน้าที่รับเสียงพูดของเราส่งเข้าคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "อุปกรณ์พกพาขนาดเล็กที่ใช้เสียบช่อง USB เก็บการบ้านคืออะไร?",
                "correct": "แฟลชไดรฟ์ (Flash Drive)", "distractors": ["พัดลมเคส", "สายไฟคอม", "แรม (RAM)"],
                "explanation": "Flash Drive เป็นอุปกรณ์เก็บข้อมูลสำรองแบบพกพาสะดวก"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "Google Chrome และ Microsoft Edge จัดเป็นโปรแกรมประเภทใด?",
                "correct": "เว็บบราวเซอร์ (Web Browser)", "distractors": ["โปรแกรมวาดภาพ", "เครื่องคิดเลข", "โปรแกรมพิมพ์งาน"],
                "explanation": "Web Browser ใช้สำหรับเปิดดูเว็บไซต์และเล่นอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "โปรแกรมใดบน Windows ที่เด็ก ๆ นิยมใช้ฝึกวาดภาพและระบายสี?",
                "correct": "Paint", "distractors": ["Excel", "Word", "Calculator"],
                "explanation": "Paint เป็นโปรแกรมวาดภาพและระบายสีรูปทรงพื้นฐาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "โปรแกรม Microsoft Word เหมาะสำหรับใช้งานประเภทใด?",
                "correct": "พิมพ์เอกสารและรายงาน", "distractors": ["ตัดต่อภาพยนตร์", "ฟังวิทยุ", "สแกนหาฝุ่น"],
                "explanation": "Microsoft Word ใช้สำหรับพิมพ์งานเอกสารและทำรายงาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "โปรแกรม Microsoft PowerPoint นิยมใช้ทำอะไรมากที่สุด?",
                "correct": "ทำสไลด์นำเสนองาน", "distractors": ["เล่นเกมต่อสู้", "สร้างตารางสูตรคูณ", "ดูคลิปการ์ตูน"],
                "explanation": "PowerPoint ออกแบบมาสำหรับสร้างสไลด์นำเสนอข้อความและรูปภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ไอคอนรูปถังขยะ 'Recycle Bin' บนหน้าจอ มีไว้เพื่ออะไร?",
                "correct": "เก็บไฟล์ที่เพิ่งลบชั่วคราว", "distractors": ["เก็บเพลงใหม่ล่าสุด", "ทำลายคอมพิวเตอร์", "เก็บรูปภาพโปรด"],
                "explanation": "Recycle Bin เก็บไฟล์ที่เพิ่งลบ สามารถกู้คืน (Restore) กลับมาได้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่ม 'Backspace' บนแป้นพิมพ์ มีไว้ใช้ทำอะไรเวลาพิมพ์งาน?",
                "correct": "ลบตัวอักษรทางซ้าย", "distractors": ["เพิ่มเสียงลำโพง", "เปิดหน้าต่างใหม่", "ปิดเครื่องทันที"],
                "explanation": "Backspace ใช้ลบตัวอักษรที่อยู่ข้างหน้า (ซ้าย) ของเคอร์เซอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่ม 'Esc' (Escape) มุมบนซ้ายของคีย์บอร์ด มักใช้เพื่อทำอะไร?",
                "correct": "ยกเลิก / ออกจากเต็มจอ", "distractors": ["บันทึกงาน", "พิมพ์ตัวใหญ่", "เปิดเครื่องคอม"],
                "explanation": "ปุ่ม Esc ใช้กดยกเลิก หรือออกจากโหมดเต็มหน้าจอ / ออกจากเกม"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มฟังก์ชันใดบนแป้นพิมพ์ที่ใช้กดเพื่อ 'รีเฟรช' (Refresh) หน้าเว็บ?",
                "correct": "F5", "distractors": ["F1", "F12", "F4"],
                "explanation": "F5 เป็นปุ่มลัดมาตรฐานสำหรับโหลดหน้าเว็บใหม่ (Refresh)"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "การคลิกปุ่มซ้ายของเมาส์ 2 ครั้งติดกันอย่างรวดเร็ว เรียกว่าอะไร?",
                "correct": "ดับเบิลคลิก (Double Click)", "distractors": ["คลิกขวา", "สกอร์เมาส์", "แดร็กเมาส์"],
                "explanation": "Double Click คือการคลิก 2 ครั้งติดกันเพื่อเปิดโปรแกรมหรือเปิดไฟล์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "อุปกรณ์ใดใช้กระจายสัญญาณอินเทอร์เน็ตไร้สาย (Wi-Fi) ในบ้าน?",
                "correct": "เราเตอร์ (Router)", "distractors": ["เครื่องคิดเลข", "แฟลชไดรฟ์", "พาวเวอร์แบงก์"],
                "explanation": "Wi-Fi Router ทำหน้าที่กระจายสัญญาณอินเทอร์เน็ตไร้สาย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "รหัสผ่าน (Password) ที่ปลอดภัย ควรตั้งแบบใด?",
                "correct": "ผสมตัวหนังสือและตัวเลข", "distractors": ["ใช้ตัวเลข 123456", "ใช้วันเกิดตัวเอง", "บอกเพื่อนทุกคน"],
                "explanation": "รหัสผ่านที่ดีควรเดายากและผสมตัวอักษรกับตัวเลข"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ข้อมูลใดที่ไม่ควรบอกคนแปลกหน้าบนอินเทอร์เน็ตอย่างเด็ดขาด?",
                "correct": "รหัสผ่านและที่อยู่บ้าน", "distractors": ["การ์ตูนที่ชอบดู", "สีที่ชอบ", "วิชาที่ชอบเรียน"],
                "explanation": "รหัสผ่านและข้อมูลส่วนตัวเป็นความลับ ห้ามบอกคนอื่นเพื่อความปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ไฟล์รูปภาพทั่วไป มักมีนามสกุลไฟล์ลงท้ายด้วยอะไร?",
                "correct": ".jpg หรือ .png", "distractors": [".mp3", ".mp4", ".exe"],
                "explanation": ".jpg และ .png คือนามสกุลไฟล์รูปภาพยอดนิยม"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ไฟล์เพลงที่เปิดฟังในคอมพิวเตอร์ มักเป็นไฟล์นามสกุลใด?",
                "correct": ".mp3", "distractors": [".jpg", ".pdf", ".docx"],
                "explanation": ".mp3 เป็นรูปแบบไฟล์เสียงและเพลงมาตรฐาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ไฟล์เอกสารใบงานที่เปิดอ่านแล้วตัวหนังสือไม่เลื่อนเพี้ยน คือไฟล์ใด?",
                "correct": ".pdf", "distractors": [".mp3", ".avi", ".exe"],
                "explanation": ".pdf เป็นไฟล์เอกสารที่คงรูปแบบหน้ากระดาษเดิมทุกอุปกรณ์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หูฟังไร้สายเชื่อมต่อกับคอมพิวเตอร์ด้วยสัญญาณใด?",
                "correct": "บลูทูธ (Bluetooth)", "distractors": ["สัญญาณ GPS", "คลื่นไมโครเวฟ", "สายไฟบ้าน"],
                "explanation": "Bluetooth เป็นคลื่นสัญญาณไร้สายระยะใกล้สำหรับหูฟังและเมาส์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มลัด 'Ctrl + A' มีประโยชน์อย่างไร?",
                "correct": "เลือกทั้งหมด (Select All)", "distractors": ["ลบไฟล์ทั้งหมด", "ปิดหน้าต่าง", "บันทึกงานทันที"],
                "explanation": "Ctrl + A ใช้เลือกคลุมข้อความหรือไฟล์ทั้งหมดในครั้งเดียว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ปุ่มลัด 'Alt + Tab' บนคอมพิวเตอร์ ใช้สำหรับทำอะไร?",
                "correct": "สลับหน้าต่างโปรแกรม", "distractors": ["ปิดคอมพิวเตอร์", "แคปหน้าจอ", "เพิ่มเสียงลำโพง"],
                "explanation": "Alt + Tab ใช้สลับเปลี่ยนหน้าต่างโปรแกรมที่เปิดอยู่ได้อย่างรวดเร็ว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "เว็บไซต์ 'Google' ทำหน้าที่หลักเป็นอะไร?",
                "correct": "ค้นหาข้อมูล (Search Engine)", "distractors": ["โปรแกรมวาดภาพ", "เครื่องคิดเลข", "เกมออนไลน์"],
                "explanation": "Google เป็น Search Engine ใช้ค้นหาข้อมูล รูปภาพ และวิดีโอบนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "การดึงรูปหรือเกมจากอินเทอร์เน็ตมาเก็บไว้ในเครื่อง เรียกว่าอะไร?",
                "correct": "ดาวน์โหลด (Download)", "distractors": ["อัปโหลด (Upload)", "รีสตาร์ท", "ดีลีต"],
                "explanation": "Download คือการดึงไฟล์จากเน็ตมาบันทึกในเครื่องของเรา"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "การส่งรูปหรือการบ้านขึ้นไปบนเว็บไซต์ เรียกว่าอะไร?",
                "correct": "อัปโหลด (Upload)", "distractors": ["ดาวน์โหลด (Download)", "สแกน", "ปรินต์"],
                "explanation": "Upload คือการส่งไฟล์จากเครื่องเราขึ้นไปบนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "คำว่า 'WWW' หน้าชื่อเว็บไซต์ ย่อมาจากอะไร?",
                "correct": "World Wide Web", "distractors": ["World Wide Windows", "Web World Wide", "Wifi World Web"],
                "explanation": "World Wide Web คือเครือข่ายใยแมงมุมที่เชื่อมต่อเว็บไซต์ทั่วโลก"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "อุปกรณ์ใดทำหน้าที่แสดงภาพและตัวหนังสือให้เรามองเห็น?",
                "correct": "จอภาพ (Monitor)", "distractors": ["ฮาร์ดดิสก์", "คีย์บอร์ด", "เคสคอมพิวเตอร์"],
                "explanation": "Monitor (จอภาพ) ทำหน้าที่แสดงผลลัพธ์รูปภาพและวิดีโอ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "ข้อใดเป็นท่านั่งใช้งานคอมพิวเตอร์ที่ถูกต้องที่สุด?",
                "correct": "นั่งหลังตรงพักสายตา", "distractors": ["นอนคว่ำเล่นในที่มืด", "วางแก้วน้ำบนเคสคอม", "จ้องจอนาน 10 ชม.ติด"],
                "explanation": "การนั่งหลังตรงและพักสายตาทุก 20-30 นาทีช่วยถนอมสายตาและสุขภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "หากหน้าจอคอมพิวเตอร์มีฝุ่นเกาะ ควรทำความสะอาดอย่างไร?",
                "correct": "ใช้ผ้านุ่มไมโครไฟเบอร์", "distractors": ["เอาน้ำสาดใส่หน้าจอ", "ใช้แปรงลวดขัด", "เอาน้ำยาล้างจานราด"],
                "explanation": "ควรใช้ผ้าไมโครไฟเบอร์แห้งนุ่มเช็ดหน้าจอเบา ๆ หลังปิดจอแล้ว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย",
                "text": "กล่องสี่เหลี่ยมที่รวมชิ้นส่วนข้างในของคอมพิวเตอร์ไว้ เรียกว่าอะไร?",
                "correct": "เคส (Computer Case)", "distractors": ["เมาส์", "แผ่นรองเมาส์", "แฟลชไดรฟ์"],
                "explanation": "เคส (Case) คือตัวถังที่บรรจุอุปกรณ์ภายในคอมพิวเตอร์ทั้งหมด"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับปานกลาง (ป.5 - ม.2) 25 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "หน่วยความจำ 'RAM' ทำหน้าที่เปรียบเสมือนอะไร?",
                "correct": "โต๊ะทำงานชั่วคราว", "distractors": ["ตู้เก็บของถาวร", "หลอดไฟส่องสว่าง", "ลำโพงส่งเสียง"],
                "explanation": "RAM เปรียบเหมือนโต๊ะทำงานชั่วคราว ยิ่งโต๊ะใหญ่ยิ่งเปิดหลายโปรแกรมได้ลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "หน่วยความจำ 'SSD' มีจุดเด่นเหนือกว่าฮาร์ดดิสก์จานหมุนแบบเดิมอย่างไร?",
                "correct": "อ่านเขียนเร็วกว่ามาก", "distractors": ["ราคาถูกกว่ามาก", "รับสัญญาณวิทยุได้", "มีความจุไม่จำกัด"],
                "explanation": "SSD บันทึกข้อมูลลงชิปอิเล็กทรอนิกส์ จึงเปิดเครื่องและโหลดเกมเร็วกว่าฮาร์ดดิสก์มาก"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ในระบบคอมพิวเตอร์ 1 ไบต์ (Byte) มีค่าเท่ากับกี่บิต (Bit)?",
                "correct": "8 บิต", "distractors": ["4 บิต", "16 บิต", "100 บิต"],
                "explanation": "1 Byte เท่ากับ 8 Bits ซึ่งพอดีสำหรับเก็บตัวอักษร 1 ตัว"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "หน่วยวัดความจุข้อใดมีขนาดใหญ่ที่สุด?",
                "correct": "1 Terabyte (TB)", "distractors": ["1 Gigabyte (GB)", "1 Megabyte (MB)", "1 Kilobyte (KB)"],
                "explanation": "เรียงจากเล็กไปใหญ่: KB -> MB -> GB -> TB (1 TB เท่ากับประมาณ 1,024 GB)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ความจุ 1 Gigabyte (GB) มีค่าเท่ากับกี่ Megabyte (MB)?",
                "correct": "1,024 MB", "distractors": ["100 MB", "10 MB", "1,000,000 MB"],
                "explanation": "ในระบบเลขฐานสอง 1 GB มีค่าเท่ากับ 1,024 MB"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "การ์ดจอ หรือ 'GPU' มีหน้าที่หลักเน้นไปที่งานประเภทใด?",
                "correct": "ประมวลผลภาพและเกม 3D", "distractors": ["จ่ายไฟเข้าเมนบอร์ด", "เก็บไฟล์เสียง", "ป้องกันฝุ่นเข้าเคส"],
                "explanation": "GPU ทำหน้าที่ประมวลผลกราฟิก วิดีโอ และเกม 3 มิติให้สวยงามลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "สายเคเบิล 'HDMI' ส่งสัญญาณอะไรไปยังจอภาพ?",
                "correct": "ส่งทั้งภาพและเสียง", "distractors": ["ส่งเฉพาะกระแสไฟ", "ส่งเฉพาะเสียงเพลง", "ส่งคลื่นวิทยุ"],
                "explanation": "HDMI ส่งสัญญาณภาพความละเอียดสูงและเสียงพร้อมกันในสายเส้นเดียว"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ไวรัสคอมพิวเตอร์ (Computer Virus) คืออะไร?",
                "correct": "โปรแกรมทำลายข้อมูล", "distractors": ["เชื้อโรคที่ทำให้คนป่วย", "ฝุ่นในพัดลมซีพียู", "สายไฟที่ขาดในเครื่อง"],
                "explanation": "ไวรัสคอมพิวเตอร์คือซอฟต์แวร์ไม่พึงประสงค์ที่มุ่งทำลายหรือขโมยข้อมูล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "โปรแกรมแอนติไวรัส (Antivirus) มีหน้าที่หลักคืออะไร?",
                "correct": "ตรวจจับและกำจัดไวรัส", "distractors": ["ช่วยให้เล่นเกมชนะ", "เพิ่มความเร็วพิมพ์งาน", "ปรับหน้าจอให้สว่าง"],
                "explanation": "Antivirus ช่วยตรวจจับ ป้องกัน และกำจัดภัยคุกคามในคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "Google Drive และ iCloud จัดเป็นบริการประเภทใด?",
                "correct": "คลาวด์สตอเรจ (Cloud Storage)", "distractors": ["เกมออนไลน์", "โปรแกรมตัดต่อเพลง", "การ์ดจอเสริม"],
                "explanation": "Cloud Storage ให้บริการเก็บไฟล์ออนไลน์ สามารถเปิดอ่านได้ทุกที่"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ภัยคุกคามแบบ 'Phishing' (ฟิชชิ่ง) มีลักษณะการหลอกลวงอย่างไร?",
                "correct": "ส่งลิงก์ปลอมหลอกเอาข้อมูล", "distractors": ["ปาหินใส่หน้าจอคอม", "พิมพ์แป้นพิมพ์เร็วไป", "เปิดเพลงเสียงดังไป"],
                "explanation": "Phishing คือการทำหน้าเว็บหรืออีเมลปลอมเพื่อหลอกให้เหยื่อกรอกรหัสผ่าน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ระบบยืนยันตัวตน 2 ชั้น (2FA) ช่วยเพิ่มความปลอดภัยอย่างไร?",
                "correct": "ใส่รหัสผ่านคู่กับ OTP", "distractors": ["ล็อกอินพร้อมกัน 2 คน", "พิมพ์รหัสเดิม 2 รอบ", "เปิดคอม 2 เครื่องพร้อมกัน"],
                "explanation": "2FA เพิ่มความปลอดภัยโดยต้องใช้รหัส OTP จากมือถือร่วมกับรหัสผ่าน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ไฟล์บีบอัดนามสกุล '.zip' มีประโยชน์อย่างไร?",
                "correct": "รวมไฟล์และย่อขนาดลง", "distractors": ["แปลงรูปภาพเป็นเพลง", "เพิ่มความเร็วพัดลม", "ทำให้ภาพคมชัด 10 เท่า"],
                "explanation": "ไฟล์ Zip ช่วยรวมหลาย ๆ ไฟล์เข้าด้วยกันและลดขนาดไฟล์ให้ส่งต่อง่าย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ที่อยู่เว็บไซต์ เช่น 'https://www.google.com' มีชื่อเรียกว่าอะไร?",
                "correct": "URL", "distractors": ["CPU", "RAM", "PDF"],
                "explanation": "URL (Uniform Resource Locator) คือที่อยู่ระบุตำแหน่งเว็บไซต์บนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ระบบปฏิบัติการยอดนิยมสำหรับเครื่องคอมพิวเตอร์ PC คือข้อใด?",
                "correct": "Microsoft Windows", "distractors": ["Photoshop", "Google Chrome", "Roblox"],
                "explanation": "Windows เป็นระบบปฏิบัติการยอดนิยมสำหรับเครื่องคอมพิวเตอร์ทั่วไป"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ระบบปฏิบัติการหลักบนสมาร์ตโฟนในปัจจุบันคือข้อใด?",
                "correct": "Android และ iOS", "distractors": ["Windows 95 และ DOS", "Word และ Excel", "Paint และ Notepad"],
                "explanation": "สมาร์ตโฟนส่วนใหญ่ใช้ระบบปฏิบัติการ Android หรือ iOS (iPhone)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "สัญลักษณ์แม่กุญแจและ 'https://' บนเว็บเบราว์เซอร์ หมายถึงอะไร?",
                "correct": "เว็บมีการเข้ารหัสปลอดภัย", "distractors": ["เว็บนี้ต้องเสียเงินเข้าชม", "เว็บสำหรับเล่นเกมเท่านั้น", "เว็บกำลังถูกไวรัสโจมตี"],
                "explanation": "HTTPS มีการเข้ารหัสความปลอดภัย ป้องกันข้อมูลถูกแอบดักจับ"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "แผงวงจรหลักที่เชื่อมต่ออุปกรณ์ทุกชิ้นในคอมพิวเตอร์เข้าด้วยกันคืออะไร?",
                "correct": "เมนบอร์ด (Motherboard)", "distractors": ["การ์ดเสียง", "สายไฟบ้าน", "เว็บแคม"],
                "explanation": "Motherboard คือแผงวงจรพิมพ์หลักที่เป็นศูนย์กลางเชื่อมต่ออุปกรณ์ทุกชิ้น"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "พาวเวอร์ซัพพลาย (Power Supply Unit : PSU) มีหน้าที่อะไร?",
                "correct": "แปลงและจ่ายไฟให้เครื่อง", "distractors": ["เปิดเสียงเพลงเมื่อเปิดเครื่อง", "ทำความสะอาดหน้าจอ", "บันทึกรูปภาพ"],
                "explanation": "PSU ทำหน้าที่แปลงไฟฟ้าบ้านและจ่ายพลังงานไฟฟ้าไปเลี้ยงทุกชิ้นส่วนในคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "เครือข่าย 'LAN' หมายถึงการเชื่อมต่อแบบใด?",
                "correct": "เครือข่ายระยะใกล้ในห้อง", "distractors": ["เครือข่ายดาวเทียมรอบโลก", "เครือข่ายใต้มหาสมุทร", "เครือข่ายสถานีอวกาศ"],
                "explanation": "LAN (Local Area Network) คือเครือข่ายท้องถิ่นระยะใกล้ เช่น ในห้องคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "สัญลักษณ์ใดที่ต้องมีคั่นในที่อยู่อีเมลเสมอ เช่น student...gmail.com?",
                "correct": "@ (เครื่องหมายแอท)", "distractors": ["# (แฮชแท็ก)", "$ (ดอลลาร์)", "& (แอนด์)"],
                "explanation": "สัญลักษณ์ @ ใช้คั่นระหว่างชื่อผู้ใช้กับชื่อโดเมนอีเมล เช่น user@gmail.com"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "กล้องเว็บแคม (Webcam) จัดเป็นอุปกรณ์ประเภทใด?",
                "correct": "อุปกรณ์รับข้อมูล (Input)", "distractors": ["อุปกรณ์แสดงผล (Output)", "อุปกรณ์ประมวลผล", "อุปกรณ์จ่ายไฟ"],
                "explanation": "Webcam รับภาพจากภายนอกเข้าสู่ระบบคอมพิวเตอร์ จึงเป็นอุปกรณ์ Input"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "โปรแกรมแบบ 'Open Source' มีความหมายว่าอย่างไร?",
                "correct": "เปิดเผยโค้ดให้พัฒนาฟรี", "distractors": ["ต้องเปิดฝาเครื่องเวลาใช้", "โปรแกรมราคาแพงที่สุด", "ห้ามคนอื่นดูโค้ด"],
                "explanation": "Open Source คือซอฟต์แวร์ที่เปิดเผยซอร์สโค้ดให้ทุกคนนำไปพัฒนาต่อยอดได้ฟรี"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "หน่วยวัดความเร็วเน็ต 'Mbps' คำว่า 'M' ย่อมาจากอะไร?",
                "correct": "Mega (ล้าน)", "distractors": ["Minute", "Mouse", "Music"],
                "explanation": "Mbps ย่อมาจาก Megabits per second (ล้านบิตต่อวินาที)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง",
                "text": "ปุ่ม 'Ctrl + Shift + Esc' ใน Windows ใช้เปิดโปรแกรมใดเพื่อดูว่าโปรแกรมไหนค้าง?",
                "correct": "Task Manager", "distractors": ["Paint", "Recycle Bin", "Calculator"],
                "explanation": "Task Manager ใช้ตรวจสอบโปรแกรมที่ทำงานอยู่และสามารถสั่งปิดโปรแกรมที่ค้างได้"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับยาก (เดิม 25 ข้อ)
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หมายเลข 'IP Address' ในเครือข่ายอินเทอร์เน็ตทำหน้าที่เปรียบเหมือนสิ่งใด?",
                "correct": "บ้านเลขที่ระบุตำแหน่งเครื่อง", "distractors": ["รหัสผ่านเกม", "ยี่ห้อจอภาพ", "ความสว่างหน้าจอ"],
                "explanation": "IP Address ทำหน้าที่เป็นหมายเลขระบุตัวตนและตำแหน่งของอุปกรณ์ในเครือข่าย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 'DNS' (Domain Name System) ในอินเทอร์เน็ตมีหน้าที่อะไร?",
                "correct": "แปลงชื่อเว็บเป็นเลข IP", "distractors": ["ล้างไวรัสในอีเมล", "ปรับพัดลมเคส", "ดาวน์โหลดเกม"],
                "explanation": "DNS แปลงชื่อเว็บไซต์ที่จำง่ายให้กลายเป็นหมายเลข IP Address"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 64-bit ดีกว่าระบบ 32-bit ในเรื่องการรองรับขนาดแรม (RAM) อย่างไร?",
                "correct": "รองรับแรมได้เกิน 4 GB", "distractors": ["ทำงานเร็วกว่าเสมอ 10 เท่า", "ใช้ได้เฉพาะเครื่องไม่มีดิสก์", "รองรับแรมได้เท่ากัน"],
                "explanation": "ระบบ 32-bit รองรับ RAM สูงสุดเพียง 4 GB ส่วน 64-bit รองรับ RAM ได้มหาศาล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "อาการจอฟ้า 'Blue Screen of Death' (BSOD) มักเกิดจากสาเหตุใด?",
                "correct": "ฮาร์ดแวร์/ไดรเวอร์มีปัญหา", "distractors": ["หน้าจอเปลี่ยนสีตามอากาศ", "เปิดโปรแกรมเกิน 3 หน้า", "ปุ่มแป้นพิมพ์หลุด"],
                "explanation": "BSOD คือหน้าจอแจ้งเตือนข้อผิดพลาดรุนแรงระดับฮาร์ดแวร์หรือไดรเวอร์ระบบ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "โปรแกรมประเภท 'Driver' (ไดรเวอร์) มีความสำคัญอย่างไร?",
                "correct": "ตัวกลางสั่งการฮาร์ดแวร์", "distractors": ["เป็นเกมแข่งรถ", "เป็นโปรแกรมฟังเพลง", "เป็นสายไฟเครื่องพิมพ์"],
                "explanation": "Driver ทำหน้าที่เป็นตัวแปลคำสั่งให้ระบบปฏิบัติการสั่งการฮาร์ดแวร์ได้ถูกต้อง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ซิลิโคนระบายความร้อน (Thermal Paste) ทาไว้เพื่ออะไร?",
                "correct": "ส่งความร้อนจาก CPU ไปพัดลม", "distractors": ["ติดกาวไม่ให้ CPU หลุด", "เพิ่มแรมให้คอมพิวเตอร์", "ป้องกันไฟฟ้าลัดวงจร"],
                "explanation": "Thermal Paste ช่วยส่งผ่านความร้อนจากหน้าสัมผัสของ CPU ไปยังพัดลมระบายความร้อน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หน่วยความจำแคช 'Cache Memory' ใน CPU มีประโยชน์อย่างไร?",
                "correct": "ส่งข้อมูลที่ใช้บ่อยให้ CPU เร็วขึ้น", "distractors": ["เก็บไฟล์หนังขนาดใหญ่", "ทำความสะอาดเคส", "ลดการกินไฟของจอ"],
                "explanation": "Cache Memory ใน CPU มีความเร็วสูงมาก ช่วยพักข้อมูลที่ใช้บ่อยเพื่อลดเวลาเรียกใช้งาน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "มัลแวร์ประเภท 'Ransomware' (มัลแวร์เรียกค่าไถ่) ทำร้ายผู้ใช้อย่างไร?",
                "correct": "ล็อกไฟล์เพื่อเรียกเงิน", "distractors": ["เปิดเพลงเสียงดังตลอด", "เปลี่ยนภาพหน้าจอเป็นสีดำ", "ปิดเครื่องทุก 5 นาที"],
                "explanation": "Ransomware จะเข้ารหัสล็อกไฟล์ในเครื่องแล้วขู่เรียกเงินเพื่อแลกกับรหัสปลดล็อก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การทำ 'RAID 1' มีประโยชน์อย่างไรในการเก็บข้อมูล?",
                "correct": "สำรอง 2 ดิสก์กันข้อมูลหาย", "distractors": ["ดูหนังได้ชัดขึ้น 2 เท่า", "ทำให้เสียงเพลงดังขึ้น", "ลดขนาดไฟล์ลงครึ่งหนึ่ง"],
                "explanation": "RAID 1 (Mirroring) เขียนข้อมูลเหมือนกันลงดิสก์ 2 ตัว ช่วยป้องกันข้อมูลหายหากตัวใดตัวหนึ่งเสีย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "เหตุใด SSD แบบ 'M.2 NVMe' จึงเร็วกว่า SSD แบบ SATA?",
                "correct": "เชื่อมต่อตรงผ่านบัส PCIe", "distractors": ["มีขนาดตัวที่ใหญ่กว่า", "มีพัดลมในตัว 5 ตัว", "ใช้สายไฟบ้านโดยตรง"],
                "explanation": "NVMe เชื่อมต่อผ่านบัส PCIe ตรงเข้าสู่ระบบ จึงอ่านเขียนข้อมูลได้ไวกว่า SATA มาก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "อาการ 'Bottleneck' (คอขวด) ในการจัดสเปกคอมพิวเตอร์คืออะไร?",
                "correct": "ชิ้นส่วนหนึ่งช้าจนฉุดเครื่อง", "distractors": ["มัดสายไฟในเคสแน่นเกิน", "ช่องพัดลมมีขนาดเล็ก", "เปิดโปรแกรมพร้อมกันมาก"],
                "explanation": "Bottleneck เกิดขึ้นเมื่ออุปกรณ์ชิ้นใดชิ้นหนึ่งช้าเกินไปจนฉุดประสิทธิภาพของระบบรวม"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 'UEFI' มีข้อดีกว่าระบบ 'BIOS' ดั้งเดิมอย่างไร?",
                "correct": "บูตเร็วกว่า รองรับดิสก์เกิน 2TB", "distractors": ["ทำให้ไม่ต้องใช้แรม", "เล่นเกมไม่กระตุกเลย", "ไม่ต้องเสียบปลั๊กไฟ"],
                "explanation": "UEFI บูตเครื่องได้เร็วขึ้น มีหน้าตาเมนูทันสมัย และรองรับฮาร์ดดิสก์ความจุสูง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 'Firewall' (ไฟร์วอลล์) มีหน้าที่อะไรในคอมพิวเตอร์?",
                "correct": "บล็อกการบุกรุกเครือข่าย", "distractors": ["ดับเพลิงเมื่อคอมร้อน", "ป้องกันไฟกระชาก", "เพิ่มแสงสว่างหน้าจอ"],
                "explanation": "Firewall ทำหน้าที่เป็นประตูด่านตรวจ คัดกรองทราฟฟิกข้อมูลเพื่อป้องกันผู้บุกรุก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 'VPN' ช่วยเพิ่มความปลอดภัยอย่างไรเวลาเล่นเน็ตสาธารณะ?",
                "correct": "ซ่อน IP และเข้ารหัสข้อมูล", "distractors": ["ล้างไวรัสในเครื่อง", "เพิ่มความเร็วเน็ต 10 เท่า", "ประหยัดแบตเตอรี่"],
                "explanation": "VPN สร้างช่องทางส่งข้อมูลแบบเข้ารหัส ช่วยปกป้องความเป็นส่วนตัวบน Wi-Fi สาธารณะ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "สัญลักษณ์ '80 PLUS' บนพาวเวอร์ซัพพลาย (PSU) หมายถึงอะไร?",
                "correct": "ประสิทธิภาพแปลงไฟเกิน 80%", "distractors": ["รับประกันการใช้งาน 80 ปี", "รองรับอุณหภูมิ 80 องศา", "จ่ายไฟได้ 80 วัตต์"],
                "explanation": "80 PLUS คือมาตรฐานรับรองประสิทธิภาพการแปลงพลังงานไฟฟ้าที่สูญเสียความร้อนน้อย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หน่วยความจำเสมือน 'Virtual Memory' ทำงานอย่างไรเมื่อ RAM เต็ม?",
                "correct": "ดึงพื้นที่ดิสก์มาช่วยพักแรม", "distractors": ["ส่งข้อมูลไปเก็บในมือถือ", "ปิดคอมพิวเตอร์ทันที", "ลบไฟล์รูปภาพทิ้ง"],
                "explanation": "Virtual Memory นำพื้นที่จัดเก็บบนดิสก์มาช่วยพักข้อมูลชั่วคราวเพื่อป้องกันโปรแกรมค้าง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การทำ 'Overclock' (โอเวอร์คล็อก) คืออะไร?",
                "correct": "เร่งความเร็วเกินสเปกเดิม", "distractors": ["ตั้งเวลาเปิด-ปิดตามนาฬิกา", "การเปลี่ยนเคสใหม่", "การลดความเร็วพัดลม"],
                "explanation": "Overclock คือการปรับเร่งความเร็วของ CPU หรือ GPU ให้ทำงานสูงกว่าค่ามาตรฐานโรงงาน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "กฎสำรองข้อมูล '3-2-1 Backup' มีหลักการง่าย ๆ อย่างไร?",
                "correct": "เก็บ 3 ชุด 2 สื่อ 1 คลาวด์", "distractors": ["สำรองสัปดาห์ละ 3 ครั้ง", "ใช้คอม 3 เครื่อง ดิสก์ 2 ตัว", "นับ 3 2 1 ก่อนกดบันทึก"],
                "explanation": "3-2-1 Backup คือวิธีสำรองข้อมูลที่ดีที่สุด: 3 ชุดข้อมูล, 2 รูปแบบสื่อ, 1 ชุดบนคลาวด์"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ความละเอียดหน้าจอแบบ 'Full HD' (1080p) มีขนาดเท่าใด?",
                "correct": "1920 x 1080 พิกเซล", "distractors": ["1280 x 720 พิกเซล", "3840 x 2160 พิกเซล", "800 x 600 พิกเซล"],
                "explanation": "Full HD มาตรฐานมีความละเอียด 1920 x 1080 พิกเซล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "อัตราการรีเฟรช 'Refresh Rate' 144Hz บนจอมอนิเตอร์ มีประโยชน์อย่างไร?",
                "correct": "ภาพเคลื่อนไหวลื่นไหลเนียนตา", "distractors": ["จอภาพประหยัดไฟขึ้น 2 เท่า", "เสียงเพลงดังขึ้น", "แป้นพิมพ์กดง่ายขึ้น"],
                "explanation": "Refresh Rate 144Hz แสดงผล 144 ภาพต่อวินาที ทำให้ภาพเคลื่อนไหวเนียนตาลื่นไหล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หมายเลข 'MAC Address' แตกต่างจาก 'IP Address' อย่างไร?",
                "correct": "MAC ฝังติดการ์ดเน็ตถาวร", "distractors": ["MAC ใช้เฉพาะเครื่อง Apple", "IP เปลี่ยนแปลงไม่ได้", "ทั้งคู่เหมือนกันทุกอย่าง"],
                "explanation": "MAC Address เป็นเลขประจำตัวฮาร์ดแวร์ถาวร ส่วน IP Address กำหนดตามเครือข่ายที่เชื่อมต่อ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบ 'Multi-Core' (เช่น Quad-Core) ใน CPU หมายถึงอะไร?",
                "correct": "มีหลายแกนสมองในชิปเดียว", "distractors": ["มีพัดลมระบายความร้อน 4 ตัว", "มีสายไฟต่อเข้า 2 เส้น", "ทำให้หน้าจอมีหลายสี"],
                "explanation": "Multi-Core คือการรวมหน่วยประมวลผลหลายแกนไว้ในชิป CPU เดียวกันเพื่อแบ่งงานกันทำ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "แรมมาตรฐาน 'DDR5' มีข้อดีกว่า 'DDR4' อย่างไร?",
                "correct": "ส่งข้อมูลไวกว่าและประหยัดไฟ", "distractors": ["มีขนาดแผงใหญ่กว่าเดิม 2 เท่า", "ไม่ต้องใช้กระแสไฟฟ้า", "เสียบลงช่อง DDR4 ได้ทันที"],
                "explanation": "DDR5 มีความเร็วถ่ายโอนข้อมูลสูงกว่าและใช้พลังงานน้อยกว่า DDR4"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การโจมตีแบบ 'DDoS' บนเว็บไซต์ มีลักษณะอย่างไร?",
                "correct": "ยิงข้อมูลจนเว็บล่ม", "distractors": ["แอบขโมยแป้นพิมพ์", "ตัดสายไฟ", "ส่งสติกเกอร์ในแชท"],
                "explanation": "DDoS มุ่งยิงทราฟฟิกปริมาณมหาศาลจากหลายเครื่องจนทำให้เซิร์ฟเวอร์เป้าหมายล่ม"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "เหตุใดจึงไม่ควรนำแฟลชไดรฟ์ของคนแปลกหน้ามาเสียบเครื่อง?",
                "correct": "เสี่ยงติดไวรัสหรือมัลแวร์", "distractors": ["ทำให้พอร์ต USB ละลาย", "ทำให้หน้าจอเปลี่ยนสี", "ทำให้ค่าไฟบ้านเพิ่มขึ้น"],
                "explanation": "Flash Drive ที่ไม่ทราบที่มาอาจมีไวรัสแฝงอยู่เพื่อแพร่กระจายหรือขโมยข้อมูล"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับยาก (เพิ่มใหม่อีก 25 ข้อ)
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หน่วยคำนวณทางคณิตศาสตร์และตรรกะภายใน CPU มีชื่อย่อว่าอะไร?",
                "correct": "ALU", "distractors": ["GPU", "PSU", "BIOS"],
                "explanation": "ALU (Arithmetic Logic Unit) ทำหน้าที่คำนวณตัวเลขและเปรียบเทียบตรรกะใน CPU"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หน่วยความจำประเภทใดมีความเร็วในการอ่านเขียนสูงสุดและอยู่ใกล้ชิดแกนประมวลผลมากที่สุด?",
                "correct": "รีจิสเตอร์ (Register)", "distractors": ["Cache L3", "RAM DDR5", "NVMe SSD"],
                "explanation": "Register เป็นหน่วยความจำขนาดเล็กพิเศษที่อยู่ใน CPU จึงมีความเร็วสูงที่สุดในระบบคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "สัญญาณเสียง 'Beep Codes' ตอนเปิดเครื่องคอมพิวเตอร์ เกิดขึ้นจากการตรวจสอบของสิ่งใด?",
                "correct": "POST (Power-On Self-Test)", "distractors": ["Windows Defender", "Task Manager", "DirectX"],
                "explanation": "POST ทำการตรวจสอบฮาร์ดแวร์พื้นฐานก่อนบูต หากชิ้นส่วนใดขัดข้องจะส่งเสียงเตือน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ชิปความปลอดภัย 'TPM 2.0' (Trusted Platform Module) มีหน้าที่หลักคืออะไร?",
                "correct": "เข้ารหัสและเก็บกุญแจความปลอดภัยระดับฮาร์ดแวร์", "distractors": ["เพิ่มความเร็วสัญญาณ Wi-Fi", "สำรองข้อมูลรูปภาพอัตโนมัติ", "ควบคุมไฟ RGB ในเคส"],
                "explanation": "TPM ให้การเข้ารหัสฮาร์ดแวร์เพื่อปกป้องข้อมูลและการบูตระบบอย่างปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ถ่านกระดุมกลมแบน (CR2032) บนเมนบอร์ดมีหน้าที่สำคัญอะไร?",
                "correct": "จ่ายไฟเลี้ยงนาฬิกา RTC และจำค่าไบออส", "distractors": ["จ่ายไฟให้พัดลมระบายความร้อน", "ช่วยเพิ่มความเร็วอินเทอร์เน็ต", "สำรองไฟหน้าจอเวลาไฟดับ"],
                "explanation": "แบตเตอรี่ CMOS เลี้ยงวงจรนาฬิกา Real-Time Clock และรักษาค่าการตั้งค่า BIOS เมื่อปิดเครื่อง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "กลไก 'Thermal Throttling' ของคอมพิวเตอร์ทำงานเพื่ออะไร?",
                "correct": "ลดความเร็ว CPU เมื่อร้อนเกินเพื่อป้องกันชิปพัง", "distractors": ["เร่งความเร็วพัดลมจนสุดตลอดเวลา", "ตัดสัญญาณอินเทอร์เน็ตทันที", "ลบไฟล์ที่ไม่จำเป็นทิ้ง"],
                "explanation": "Thermal Throttling ลดสัญญาณนาฬิกาอัตโนมัติเมื่ออุณหภูมิสูงเกินขีดจำกัดเพื่อป้องกันฮาร์ดแวร์เสียหาย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "สล็อตเชื่อมต่อ 'PCIe 4.0 x16' บนเมนบอร์ด นิยมใช้ติดตั้งอุปกรณ์ใด?",
                "correct": "การ์ดจอแยก (Graphics Card)", "distractors": ["แผงแรม (RAM)", "พาวเวอร์ซัพพลาย", "ซีพียู (CPU)"],
                "explanation": "ช่อง PCIe x16 ให้แบนด์วิดท์ส่งข้อมูลมหาศาล เหมาะที่สุดสำหรับการ์ดแสดงผลความเร็วสูง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ในระบบปฏิบัติการ สภาวะ 'Deadlock' (การติดตาย) เกิดจากสาเหตุใด?",
                "correct": "กระบวนการรอแย่งทรัพยากรซึ่งกันและกันจนค้าง", "distractors": ["ไวรัสลบไฟล์ระบบทั้งหมด", "ฮาร์ดดิสก์เต็ม 100%", "พัดลมหยุดหมุน"],
                "explanation": "Deadlock เกิดขึ้นเมื่อ 2 กระบวนการต่างถือครองทรัพยากรและรออีกฝ่ายปล่อย ทำให้ระบบค้างสนิท"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "เหตุการณ์ 'Page Fault' ในระบบปฏิบัติการเกิดขึ้นเมื่อใด?",
                "correct": "ข้อมูลที่โปรเซสต้องการยังไม่ได้โหลดเข้า RAM", "distractors": ["เปิดหน้าเว็บเบราว์เซอร์ไม่ติด", "พิมพ์งานแล้วกระดาษติดเครื่องพิมพ์", "สายแลนหลุดจากเครื่อง"],
                "explanation": "Page Fault แจ้งเตือนเมื่อข้อมูลที่ระบบเรียกใช้อยู่ใน Virtual Memory บนดิสก์และต้องดึงเข้า RAM"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การทำงานแบบ 'Multithreading' ช่วยให้คอมพิวเตอร์เร็วขึ้นอย่างไร?",
                "correct": "แบ่งงานย่อยให้หลายเธรดทำงานขนานกัน", "distractors": ["เพิ่มกระแสไฟฟ้าให้ซีพียู 2 เท่า", "เชื่อมต่อเน็ต 2 สายพร้อมกัน", "ลบข้อมูลที่ซ้ำซ้อนในดิสก์"],
                "explanation": "Multithreading ช่วยให้หลายงานย่อยภายในโปรแกรมเดียวประมวลผลพร้อมกันได้อย่างมีประสิทธิภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "กลไก 'Mutex' (Mutual Exclusion) ในการเขียนโปรแกรมมีไว้เพื่ออะไร?",
                "correct": "ล็อกไม่ให้หลายเธรดเข้าถึงทรัพยากรพร้อมกัน", "distractors": ["ปิดเสียงไมโครโฟนอัตโนมัติ", "ซ่อนหน้าต่างโปรแกรม", "เชื่อมต่อบลูทูธ"],
                "explanation": "Mutex ป้องกันปัญหา Race Condition โดยอนุญาตให้มีเพียง 1 เธรดเข้าใช้งานทรัพยากรในช่วงเวลาหนึ่ง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "กระบวนการสร้างการเชื่อมต่อของโปรโตคอล TCP เรียกว่าอะไร?",
                "correct": "Three-Way Handshake", "distractors": ["Two-Step Verification", "Direct Connection", "Ping Pong Request"],
                "explanation": "TCP ใช้กระบวนการ 3 ขั้นตอน (SYN, SYN-ACK, ACK) เพื่อยืนยันความพร้อมก่อนเริ่มส่งข้อมูล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "โปรโตคอลเครือข่ายแบบ 'UDP' เหมาะกับงานประเภทใดมากที่สุด?",
                "correct": "สตรีมมิ่งสดและเกมออนไลน์เรียลไทม์", "distractors": ["ส่งไฟล์เอกสารการเงิน", "ดาวน์โหลดไฟล์ติดตั้งโปรแกรม", "การส่งอีเมลสำคัญ"],
                "explanation": "UDP เน้นความเร็วและหน่วงเวลาต่ำโดยไม่ต้องรอตอบรับ เหมาะสำหรับ Voice, Video Streaming และ Gaming"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การแจกหมายเลข IP Address อัตโนมัติในเครือข่าย เป็นหน้าที่ของบริการใด?",
                "correct": "DHCP", "distractors": ["DNS", "FTP", "HTTP"],
                "explanation": "DHCP (Dynamic Host Configuration Protocol) กำหนด IP และค่าเครือข่ายให้อุปกรณ์ใหม่อัตโนมัติ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "หมายเลขพอร์ตมาตรฐาน (Default Port) สำหรับการเชื่อมต่อ 'HTTPS' คือพอร์ตใด?",
                "correct": "443", "distractors": ["80", "21", "22"],
                "explanation": "พอร์ต 443 เป็นพอร์ตมาตรฐานสำหรับเว็บที่มีการเข้ารหัส HTTPS (ส่วน HTTP ทั่วไปคือพอร์ต 80)"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "โปรโตคอลใดใช้ค้นหาหมายเลขประจำฮาร์ดแวร์ (MAC Address) จาก IP Address?",
                "correct": "ARP (Address Resolution Protocol)", "distractors": ["ICMP", "SNMP", "SMTP"],
                "explanation": "ARP ทำหน้าที่สอบถามและจับคู่หมายเลข IP ให้ตรงกับ MAC Address ของอุปกรณ์ในวง LAN"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "เทคโนโลยี 'NAT' (Network Address Translation) บนเราเตอร์มีประโยชน์อย่างไร?",
                "correct": "แปลง Private IP หลายเครื่องออกสู่ 1 Public IP", "distractors": ["เพิ่มความจุของฮาร์ดดิสก์", "เปลี่ยนชื่อคอมพิวเตอร์อัตโนมัติ", "สำรองไฟเมื่อเกิดไฟดับ"],
                "explanation": "NAT ช่วยให้อุปกรณ์นับร้อยเครื่องในบ้านสามารถแชร์ออกสู่อินเทอร์เน็ตผ่าน Public IP เดียวกันได้"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การเข้ารหัสแบบ 'Asymmetric Encryption' (กุญแจอสมมาตร) ใช้สิ่งใดในการทำงาน?",
                "correct": "กุญแจคู่ Public Key และ Private Key", "distractors": ["กุญแจเดอกเดียวกันทั้งสองฝั่ง", "รหัสผ่านตัวเลข 4 หลัก", "การพิมพ์ลายนิ้วมือ"],
                "explanation": "Asymmetric Encryption ใช้ Public Key ในการเข้ารหัส และต้องใช้ Private Key คู่กันในการถอดรหัส"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ฟังก์ชันแฮชทางความปลอดภัย (เช่น SHA-256) มีคุณสมบัติสำคัญข้อใด?",
                "correct": "คำนวณทางเดียว ไม่สามารถแปลงกลับเป็นข้อมูลเดิมได้", "distractors": ["ขยายขนาดไฟล์ให้ใหญ่ขึ้น", "กู้คืนรหัสผ่านกลับมาได้เสมอ", "บีบอัดไฟล์เพลงให้เล็กลง"],
                "explanation": "Cryptographic Hash เป็นฟังก์ชันทางเดียว (One-Way) เหมาะสำหรับตรวจสอบความถูกต้องและเก็บรหัสผ่าน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การโจมตีแบบ 'SQL Injection' เกิดจากช่องโหว่ประเภทใด?",
                "correct": "การไม่ตรวจสอบและกรองข้อความ Input จากผู้ใช้", "distractors": ["สายแลนชำรุดเสียหาย", "การตั้งรหัสผ่านยาวเกินไป", "เปิดคอมพิวเตอร์ทิ้งไว้นาน"],
                "explanation": "SQL Injection เกิดเมื่อแฮกเกอร์แทรกคำสั่ง SQL ผ่านช่องกรอกข้อมูลเข้าสู่ฐานข้อมูลโดยตรง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ช่องโหว่ความปลอดภัยที่ถูกโจมตีก่อนที่ผู้พัฒนาจะปล่อยแพตช์แก้ไข เรียกว่าอะไร?",
                "correct": "Zero-Day Exploit", "distractors": ["Brute Force", "Spyware", "Phishing"],
                "explanation": "Zero-Day คือช่องโหว่สดใหม่ที่ผู้พัฒนายังไม่มีแพตช์ป้องกัน ทำให้มีความเสี่ยงสูงมาก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "การโจมตีแบบ 'Man-in-the-Middle' (MitM) มีลักษณะพฤติกรรมอย่างไร?",
                "correct": "แอบดักจับและแก้ไขข้อมูลระหว่างผู้ส่งและผู้รับ", "distractors": ["ทำลายชิ้นส่วนฮาร์ดแวร์ในเครื่อง", "ขโมยจอภาพไปจากโต๊ะทำงาน", "ส่งอีเมลโฆษณาสินค้า"],
                "explanation": "MitM คือการที่ผู้โจมตีแทรกตัวอยู่กึ่งกลางการสื่อสารเพื่อดักฟังหรือปลอมแปลงข้อมูล"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "ระบบไฟล์แบบ 'NTFS' บน Windows เหนือกว่า 'FAT32' ในเรื่องใด?",
                "correct": "รองรับไฟล์ขนาดเกิน 4GB และมีความปลอดภัยสูง", "distractors": ["เล่นเกมได้เฟรมเรตสูงขึ้น 2 เท่า", "ไม่ต้องเสียบไฟเลี้ยงฮาร์ดดิสก์", "เปลี่ยนสีโฟลเดอร์ได้อัตโนมัติ"],
                "explanation": "FAT32 จำกัดขนาดไฟล์ไม่เกิน 4GB ส่วน NTFS รองรับไฟล์ขนาดใหญ่มากและมีระบบสิทธิ์ความปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "รหัสสถานะ HTTP Code '404 Not Found' มีความหมายว่าอย่างไร?",
                "correct": "ไม่พบหน้าเว็บหรือไฟล์ที่ต้องการบนเซิร์ฟเวอร์", "distractors": ["เซิร์ฟเวอร์กำลังถูกปิดปรับปรุง", "การส่งข้อมูลสำเร็จเรียบร้อย", "รหัสผ่านไม่ถูกต้อง"],
                "explanation": "HTTP 404 บ่งชี้ว่า Client เชื่อมต่อไปยังเซิร์ฟเวอร์ได้ แต่ไม่พบหน้าเว็บ (URL) ตามที่ระบุ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก",
                "text": "สถาปัตยกรรมชุดคำสั่งแบบ 'RISC' (เช่น ชิป ARM) มีจุดเด่นอย่างไรเมื่อเทียบกับ CISC?",
                "correct": "คำสั่งเรียบง่าย ประหยัดพลังงาน และประมวลผลเร็ว", "distractors": ["มีขนาดตัวชิปหนักกว่า 5 เท่า", "ต้องใช้น้ำหล่อเย็นตลอดเวลา", "ไม่สามารถเขียนโค้ดสั่งการได้"],
                "explanation": "RISC ใช้ชุดคำสั่งสั้นและง่าย ช่วยลดความซับซ้อนของวงจร กินไฟน้อย และนิยมอย่างยิ่งในสมาร์ตโฟน"
            },

            # =========================================================================
            # [หมวด: สาขาวิทยาการคอมพิวเตอร์เบื้องต้น] - เดิม 10 ข้อ
            # =========================================================================
            {
                "category": cat_cs, "difficulty": "ง่าย",
                "text": "สาขาวิทยาการคอมพิวเตอร์ (Computer Science) เรียนเน้นเรื่องอะไร?",
                "correct": "เขียนโค้ด สร้างเกม เว็บ และ AI", "distractors": ["ซ่อมพัดลมและเดินสายไฟ", "พิมพ์ดีดเอกสารอย่างเดียว", "เล่นเกมไม่ต้องเรียน"],
                "explanation": "วิทยาการคอมพิวเตอร์ (CS) เรียนการคิดเป็นระบบ เขียนโค้ด สร้างเกม เว็บไซต์ และนวัตกรรม AI"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย",
                "text": "โปรแกรมต่อบล็อกคำสั่งสีสันสดใสที่เด็ก ๆ นิยมใช้ฝึกสร้างเกมคือโปรแกรมใด?",
                "correct": "Scratch", "distractors": ["Excel", "Word", "Calculator"],
                "explanation": "Scratch เป็นโปรแกรมเขียนโค้ดแบบต่อบล็อกที่สนุกและเข้าใจง่ายสำหรับน้อง ๆ"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย",
                "text": "คำว่า 'อัลกอริทึม' (Algorithm) หมายถึงอะไร?",
                "correct": "ลำดับขั้นตอนการแก้ปัญหา", "distractors": ["ชื่อยี่ห้อคอมพิวเตอร์", "ภาษาต่างดาว", "ชื่อตัวละครในเกม"],
                "explanation": "Algorithm คือลำดับขั้นตอนที่ชัดเจนในการแก้ปัญหาทีละสเต็ป"
            },
            {
                "category": cat_cs, "difficulty": "ง่าย",
                "text": "ในวงการเขียนโปรแกรม หากโค้ดทำงานผิดพลาด เราจะเรียกข้อผิดพลาดนั้นว่าอะไร?",
                "correct": "บั๊ก (Bug)", "distractors": ["มด (Ant)", "นก (Bird)", "ปลา (Fish)"],
                "explanation": "Bug หมายถึงจุดบกพร่องหรือข้อผิดพลาดในโปรแกรมคอมพิวเตอร์"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง",
                "text": "ภาษาเขียนโปรแกรมยอดนิยมที่มีโลโก้รูป 'งู' และอ่านเข้าใจง่ายคือภาษาใด?",
                "correct": "Python (ไพทอน)", "distractors": ["Photoshop", "PowerPoint", "Paint"],
                "explanation": "Python เป็นภาษาเขียนโปรแกรมที่อ่านง่ายและนิยมใช้สร้าง AI มากที่สุด"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง",
                "text": "อาชีพใดเป็นสายงานตรงของคนที่จบสาขาวิทยาการคอมพิวเตอร์?",
                "correct": "โปรแกรมเมอร์และนักสร้างเกม", "distractors": ["ช่างซ่อมมอเตอร์ไซค์", "คนขับรถบรรทุก", "พนักงานพิมพ์ดีด"],
                "explanation": "บัณฑิต CS สามารถเป็นนักพัฒนาซอฟต์แวร์ ผู้สร้างเกม และผู้เชี่ยวชาญด้านข้อมูล/AI"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง",
                "text": "คำสั่ง 'If...Else' ในการเขียนโปรแกรม มีไว้ใช้ทำอะไร?",
                "correct": "เช็คเงื่อนไขเพื่อตัดสินใจ", "distractors": ["การวนทำซ้ำไม่รู้จบ", "ปิดเครื่องคอมพิวเตอร์", "ลบโค้ดทิ้ง"],
                "explanation": "If-Else ใช้ตรวจสอบเงื่อนไข เช่น 'ถ้าคะแนนถึง 50 ให้ผ่าน มิฉะนั้น ให้ปรับปรุง'"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง",
                "text": "คำสั่งประเภท 'Loop' ในการเขียนโปรแกรมมีประโยชน์อย่างไร?",
                "correct": "ทำงานซ้ำตามรอบที่สั่ง", "distractors": ["เปิดเพลงวนซ้ำ", "สุ่มตัวเลข", "ปิดหน้าต่างโปรแกรม"],
                "explanation": "Loop หรือการวนซ้ำ ใช้สั่งให้คอมพิวเตอร์ทำงานเดิมซ้ำ ๆ โดยไม่ต้องเขียนโค้ดซ้ำหลายบรรทัด"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "โครงสร้างข้อมูลแบบ 'Stack' (สแต็ก) มีหลักการทำงานคล้ายสิ่งใด?",
                "correct": "กองจานซ้อนกัน (ใบบนออกก่อน)", "distractors": ["การต่อแถวซื้อขนม", "การโยนเหรียญ", "การหมุนวงล้อ"],
                "explanation": "Stack ทำงานแบบ LIFO (Last-In First-Out) เปรียบเหมือนกองจานที่ใบบนสุดจะถูกหยิบออกก่อน"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "สาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยราชภัฏศรีสะเกษ มีตัวย่อว่าอะไร?",
                "correct": "CS (Computer Science)", "distractors": ["AI", "IT", "SE"],
                "explanation": "CS ย่อมาจาก Computer Science คือสาขาวิชาวิทยาการคอมพิวเตอร์ มรภ.ศรีสะเกษ"
            },

            # =========================================================================
            # [หมวด: สาขาวิทยาการคอมพิวเตอร์] - ระดับยาก (เพิ่มใหม่อีก 25 ข้อ)
            # =========================================================================
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ประสิทธิภาพเชิงเวลา (Time Complexity) ของอัลกอริทึม 'Binary Search' คือเท่าใด?",
                "correct": "O(log n)", "distractors": ["O(n^2)", "O(n)", "O(1)"],
                "explanation": "Binary Search แบ่งข้อมูลออกเป็นครึ่งหนึ่งในแต่ละรอบ จึงมี Time Complexity เท่ากับ O(log n)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "โครงสร้างข้อมูลแบบ 'Queue' (คิว) ทำงานตามหลักการใด?",
                "correct": "FIFO (First-In, First-Out เข้าก่อนออกก่อน)", "distractors": ["LIFO (Last-In, First-Out)", "Random In, Random Out", "Priority Only"],
                "explanation": "Queue ทำงานแบบ FIFO เสมือนการเข้าแถวซื้อบัตร คนที่มาก่อนจะได้รับการบริการก่อน"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ข้อผิดพลาดแบบ 'Stack Overflow' ในการเขียนโปรแกรมมักเกิดจากสาเหตุใด?",
                "correct": "การเรียกฟังก์ชันซ้ำตัวเอง (Recursion) ไม่รู้จบ", "distractors": ["หน่วยความจำฮาร์ดดิสก์เต็ม", "ประกาศตัวแปรมากเกินไปในหน้าเดียว", "การใช้ตัวพิมพ์เล็กพิมพ์ใหญ่ผิด"],
                "explanation": "การเรียก Recursive Function โดยไม่มี Base Case หรือไม่สิ้นสุด จะทำให้ Call Stack เต็มจนเกิด Stack Overflow"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "อัลกอริทึมจัดเรียงข้อมูลแบบใดมี Time Complexity เฉลี่ยดีที่สุด O(n log n)?",
                "correct": "Merge Sort / Quick Sort", "distractors": ["Bubble Sort", "Insertion Sort", "Selection Sort"],
                "explanation": "Merge Sort และ Quick Sort ใช้วิธี Divide and Conquer มีประสิทธิภาพระดับ O(n log n)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "โครงสร้างข้อมูล 'Hash Table' มีความเร็วในการค้นหาข้อมูลโดยเฉลี่ยระดับใด?",
                "correct": "O(1) ค่าคงที่", "distractors": ["O(n)", "O(n^2)", "O(log n)"],
                "explanation": "Hash Table ใช้ Hash Function แปลงคีย์เป็นดัชนี จึงเข้าถึงข้อมูลได้ทันทีในระดับ O(1)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ใน OOP (เชิงวัตถุ) คุณสมบัติ 'Polymorphism' หมายถึงอะไร?",
                "correct": "อ็อบเจกต์ต่างคลาสสามารถตอบสนองต่อเมธอดชื่อเดียวกันได้หลากหลาย", "distractors": ["การสืบทอดตัวแปรจากคลาสแม่เพียงอย่างเดียว", "การซ่อนโค้ดไม่ให้ใครมองเห็น", "การทำให้โปรแกรมรันเร็วขึ้น 10 เท่า"],
                "explanation": "Polymorphism (พหุสัณฐาน) อนุญาตให้เมธอดชื่อเดียวกันทำงานตามพฤติกรรมเฉพาะของแต่ละคลาสย่อย"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ใน OOP คุณสมบัติ 'Encapsulation' (การห่อหุ้ม) มีจุดประสงค์หลักเพื่ออะไร?",
                "correct": "ซ่อนรายละเอียดและป้องกันการแก้ไขข้อมูลภายในโดยตรง", "distractors": ["รวมไฟล์โค้ดทั้งหมดเป็นไฟล์เดียว", "การแปลงโค้ดเป็นภาษาไบนารี", "เพิ่มความเร็วในการเชื่อมต่อเน็ต"],
                "explanation": "Encapsulation ซ่อนสถานะภายในอ็อบเจกต์ และให้เข้าถึงผ่าน Getter/Setter ที่ปลอดภัย"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "โปรแกรม 'Compiler' แตกต่างจาก 'Interpreter' อย่างไร?",
                "correct": "Compiler แปลงโค้ดทั้งหมดเป็นภาษาเครื่องก่อนรันทีเดียว", "distractors": ["Compiler รันโค้ดทีละบรรทัดช้ากว่า", "Compiler ใช้สำหรับวาดรูปเท่านั้น", "Interpreter แปลงภาษาได้เฉพาะภาษา C"],
                "explanation": "Compiler (เช่น C/C++, Rust) คอมไพล์โค้ดทั้งชุด ส่วน Interpreter (เช่น Python) แปลและรันทีละบรรทัด"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ระบบ 'Garbage Collection' ในภาษาโปรแกรมทำหน้าที่อะไร?",
                "correct": "ตรวจจับและคืนหน่วยความจำที่ไม่ได้ใช้งานแล้วอัตโนมัติ", "distractors": ["ลบไวรัสและไฟล์ขยะในระบบปฏิบัติการ", "จัดเรียงโค้ดให้สวยงามตามมาตรฐาน", "ลบประวัติการแชททั้งหมด"],
                "explanation": "Garbage Collector คอยจัดการคืน Memory จากอ็อบเจกต์ที่ไม่มีการอ้างอิงถึง เพื่อป้องกัน Memory Leak"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "คำสั่งใน Git ข้อใดใช้สำหรับรวมประวัติโค้ดจาก Branch อื่นเข้ามาใน Branch ปัจจุบัน?",
                "correct": "git merge", "distractors": ["git commit", "git push", "git clone"],
                "explanation": "git merge ใช้ผสานการเปลี่ยนแปลงและประวัติการพัฒนาจากกิ่งต้นทางมารวมไว้ด้วยกัน"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "มาตรฐานการส่งข้อมูลแบบ 'JSON' ย่อมาจากคำว่าอะไร?",
                "correct": "JavaScript Object Notation", "distractors": ["Java Standard Online Network", "Joint System Output Node", "JavaScript Open Navigation"],
                "explanation": "JSON เป็นรูปแบบแลกเปลี่ยนข้อมูลแบบข้อความที่อ่านเข้าใจง่ายและนิยมใช้ใน Web API ทั่วโลก"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ในฐานข้อมูลเชิงสัมพันธ์ คีย์ที่ใช้อ้างอิงเชื่อมโยงไปยังตารางอื่นเรียกว่าอะไร?",
                "correct": "Foreign Key (คีย์นอก)", "distractors": ["Primary Key (คีย์หลัก)", "Candidate Key", "Super Key"],
                "explanation": "Foreign Key เป็นฟิลด์ที่ชี้ไปยัง Primary Key ของอีกตารางเพื่อสร้างความสัมพันธ์ระหว่างข้อมูล"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "คุณสมบัติ 'ACID' ของฐานข้อมูล ตัวอักษร 'A' ย่อมาจากคำว่าอะไร?",
                "correct": "Atomicity (ทำสำเร็จครบทุกขั้นตอนหรือไม่ทำเลย)", "distractors": ["Availability", "Accuracy", "Automation"],
                "explanation": "Atomicity รับประกันว่าทุกการกระทำใน Transaction ต้องสำเร็จครบถ้วน หากมีจุดใดพลาดจะยกเลิกทั้งหมด (Rollback)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ฐานข้อมูลแบบ 'NoSQL' (เช่น MongoDB) เหมาะกับข้อมูลลักษณะใด?",
                "correct": "ข้อมูลที่ยืดหยุ่น ไร้โครงสร้าง หรือมี Schema ไม่ตายตัว", "distractors": ["ข้อมูลตารางบัญชีการเงินที่เข้มงวด", "ข้อมูลที่ไม่ต้องการบันทึกลงดิสก์", "ข้อมูลตัวเลขฐานสอง 0 และ 1 เท่านั้น"],
                "explanation": "NoSQL ออกแบบมาเพื่อรองรับข้อมูลแบบ Unstructured / Semi-Structured และขยายขนาดแบบ Scale-out ได้ดี"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "เทคโนโลยี 'Docker Container' มีข้อได้เปรียบเหนือ 'Virtual Machine (VM)' อย่างไร?",
                "correct": "แชร์ OS Kernel ร่วมกัน ทำให้บูตเร็วและกินทรัพยากรน้อยกว่า", "distractors": ["จำลองระบบปฏิบัติการได้สมบูรณ์กว่า", "ไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ต", "ใช้งานได้เฉพาะบนระบบ Windows"],
                "explanation": "Container ทำงานแบบ Lightweight โดยแชร์ Kernel ร่วมกัน จึงใช้เนื้อที่และแรมลดลงอย่างมาก"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "บริการคลาวด์แบบ 'IaaS' (เช่น AWS EC2, Google Compute Engine) ให้บริการสิ่งใด?",
                "correct": "โครงสร้างพื้นฐานเสมือน เช่น CPU, RAM, Storage และ Network", "distractors": ["ซอฟต์แวร์สำเร็จรูปพร้อมใช้งานผ่านเว็บ", "แพลตฟอร์มเขียนโค้ดและรันฐานข้อมูล", "บริการดูแลและซ่อมแซมคอมพิวเตอร์ที่บ้าน"],
                "explanation": "IaaS (Infrastructure as a Service) ให้อำนาจผู้ใช้จัดการเครื่องเซิร์ฟเวอร์เสมือนและระบบเครือข่ายอย่างอิสระ"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ในกระบวนการ DevOps คำว่า 'CI' ใน CI/CD ย่อมาจากอะไร?",
                "correct": "Continuous Integration", "distractors": ["Computer Intelligence", "Cloud Infrastructure", "Code Information"],
                "explanation": "CI (Continuous Integration) คือการผสานโค้ดเข้าสู่คลังหลักอย่างสม่ำเสมอพร้อมรัน Automated Test ตรวจสอบ"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "ใน Machine Learning ปัญหา 'Overfitting' มีลักษณะอย่างไร?",
                "correct": "โมเดลจำข้อมูลที่ใช้สอนได้ดีเกินไป แต่ทำนายข้อมูลใหม่ได้แย่", "distractors": ["โมเดลคำนวณช้าจนระบบค้าง", "ชุดข้อมูลมีขนาดเล็กเกินไปจนเทรนไม่ได้", "โมเดลทำนายได้ถูกต้อง 100% กับทุกข้อมูล"],
                "explanation": "Overfitting เกิดเมื่อโมเดลซับซ้อนเกินไปจนจดจำ Noise ใน Training Data ทำให้ Generalize กับข้อมูลจริงได้ไม่ดี"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "เครือข่ายประสาทเทียม (Artificial Neural Network) ได้รับแรงบันดาลใจจากอะไร?",
                "correct": "การทำงานของเซลล์ประสาทในสมองมนุษย์", "distractors": ["การไหลเวียนของกระแสน้ำในแม่น้ำ", "โครงสร้างของต้นไม้และใบไม้", "ระบบทางหลวงและการจราจร"],
                "explanation": "Neural Network จำลองการรับส่งสัญญาณของเซลล์ประสาท (Neurons) ผ่านค่าน้ำหนัก (Weights)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "โมเดลภาษาขนาดใหญ่ (LLM) เช่น ChatGPT หรือ Gemini พัฒนาบนสถาปัตยกรรมใด?",
                "correct": "Transformer Architecture", "distractors": ["Decision Tree", "Linear Regression", "Bubble Algorithm"],
                "explanation": "Transformer ใช้กลไก Self-Attention ในการทำความเข้าใจความสัมพันธ์ของคำในประโยคได้อย่างมีประสิทธิภาพสูง"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "การเรียนรู้ของเครื่องแบบ 'Supervised Learning' จำเป็นต้องมีสิ่งใดในการฝึก?",
                "correct": "ชุดข้อมูลนำเข้าพร้อมคำตอบเฉลย (Labeled Data)", "distractors": ["การปล่อยให้โมเดลลองผิดลองถูกเองทั้งหมด", "การเชื่อมต่อกับกล้องวงจรปิด", "การใช้หุ่นยนต์ช่วยพิมพ์"],
                "explanation": "Supervised Learning เป็นการสอนโมเดลโดยใช้ตัวอย่างที่มีทั้ง Input (ข้อมูล) และ Output (เฉลยที่ถูกต้อง)"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "เทคโนโลยี 'Blockchain' มีจุดเด่นสำคัญที่สุดในข้อใด?",
                "correct": "เป็นบัญชีแยกประเภทกระจายศูนย์ที่แก้ไขย้อนหลังไม่ได้", "distractors": ["พิมพ์เงินสดออกมาได้อัตโนมัติ", "ส่งข้อความได้โดยไม่ต้องใช้อินเทอร์เน็ต", "เพิ่มความเร็วสัญญาณมือถือ 5G"],
                "explanation": "Blockchain เป็น Distributed Ledger ที่ใช้การเข้ารหัสและการเห็นพ้อง (Consensus) เพื่อความโปร่งใสและแก้ไขไม่ได้"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "หน่วยข้อมูลพื้นฐานของคอมพิวเตอร์ควอนตัม (Quantum Computer) เรียกว่าอะไร?",
                "correct": "คิวบิต (Qubit)", "distractors": ["บิต (Bit)", "ไบต์ (Byte)", "พิกเซล (Pixel)"],
                "explanation": "Qubit สามารถอยู่ในสถานะซ้อนทับ (Superposition) ทั้ง 0 และ 1 พร้อมกันได้ ทำให้ประมวลผลเร็วมหาศาล"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "รหัสสถานะ HTTP Code '500 Internal Server Error' บ่งบอกถึงสิ่งใด?",
                "correct": "เซิร์ฟเวอร์เกิดข้อผิดพลาดในการประมวลผลโค้ดฝั่ง Backend", "distractors": ["ผู้ใช้งานไม่ได้ล็อกอินเข้าระบบ", "สัญญาณ Wi-Fi ที่บ้านหลุด", "พิมพ์ URL เว็บไซต์ผิด"],
                "explanation": "HTTP 500 เกิดเมื่อสคริปต์หรือโปรแกรมฝั่งเซิร์ฟเวอร์เกิด Exception หรือข้อผิดพลาดจนไม่สามารถส่งหน้าเว็บได้"
            },
            {
                "category": cat_cs, "difficulty": "ยาก",
                "text": "กระบวนการพัฒนาซอฟต์แวร์แบบ 'Agile' เน้นการทำงานในลักษณะใด?",
                "correct": "ยืดหยุ่น ปรับเปลี่ยนตามความต้องการ และส่งมอบงานเป็นรอบสั้น ๆ (Sprints)", "distractors": ["วางแผนครั้งเดียว 2 ปีโดยห้ามแก้ไขอะไรเลย", "ทำงานคนเดียวโดยไม่ปรึกษาทีม", "เขียนเอกสารรายงานหนา 500 หน้าก่อนเริ่มเขียนโค้ด"],
                "explanation": "Agile เน้นการปรับตัวที่รวดเร็ว การสื่อสารในทีม และการส่งมอบซอฟต์แวร์ที่ใช้งานได้จริงในระยะเวลาสั้น ๆ"
            },
        ]

        # 6. สุ่มกระจายตัวเลือก A, B, C, D อย่างทั่วถึงและยุติธรรม (ไม่ให้ข้อ A ถูกอย่างเดียว)
        # ใช้ Random Seed เพื่อความแน่นอนในการทดสอบ แต่กระจายตำแหน่งเฉลยให้เท่า ๆ กัน
        rng = random.Random(2026)
        prepared_questions = []

        letters = ["A", "B", "C", "D"]
        distribution_counts = {"A": 0, "B": 0, "C": 0, "D": 0}

        for item in raw_items:
            choices = [item["correct"]] + list(item["distractors"])
            rng.shuffle(choices)
            correct_index = choices.index(item["correct"])
            correct_letter = letters[correct_index]
            distribution_counts[correct_letter] += 1

            prepared_questions.append({
                "category": item["category"],
                "text": item["text"],
                "choice_a": choices[0],
                "choice_b": choices[1],
                "choice_c": choices[2],
                "choice_d": choices[3],
                "correct_choice": correct_letter,
                "explanation": item.get("explanation", ""),
                "difficulty": item["difficulty"],
                "is_active": True,
            })

        self.stdout.write(self.style.NOTICE(
            f"กระจายเฉลยตัวเลือกสำเร็จ: A={distribution_counts['A']}, B={distribution_counts['B']}, "
            f"C={distribution_counts['C']}, D={distribution_counts['D']}"
        ))

        # 7. บันทึกคำถามลงใน SQLite
        self.stdout.write(self.style.NOTICE(f"3. บันทึกคำถาม {len(prepared_questions)} ข้อลง SQLite..."))
        created_questions = []
        for i, q_data in enumerate(prepared_questions, start=1):
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

        # 8. ซิงค์ไปยัง Firebase Firestore แบบขนาน
        self.stdout.write(self.style.NOTICE(f"4. ซิงค์คำถาม {success_db} ข้อไปยัง Firebase Firestore..."))
        with ThreadPoolExecutor(max_workers=15) as executor:
            sync_results = list(executor.map(sync_question_to_firestore, created_questions))
            success_fb = sum(1 for r in sync_results if r)
        self.stdout.write(self.style.SUCCESS(f"[OK] ซิงค์ขึ้น Firebase Firestore สำเร็จ ({success_fb}/{success_db} ข้อ)"))

        # สรุปผล
        easy_count = sum(1 for q in prepared_questions if q["difficulty"] == "ง่าย")
        medium_count = sum(1 for q in prepared_questions if q["difficulty"] == "ปานกลาง")
        hard_count = sum(1 for q in prepared_questions if q["difficulty"] == "ยาก")
        cat1_count = sum(1 for q in prepared_questions if q["category"] == cat_basic)
        cat2_count = sum(1 for q in prepared_questions if q["category"] == cat_cs)

        self.stdout.write(self.style.SUCCESS(f"\n======================================================="))
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] สร้างชุดคำถาม 150 ข้อ พร้อมสุ่มเฉลย A-D สำเร็จ 100%!"))
        self.stdout.write(self.style.SUCCESS(f"  - บันทึกลง SQLite: {success_db}/{len(prepared_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - ซิงค์ขึ้น Firebase: {success_fb}/{len(prepared_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - สถิติระดับความยาก: ง่าย {easy_count} ข้อ, ปานกลาง {medium_count} ข้อ, ยาก {hard_count} ข้อ (เพิ่มข้อยากใหม่อีก 50 ข้อ)"))
        self.stdout.write(self.style.SUCCESS(f"  - สถิติเฉลยตัวเลือก: A={distribution_counts['A']}, B={distribution_counts['B']}, C={distribution_counts['C']}, D={distribution_counts['D']}"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวด {cat_basic.name}: {cat1_count} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวด {cat_cs.name}: {cat2_count} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - รวมทั้งหมด: {len(prepared_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"======================================================="))
