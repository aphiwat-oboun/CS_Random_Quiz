from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from my_app.models import Category, Question, QuizLog
from my_app.firebase_config import sync_question_to_firestore, delete_question_from_firestore, fetch_all_questions_from_firestore


class Command(BaseCommand):
    help = "ลบคำถามเดิมทั้งหมดและสร้างคำถามใหม่ 100 ข้อ (คอมพิวเตอร์เบื้องต้น: ง่าย 40, ปานกลาง 25, ยาก 25 และ สาขาวิทยาการคอมพิวเตอร์เบื้องต้น 10 ข้อ) พร้อมซิงค์เข้า Firebase Firestore"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("=== เริ่มกระบวนการล้างข้อมูลเดิมและสร้างชุดคำถามใหม่ 100 ข้อ ==="))

        # 1. เคลียร์คำถามเดิมทั้งหมดบน Firebase Firestore
        try:
            self.stdout.write(self.style.NOTICE("1. กำลังเคลียร์คำถามเดิมบน Firebase Firestore..."))
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
            color="#0ea5e9"  # สีฟ้าสดใส
        )
        cat_cs = Category.objects.create(
            name="สาขาวิทยาการคอมพิวเตอร์เบื้องต้น",
            color="#8b5cf6"  # สีม่วงเทคโนโลยี
        )
        self.stdout.write(self.style.SUCCESS("[OK] สร้าง 2 หมวดหมู่เรียบร้อย:"))
        self.stdout.write(f"  - หมวด 1: {cat_basic.name} (90 ข้อ)")
        self.stdout.write(f"  - หมวด 2: {cat_cs.name} (10 ข้อ)")

        # 5. เตรียมชุดคำถาม 100 ข้อ
        raw_questions = [
            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับง่าย (EASY) 40 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดทำหน้าที่เหมือน 'หนู' ใช้สำหรับเลื่อนเคอร์เซอร์และคลิกเลือกสิ่งต่าง ๆ บนหน้าจอคอมพิวเตอร์?",
                "choice_a": "เมาส์ (Mouse)", "choice_b": "คีย์บอร์ด (Keyboard)", "choice_c": "จอภาพ (Monitor)", "choice_d": "พัดลมระบายความร้อน (Cooling Fan)",
                "correct_choice": "A", "explanation": "เมาส์ (Mouse) เป็นอุปกรณ์ชี้ตำแหน่ง (Pointing Device) ที่ใช้สั่งการและคลิกเลือกเมนูบนจอภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพิมพ์ตัวอักษรหรือข้อความเข้าสู่เครื่องคอมพิวเตอร์ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "เครื่องพิมพ์ (Printer)", "choice_b": "แป้นพิมพ์ / คีย์บอร์ด (Keyboard)", "choice_c": "เครื่องสแกนเนอร์ (Scanner)", "choice_d": "ลำโพง (Speaker)",
                "correct_choice": "B", "explanation": "คีย์บอร์ด (Keyboard) ทำหน้าที่รับข้อมูลตัวอักษร ตัวเลข และสัญลักษณ์เพื่อป้อนเข้าสู่ระบบคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัดมาตรฐาน 'Ctrl + C' บนคีย์บอร์ดมีหน้าที่อะไร?",
                "choice_a": "คัดลอก (Copy)", "choice_b": "ตัดข้อความ (Cut)", "choice_c": "วางข้อมูล (Paste)", "choice_d": "ปิดโปรแกรม (Close)",
                "correct_choice": "A", "explanation": "Ctrl + C เป็นคีย์ลัดสากลสำหรับคำสั่ง Copy (คัดลอกข้อความหรือไฟล์)"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + V' ใช้งานคู่กับ Ctrl + C เพื่อทำหน้าที่ใด?",
                "choice_a": "ลบไฟล์", "choice_b": "บันทึกเอกสาร", "choice_c": "วางข้อมูลที่คัดลอกไว้ (Paste)", "choice_d": "เปิดไฟล์ใหม่",
                "correct_choice": "C", "explanation": "Ctrl + V ใช้สำหรับคำสั่ง Paste (วางข้อมูลที่ถูกคัดลอกไว้ลงตำแหน่งที่ต้องการ)"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + Z' มีประโยชน์อย่างไรเมื่อผู้ใช้ทำงานผิดพลาด?",
                "choice_a": "ยกเลิกการกระทำล่าสุด / ย้อนกลับ (Undo)", "choice_b": "ซูมหน้าจอเข้า", "choice_c": "ปิดหน้าต่างทันที", "choice_d": "พิมพ์เอกสารออกเครื่องพิมพ์",
                "correct_choice": "A", "explanation": "Ctrl + Z ใช้สั่ง Undo เพื่อย้อนกลับการกระทำล่าสุดที่เพิ่งทำผิดพลาด"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + S' นิยมกดเป็นประจำขณะพิมพ์งานเพื่อสิ่งใด?",
                "choice_a": "ค้นหาข้อความ", "choice_b": "ปิดคอมพิวเตอร์", "choice_c": "ส่งอีเมล", "choice_d": "บันทึกไฟล์ข้อมูล (Save)",
                "correct_choice": "D", "explanation": "Ctrl + S คือปุ่มลัดสำหรับ Save (บันทึกงาน) ช่วยป้องกันงานสูญหาย"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มยาวที่สุดที่อยู่แถวล่างสุดของคีย์บอร์ดคือปุ่มใดและใช้ทำอะไร?",
                "choice_a": "Spacebar ใช้เว้นวรรคตัวอักษร", "choice_b": "Enter ใช้ขึ้นบรรทัดใหม่", "choice_c": "Shift ใช้พิมพ์ตัวใหญ่", "choice_d": "Tab ใช้ย่อหน้า",
                "correct_choice": "A", "explanation": "Spacebar (สเปซบาร์) เป็นปุ่มที่ยาวที่สุด ใช้สำหรับเว้นวรรคช่องว่างระหว่างข้อความ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มใดบนคีย์บอร์ดที่ใช้สำหรับ 'ยืนยันคำสั่ง' หรือ 'ขึ้นบรรทัดใหม่' ในการพิมพ์งาน?",
                "choice_a": "Esc", "choice_b": "Enter", "choice_c": "Ctrl", "choice_d": "Alt",
                "correct_choice": "B", "explanation": "ปุ่ม Enter ใช้สำหรับตกลง ยืนยันคำสั่ง หรือขึ้นบรรทัดใหม่ในการพิมพ์เอกสาร"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพิมพ์ตัวอักษรภาษาอังกฤษพิมพ์ใหญ่แบบตัวเดียว ต้องกดปุ่มใดค้างไว้พร้อมกับตัวอักษรนั้น?",
                "choice_a": "Ctrl", "choice_b": "Alt", "choice_c": "Shift", "choice_d": "Tab",
                "correct_choice": "C", "explanation": "การกด Shift ค้างไว้จะทำให้พิมพ์ตัวพิมพ์ใหญ่ (Capital Letters) หรือสัญลักษณ์แถวบนของปุ่มได้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่ม 'Caps Lock' มีหน้าที่อะไร?",
                "choice_a": "ล็อกให้พิมพ์ตัวพิมพ์ใหญ่ตลอดเวลา", "choice_b": "ล็อกหน้าจอไม่ให้คนอื่นเข้า", "choice_c": "ล็อกแป้นตัวเลข", "choice_d": "ล็อกเมาส์ให้อยู่กับที่",
                "correct_choice": "A", "explanation": "Caps Lock ช่วยให้พิมพ์ตัวพิมพ์ใหญ่ภาษาอังกฤษได้อย่างต่อเนื่องโดยไม่ต้องกด Shift ค้างไว้"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์คอมพิวเตอร์ชิ้นใดที่เปรียบเหมือน 'สมอง' คอยคำนวณและประมวลผลคำสั่งทั้งหมด?",
                "choice_a": "พาวเวอร์ซัพพลาย (Power Supply)", "choice_b": "ซีพียู (CPU)", "choice_c": "การ์ดเสียง (Sound Card)", "choice_d": "เคสคอมพิวเตอร์ (Case)",
                "correct_choice": "B", "explanation": "CPU (Central Processing Unit) ทำหน้าที่ประมวลผลกลาง เปรียบเหมือนสมองของเครื่องคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการพิมพ์ข้อความและรูปภาพจากหน้าจอออกมาเป็นแผ่นกระดาษ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "เครื่องพิมพ์ (Printer)", "choice_b": "เครื่องสแกนเนอร์ (Scanner)", "choice_c": "จอภาพ (Monitor)", "choice_d": "เมาส์ (Mouse)",
                "correct_choice": "A", "explanation": "เครื่องพิมพ์ (Printer) ทำหน้าที่แสดงผลลัพธ์ข้อมูลดิจิทัลออกมาในรูปแบบเอกสารบนกระดาษ (Hard Copy)"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "หากต้องการสนทนาเสียงหรือบันทึกเสียงพูดเข้าสู่คอมพิวเตอร์ ต้องใช้อุปกรณ์ใด?",
                "choice_a": "ลำโพง", "choice_b": "หูฟัง", "choice_c": "ไมโครโฟน (Microphone)", "choice_d": "เว็บแคม",
                "correct_choice": "C", "explanation": "ไมโครโฟน (Microphone) เป็นอุปกรณ์รับสัญญาณเสียง (Audio Input) เข้าสู่คอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ขนาดเล็กชนิดใดนิยมใช้เสียบพอร์ต USB เพื่อพกพาและถ่ายโอนไฟล์ไปมาระหว่างเครื่อง?",
                "choice_a": "แฟลชไดรฟ์ (USB Flash Drive)", "choice_b": "ซีพียู (CPU)", "choice_c": "แรม (RAM)", "choice_d": "พัดลมซีพียู",
                "correct_choice": "A", "explanation": "USB Flash Drive เป็นหน่วยความจำสำรองแบบพกพาที่ใช้งานสะดวกผ่านพอร์ต USB"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "Google Chrome, Microsoft Edge และ Mozilla Firefox จัดเป็นโปรแกรมประเภทใด?",
                "choice_a": "โปรแกรมตกแต่งภาพ", "choice_b": "โปรแกรมตัดต่อวิดีโอ", "choice_c": "เว็บเบราว์เซอร์ (Web Browser)", "choice_d": "โปรแกรมป้องกันไวรัส",
                "correct_choice": "C", "explanation": "โปรแกรมเหล่านี้คือ Web Browser ที่ใช้สำหรับเปิดดูเว็บไซต์และท่องอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรมใดในชุด Microsoft Office ที่ออกแบบมาสำหรับการพิมพ์เอกสาร จดหมาย และทำรายงาน?",
                "choice_a": "Microsoft Word", "choice_b": "Microsoft Excel", "choice_c": "Microsoft PowerPoint", "choice_d": "Microsoft Access",
                "correct_choice": "A", "explanation": "Microsoft Word เป็นโปรแกรมประมวลผลคำ (Word Processing) เหมาะกับการพิมพ์เอกสารและรายงาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรมใดในชุด Microsoft Office ที่นิยมใช้ทำตารางคำนวณตัวเลขและสร้างแผนภูมิ?",
                "choice_a": "Microsoft Paint", "choice_b": "Microsoft Excel", "choice_c": "Microsoft Word", "choice_d": "Microsoft OneNote",
                "correct_choice": "B", "explanation": "Microsoft Excel เป็นโปรแกรมประเภทสเปรดชีต (Spreadsheet) สำหรับคำนวณตัวเลขและสูตรต่าง ๆ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรมใดที่นิยมใช้สำหรับการออกแบบสไลด์เพื่อนำเสนองานต่อหน้าผู้ชม (Presentation)?",
                "choice_a": "Notepad", "choice_b": "Calculator", "choice_c": "Microsoft PowerPoint", "choice_d": "VLC Media Player",
                "correct_choice": "C", "explanation": "Microsoft PowerPoint ออกแบบมาเพื่อสร้างสไลด์นำเสนอข้อความ รูปภาพ และวิดีโอ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โฟลเดอร์รูปถังขยะ 'Recycle Bin' บน Windows มีประโยชน์หลักอย่างไร?",
                "choice_a": "เก็บไฟล์ที่เพิ่งถูกลบชั่วคราว เพื่อให้สามารถกู้คืนได้", "choice_b": "ใช้ลบไฟล์ระบบทันทีอย่างถาวร", "choice_c": "เก็บไฟล์เพลงและภาพถ่าย", "choice_d": "ใช้ทำความสะอาดหน้าจอภาพ",
                "correct_choice": "A", "explanation": "Recycle Bin พักไฟล์ที่ถูกสั่งลบไว้ชั่วคราว ทำให้ผู้ใช้สามารถ Restore (กู้คืน) กลับมาได้หากลบผิดพลาด"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มใดบนคีย์บอร์ดที่กดเพื่อลบตัวอักษรที่อยู่ 'ทางซ้าย' ของเคอร์เซอร์?",
                "choice_a": "Backspace", "choice_b": "Delete", "choice_c": "Home", "choice_d": "End",
                "correct_choice": "A", "explanation": "Backspace ลบตัวอักษรที่อยู่หน้า (ซ้าย) เคอร์เซอร์ ส่วนปุ่ม Delete จะลบตัวอักษรที่อยู่หลัง (ขวา) เคอร์เซอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่ม 'Esc' (Escape) บนมุมบนซ้ายของคีย์บอร์ด มักใช้เพื่อทำอะไร?",
                "choice_a": "บันทึกข้อมูล", "choice_b": "ยกเลิกคำสั่งหรือออกจากโหมดเต็มหน้าจอ", "choice_c": "ปิดเครื่องทันที", "choice_d": "สลับภาษา",
                "correct_choice": "B", "explanation": "ปุ่ม Esc ใช้ยกเลิกหน้าต่างป๊อปอัป ออกจากโหมดเต็มหน้าจอ หรือหยุดคำสั่งชั่วคราว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มฟังก์ชัน (Function Key) ใดที่นิยมกดเพื่อ 'รีเฟรช' หรือโหลดหน้าเว็บไซต์ใหม่?",
                "choice_a": "F1", "choice_b": "F5", "choice_c": "F11", "choice_d": "F12",
                "correct_choice": "B", "explanation": "ปุ่ม F5 คือปุ่มลัดสากลสำหรับคำสั่ง Refresh / Reload หน้าเว็บเพจในเบราว์เซอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "คำสั่ง 'Restart' ในคอมพิวเตอร์หมายถึงการกระทำข้อใด?",
                "choice_a": "ปิดเครื่องแล้วเปิดขึ้นมาใหม่โดยอัตโนมัติ", "choice_b": "ล้างข้อมูลทั้งหมดในฮาร์ดดิสก์", "choice_c": "ปิดหน้าจอคอมพิวเตอร์", "choice_d": "เพิ่มความเร็วสัญญาณเน็ต",
                "correct_choice": "A", "explanation": "Restart คือการเริ่มต้นระบบใหม่ โดยปิดโปรแกรมแล้วบูตเครื่องขึ้นมาใหม่ทันที"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดใช้สำหรับกระจายสัญญาณเครือข่ายอินเทอร์เน็ตแบบไร้สาย (Wi-Fi) ภายในบ้าน?",
                "choice_a": "เมาส์", "choice_b": "เราเตอร์ (Wi-Fi Router)", "choice_c": "แรม (RAM)", "choice_d": "เครื่องคิดเลข",
                "correct_choice": "B", "explanation": "Router (เราเตอร์) ทำหน้าที่กระจายสัญญาณอินเทอร์เน็ตทั้งแบบสาย LAN และแบบไร้สาย Wi-Fi"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "รหัสผ่าน (Password) ที่มีความปลอดภัยสูง ควรมีลักษณะอย่างไร?",
                "choice_a": "ใช้ตัวเลข 123456", "choice_b": "ใช้วันเดือนปีเกิดของตัวเอง", "choice_c": "ผสมตัวอักษรพิมพ์ใหญ่ พิมพ์เล็ก ตัวเลข และสัญลักษณ์พิเศษ", "choice_d": "ใช้เบอร์โทรศัพท์มือถือ",
                "correct_choice": "C", "explanation": "รหัสผ่านที่รัดกุมควรมีความยาวเกิน 8-12 ตัวอักษร และมีตัวพิมพ์ใหญ่ พิมพ์เล็ก ตัวเลข และอักขระพิเศษผสมกัน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ข้อมูลใดต่อไปนี้ที่ไม่ควรเปิดเผยให้กับบุคคลอื่นบนอินเทอร์เน็ตเพื่อความปลอดภัย?",
                "choice_a": "ชื่อเล่นในเกม", "choice_b": "รหัสผ่านและรหัส OTP บัญชีส่วนตัว", "choice_c": "อาหารที่ชอบรับประทาน", "choice_d": "เพลงโปรด",
                "correct_choice": "B", "explanation": "รหัสผ่านและ OTP เป็นข้อมูลลับเฉพาะตัว ห้ามเปิดเผยให้ผู้อื่นเด็ดขาดเพื่อป้องกันการถูกแฮก"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์นามสกุล '.jpg' และ '.png' จัดเป็นไฟล์ประเภทใด?",
                "choice_a": "ไฟล์รูปภาพ (Image)", "choice_b": "ไฟล์เสียง (Audio)", "choice_c": "ไฟล์เอกสาร (Document)", "choice_d": "ไฟล์วิดีโอ (Video)",
                "correct_choice": "A", "explanation": "JPG และ PNG คือนามสกุลไฟล์ภาพดิจิทัลที่ใช้งานแพร่หลายมากที่สุด"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์นามสกุล '.mp3' จัดเป็นไฟล์ประเภทใด?",
                "choice_a": "ไฟล์ตารางคำนวณ", "choice_b": "ไฟล์เสียงเพลง (Audio)", "choice_c": "ไฟล์ระบบปฏิบัติการ", "choice_d": "ไฟล์ฐานข้อมูล",
                "correct_choice": "B", "explanation": "MP3 คือรูปแบบไฟล์บันทึกเสียงและดนตรีมาตรฐานที่มีการบีบอัดข้อมูลอย่างมีประสิทธิภาพ"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ไฟล์นามสกุล '.pdf' มีข้อดีหลักอย่างไรในการส่งเอกสาร?",
                "choice_a": "เปิดอ่านได้เหมือนต้นฉบับในทุกอุปกรณ์และระบบปฏิบัติการ", "choice_b": "สามารถตัดต่อเสียงได้ทันที", "choice_c": "ช่วยเพิ่มความเร็วซีพียู", "choice_d": "เปิดเล่นเกมได้",
                "correct_choice": "A", "explanation": "PDF (Portable Document Format) ถูกออกแบบมาเพื่อรักษาการจัดหน้าและรูปแบบเอกสารให้คงที่ในทุกอุปกรณ์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "เทคโนโลยีไร้สายระยะใกล้ที่นิยมใช้เชื่อมต่อคอมพิวเตอร์กับหูฟังหรือเมาส์ไร้สายคืออะไร?",
                "choice_a": "ดาวเทียม GPS", "choice_b": "บลูทูธ (Bluetooth)", "choice_c": "สายไฟเบอร์ออปติก", "choice_d": "คลื่นไมโครเวฟ",
                "correct_choice": "B", "explanation": "Bluetooth เป็นเทคโนโลยีการส่งข้อมูลไร้สายคลื่นวิทยุระยะสั้นที่ประหยัดพลังงาน"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Ctrl + A' มีหน้าที่อะไรในการจัดการข้อความหรือไฟล์?",
                "choice_a": "เลือกทั้งหมด (Select All)", "choice_b": "ลบไฟล์ทั้งหมด", "choice_c": "เรียงลำดับตามตัวอักษร", "choice_d": "ปิดโปรแกรมทั้งหมด",
                "correct_choice": "A", "explanation": "Ctrl + A ย่อมาจาก All ใช้สำหรับเลือกข้อความหรือวัตถุทั้งหมดในหน้าต่างนั้น"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "ปุ่มลัด 'Alt + Tab' บน Windows มีประโยชน์ในการทำงานอย่างไร?",
                "choice_a": "ปิดเครื่องคอมพิวเตอร์ทันที", "choice_b": "สลับการทำงานระหว่างหน้าต่างโปรแกรมที่เปิดอยู่", "choice_c": "เปิดแว่นขยายหน้าจอ", "choice_d": "เปิดเมนู Start",
                "correct_choice": "B", "explanation": "Alt + Tab ใช้สำหรับสลับหน้าต่างแอปพลิเคชันที่เปิดใช้งานได้อย่างรวดเร็ว"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรม 'Notepad' ในระบบ Windows มีไว้เพื่อจุดประสงค์ใด?",
                "choice_a": "จดบันทึกข้อความธรรมดา (Plain Text)", "choice_b": "ตัดต่อภาพยนตร์ความละเอียดสูง", "choice_c": "สแกนหาไวรัสในเครื่อง", "choice_d": "คำนวณภาษีอัตโนมัติ",
                "correct_choice": "A", "explanation": "Notepad เป็นโปรแกรม Text Editor พื้นฐานที่มาพร้อม Windows สำหรับแก้ไขข้อความธรรมดา"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "โปรแกรม 'Paint' บน Windows เหมาะสำหรับใช้งานประเภทใด?",
                "choice_a": "เขียนโค้ดภาษา C", "choice_b": "วาดรูปและแก้ไขภาพเบื้องต้น", "choice_c": "บันทึกเสียงเพลง", "choice_d": "ส่งอีเมล",
                "correct_choice": "B", "explanation": "Paint เป็นโปรแกรมวาดภาพและปรับแต่งภาพกราฟิกเบื้องต้นที่แถมมากับ Windows ทุกรุ่น"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "การส่งไฟล์หรือข้อมูลจากคอมพิวเตอร์ของเราขึ้นไปยังอินเทอร์เน็ต เรียกว่าอะไร?",
                "choice_a": "อัปโหลด (Upload)", "choice_b": "ดาวน์โหลด (Download)", "choice_c": "รีสตาร์ท (Restart)", "choice_d": "ดีลีต (Delete)",
                "correct_choice": "A", "explanation": "Upload คือการส่งผ่านข้อมูลจากเครื่องผู้ใช้ไปยังเซิร์ฟเวอร์หรือคลาวด์บนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "การดึงไฟล์หรือข้อมูลจากอินเทอร์เน็ตมาเก็บไว้ในคอมพิวเตอร์ของเรา เรียกว่าอะไร?",
                "choice_a": "อัปโหลด (Upload)", "choice_b": "ดาวน์โหลด (Download)", "choice_c": "สแกนดิสก์ (ScanDisk)", "choice_d": "คอมไพล์ (Compile)",
                "correct_choice": "B", "explanation": "Download คือการคัดลอกไฟล์จากเครือข่ายอินเทอร์เน็ตลงมาบันทึกในเครื่องของเรา"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "คำว่า 'WWW' ที่นำหน้าชื่อเว็บไซต์ ย่อมาจากคำว่าอะไร?",
                "choice_a": "World Wide Web", "choice_b": "World Wide Windows", "choice_c": "Web World Wide", "choice_d": "World Web Wireless",
                "correct_choice": "A", "explanation": "World Wide Web (WWW) คือระบบเครือข่ายข้อมูลที่เชื่อมโยงถึงกันทั่วโลกผ่านอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "Google, Bing และ Yahoo จัดเป็นเว็บไซต์ประเภทใด?",
                "choice_a": "Search Engine (เครื่องมือค้นหาข้อมูล)", "choice_b": "ระบบปฏิบัติการ", "choice_c": "แอปพลิเคชันเล่นเพลง", "choice_d": "โปรแกรมบีบอัดไฟล์",
                "correct_choice": "A", "explanation": "Search Engine คือระบบเว็บไซต์ที่ให้บริการค้นหาข้อมูล เอกสาร และรูปภาพบนอินเทอร์เน็ต"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "อุปกรณ์ใดทำหน้าที่แสดงผลภาพและกราฟิกให้ผู้ใช้งานมองเห็นบนโต๊ะคอมพิวเตอร์?",
                "choice_a": "ฮาร์ดดิสก์", "choice_b": "จอภาพ (Monitor)", "choice_c": "เมนบอร์ด", "choice_d": "คีย์บอร์ด",
                "correct_choice": "B", "explanation": "Monitor (จอภาพ) เป็นอุปกรณ์แสดงผลลัพธ์ทางสายตา (Visual Output) หลักของคอมพิวเตอร์"
            },
            {
                "category": cat_basic, "difficulty": "ง่าย", "is_active": True,
                "text": "กล้องที่ติดอยู่บนหน้าจอโน้ตบุ๊กหรือเชื่อมต่อผ่านพอร์ต USB เพื่อใช้ในการประชุมออนไลน์เรียกว่าอะไร?",
                "choice_a": "เว็บแคม (Webcam)", "choice_b": "เครื่องสแกนเนอร์", "choice_c": "แฟลชไดรฟ์", "choice_d": "การ์ดเสียง",
                "correct_choice": "A", "explanation": "เว็บแคม (Webcam) เป็นกล้องวิดีโอดิจิทัลที่ใช้ส่งภาพสดสำหรับการเรียนและประชุมออนไลน์"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับปานกลาง (MEDIUM) 25 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยความจำ 'RAM' และ 'ROM' แตกต่างกันอย่างไรเมื่อมีการปิดหรือดับไฟคอมพิวเตอร์?",
                "choice_a": "RAM ข้อมูลจะหายไป แต่ ROM ข้อมูลยังคงอยู่", "choice_b": "ROM ข้อมูลจะหายไป แต่ RAM ข้อมูลยังคงอยู่", "choice_c": "ทั้งคู่ข้อมูลจะหายไปพร้อมกัน", "choice_d": "ทั้งคู่เก็บข้อมูลถาวรไม่มีวันหาย",
                "correct_choice": "A", "explanation": "RAM เป็นหน่วยความจำชั่วคราว (Volatile Memory) ดับไฟแล้วข้อมูลหาย ส่วน ROM เป็นหน่วยความจำถาวร (Non-volatile)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "อุปกรณ์จัดเก็บข้อมูลแบบ 'SSD' (Solid State Drive) มีข้อได้เปรียบเหนือ 'HDD' (Hard Disk Drive) ในด้านใดชัดเจนที่สุด?",
                "choice_a": "ความเร็วในการอ่าน-เขียนข้อมูลสูงกว่ามากและไม่มีชิ้นส่วนที่หมุน", "choice_b": "ราคาต่อความจุถูกกว่า HDD มาก", "choice_c": "สามารถรับสัญญาณ Wi-Fi ในตัวได้", "choice_d": "มีความจุไม่จำกัด",
                "correct_choice": "A", "explanation": "SSD ใช้ชิป Flash Memory จึงทำงานเงียบ ทนต่อแรงสั่นสะเทือน และมีความเร็วอ่านเขียนสูงกว่าฮาร์ดดิสก์จานหมุน HDD หลายเท่า"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ในระบบหน่วยวัดข้อมูลดิจิทัล 1 ไบต์ (Byte) มีค่าเท่ากับกี่บิต (Bits)?",
                "choice_a": "4 บิต", "choice_b": "8 บิต", "choice_c": "16 บิต", "choice_d": "32 บิต",
                "correct_choice": "B", "explanation": "1 Byte เท่ากับ 8 Bits ซึ่งเป็นขนาดมาตรฐานที่ใช้แทนรหัสอักขระ 1 ตัวอักษร"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยความจุ 1 Gigabyte (GB) มีค่าเท่ากับกี่ Megabyte (MB) ในทางคอมพิวเตอร์เลขฐานสอง?",
                "choice_a": "1,000 MB", "choice_b": "1,024 MB", "choice_c": "512 MB", "choice_d": "2,048 MB",
                "correct_choice": "B", "explanation": "ในระบบเลขฐานสอง 1 GB มีค่าเท่ากับ 2^10 หรือ 1,024 MB"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หมายเลข 'IP Address' ในระบบเครือข่ายคอมพิวเตอร์ทำหน้าที่เปรียบเหมือนสิ่งใด?",
                "choice_a": "บ้านเลขที่ที่ระบุตำแหน่งของอุปกรณ์ในระบบเครือข่าย", "choice_b": "รหัสผ่านเข้า Wi-Fi", "choice_c": "ชื่อยี่ห้อของคอมพิวเตอร์", "choice_d": "ความเร็วของสัญญาณเน็ต",
                "correct_choice": "A", "explanation": "IP Address ทำหน้าที่เป็นหมายเลขประจำอุปกรณ์ในเครือข่ายเพื่อให้ส่งข้อมูลไปยังปลายทางได้ถูกต้อง"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบ 'DNS' (Domain Name System) มีหน้าที่หลักคืออะไรในอินเทอร์เน็ต?",
                "choice_a": "แปลงชื่อเว็บไซต์ (เช่น google.com) ให้เป็นหมายเลข IP Address", "choice_b": "สแกนหาไวรัสในอีเมล", "choice_c": "เพิ่มความเร็วสัญญาณดาวเทียม", "choice_d": "ตั้งรหัสผ่านเราเตอร์",
                "correct_choice": "A", "explanation": "DNS ทำหน้าที่เสมือนสมุดโทรศัพท์ แปลงชื่อเว็บไซต์ที่มนุษย์จำง่ายให้เป็นหมายเลข IP Address ที่คอมพิวเตอร์ใช้ติดต่อสื่อสาร"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "การยืนยันตัวตนแบบ '2FA' (Two-Factor Authentication) ช่วยเพิ่มความปลอดภัยอย่างไร?",
                "choice_a": "ต้องล็อกอินผ่าน 2 ขั้นตอน เช่น กรอกรหัสผ่านคู่กับรหัส OTP", "choice_b": "ให้เพื่อนช่วยกดยืนยัน 2 คน", "choice_c": "ต้องพิมพ์รหัสผ่านซ้ำ 2 รอบในช่องเดิม", "choice_d": "ต้องเปิดคอมพิวเตอร์พร้อมกัน 2 เครื่อง",
                "correct_choice": "A", "explanation": "2FA เป็นการตรวจสอบตัวตน 2 ชั้น เช่น รหัสผ่าน (สิ่งที่รู้) + OTP ในมือถือ (สิ่งที่มี) เพื่อป้องกันผู้ไม่หวังดี"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ภัยคุกคามทางไซเบอร์แบบ 'Phishing' (ฟิชชิ่ง) มีลักษณะการหลอกลวงอย่างไร?",
                "choice_a": "สร้างหน้าเว็บหรือส่งอีเมลปลอมเพื่อหลอกให้เหยื่อกรอกรหัสผ่านและข้อมูลการเงิน", "choice_b": "แอบเข้ามาขโมยปลั๊กไฟคอมพิวเตอร์", "choice_c": "ทำให้พัดลมซีพียูหมุนช้าลง", "choice_d": "ส่งไฟล์ขนาดใหญ่จนฮาร์ดดิสก์เต็ม",
                "correct_choice": "A", "explanation": "Phishing เป็นการหลอกลวงแบบวิศวกรรมสังคม (Social Engineering) โดยทำเว็บไซต์หรือข้อความปลอมเพื่อขโมยข้อมูลสำคัญ"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ซอฟต์แวร์ประเภท 'Malware' (มัลแวร์) มีความหมายครอบคลุมสิ่งใด?",
                "choice_a": "โปรแกรมประสงค์ร้ายทั้งหมด เช่น ไวรัส เวิร์ม ม้าโทรจัน และสปายแวร์", "choice_b": "โปรแกรมสำหรับเล่นเกมออนไลน์ฟรี", "choice_c": "ไดรเวอร์การ์ดจอที่อัปเดตใหม่ล่าสุด", "choice_d": "ระบบปฏิบัติการรุ่นทดลอง",
                "correct_choice": "A", "explanation": "Malware ย่อมาจาก Malicious Software หมายถึงซอฟต์แวร์ไม่พึงประสงค์ทุกชนิดที่มุ่งทำลายหรือขโมยข้อมูล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "เครือข่ายคอมพิวเตอร์แบบ 'LAN' (Local Area Network) หมายถึงเครือข่ายลักษณะใด?",
                "choice_a": "เครือข่ายเฉพาะบริเวณในพื้นที่จำกัด เช่น ในบ้าน ห้องเรียน หรืออาคารเดียวกัน", "choice_b": "เครือข่ายเชื่อมต่อทั่วโลก", "choice_c": "เครือข่ายดาวเทียมระหว่างประเทศ", "choice_d": "เครือข่ายใต้ท้องทะเล",
                "correct_choice": "A", "explanation": "LAN เป็นเครือข่ายท้องถิ่นระยะใกล้ เช่น การเชื่อมต่อคอมพิวเตอร์และเครื่องพิมพ์ในห้องทำงานเดียวกัน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "อุปกรณ์ 'GPU' (Graphics Processing Unit) มีหน้าที่หลักเน้นไปที่งานประเภทใด?",
                "choice_a": "ประมวลผลกราฟิก แสดงผลภาพ 3 มิติ และงานคำนวณแบบขนาน", "choice_b": "จ่ายกระแสไฟไปยังเมนบอร์ด", "choice_c": "เก็บไฟล์ระบบปฏิบัติการ", "choice_d": "ขยายเสียงลำโพง",
                "correct_choice": "A", "explanation": "GPU ทำหน้าที่ประมวลผลภาพกราฟิก วิดีโอ เกม 3 มิติ และปัจจุบันยังนิยมใช้ประมวลผลโมเดล AI อีกด้วย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "สายเคเบิล 'HDMI' นิยมใช้สำหรับส่งสัญญาณประเภทใดไปยังหน้าจอหรือทีวี?",
                "choice_a": "ส่งทั้งสัญญาณภาพดิจิทัลและสัญญาณเสียงพร้อมกันในสายเดียว", "choice_b": "ส่งเฉพาะกระแสไฟฟ้าเท่านั้น", "choice_c": "ส่งเฉพาะสัญญาณเสียงอย่างเดียว", "choice_d": "ส่งสัญญาณวิทยุ AM/FM",
                "correct_choice": "A", "explanation": "HDMI (High-Definition Multimedia Interface) รองรับการส่งทั้งสัญญาณภาพความละเอียดสูงและเสียงพร้อมกัน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ซอฟต์แวร์แบบ 'Open Source' มีจุดเด่นสำคัญคือข้อใด?",
                "choice_a": "เปิดเผยซอร์สโค้ดให้สาธารณะนำไปศึกษา ปรับปรุง และใช้งานได้", "choice_b": "เป็นโปรแกรมที่ต้องเสียค่าลิขสิทธิ์แพงที่สุด", "choice_c": "ห้ามผู้ใช้ทำการดัดแปลงโค้ดใด ๆ ทั้งสิ้น", "choice_d": "ใช้งานได้เฉพาะบนระบบ Windows เท่านั้น",
                "correct_choice": "A", "explanation": "Open Source ให้สิทธิ์เปิดเผยซอร์สโค้ดเพื่อให้นักพัฒนาทั่วโลกช่วยกันพัฒนาและตรวจสอบความปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบ 'Cloud Storage' เช่น Google Drive, OneDrive, iCloud มีประโยชน์หลักอย่างไร?",
                "choice_a": "เก็บไฟล์ไว้บนเซิร์ฟเวอร์ออนไลน์ สามารถเข้าถึงข้อมูลได้จากทุกอุปกรณ์ที่ต่อเน็ต", "choice_b": "เพิ่มความเร็วการทำงานของพัดลมซีพียู", "choice_c": "ช่วยซ่อมชิ้นส่วนฮาร์ดแวร์ที่ชำรุด", "choice_d": "ช่วยให้ไม่ต้องใช้คีย์บอร์ดพิมพ์งาน",
                "correct_choice": "A", "explanation": "Cloud Storage ให้บริการจัดเก็บไฟล์ผ่านระบบคลาวด์ ทำให้เปิดดูและแชร์งานได้ทุกที่ทุกเวลา"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบปฏิบัติการ 'Linux' จัดเป็นระบบประเภทใดและมีบทบาทสำคัญอย่างไร?",
                "choice_a": "เป็นระบบปฏิบัติการแบบเปิด (Open Source) นิยมใช้อย่างแพร่หลายบนเซิร์ฟเวอร์และคลาวด์", "choice_b": "เป็นโปรแกรมวาดภาพที่มีราคาแพง", "choice_c": "เป็นแอนติไวรัสสำหรับมือถือ", "choice_d": "เป็นยี่ห้อของจอภาพคอมพิวเตอร์",
                "correct_choice": "A", "explanation": "Linux เป็นระบบปฏิบัติการเสรีที่มีความเสถียรและความปลอดภัยสูง เป็นกระดูกสันหลังของระบบ Server ทั่วโลก"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ระบบความปลอดภัย 'Firewall' (ไฟร์วอลล์) ในคอมพิวเตอร์ทำหน้าที่อะไร?",
                "choice_a": "ตรวจสอบและคัดกรองข้อมูลเครือข่ายเข้า-ออกตามกฎความปลอดภัย", "choice_b": "ดับเพลิงเมื่อคอมพิวเตอร์เกิดความร้อนสูง", "choice_c": "ป้องกันไม่ให้สายไฟขาด", "choice_d": "ช่วยเร่งความเร็วพัดลมระบายความร้อน",
                "correct_choice": "A", "explanation": "Firewall ทำหน้าที่เป็นประตูด่านตรวจ คัดกรองทราฟฟิกข้อมูลที่น่าสงสัยไม่ให้บุกรุกเข้าสู่เครือข่าย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ไฟล์บีบอัดนามสกุล '.zip' หรือ '.rar' มีประโยชน์อย่างไร?",
                "choice_a": "รวมไฟล์หลายไฟล์เข้าด้วยกันและลดขนาดไฟล์ให้เล็กลงเพื่อความสะดวกในการส่งต่อ", "choice_b": "แปลงไฟล์เสียงเป็นไฟล์วิดีโอ", "choice_c": "เพิ่มความเร็วให้กับเครื่องพิมพ์", "choice_d": "ทำให้ภาพมีความคมชัดขึ้น 2 เท่า",
                "correct_choice": "A", "explanation": "ไฟล์ Zip/Rar เป็นการบีบอัดข้อมูล (Compression) ช่วยประหยัดพื้นที่จัดเก็บและง่ายต่อการส่งต่อทางอีเมล"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "คำว่า 'URL' (Uniform Resource Locator) ในการใช้อินเทอร์เน็ตหมายถึงสิ่งใด?",
                "choice_a": "ที่อยู่ระบุตำแหน่งของหน้าเว็บหรือทรัพยากรบนอินเทอร์เน็ต", "choice_b": "รหัสประจำตัวผู้ใช้งาน", "choice_c": "ชื่อยี่ห้อของสายแลน", "choice_d": "ความเร็วในการส่งข้อมูลต่อวินาที",
                "correct_choice": "A", "explanation": "URL คือที่อยู่เว็บไซต์ (Web Address) เช่น https://www.google.com ที่ใช้ระบุตำแหน่งของหน้าเว็บ"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "คำว่า 'Cookie' ในเว็บเบราว์เซอร์หมายถึงอะไร?",
                "choice_a": "ไฟล์ขนาดเล็กที่เว็บไซต์บันทึกไว้ในเครื่องผู้ใช้เพื่อจดจำสถานะและข้อมูลการใช้งาน", "choice_b": "ไวรัสชนิดหนึ่งที่ลบไฟล์ในเครื่อง", "choice_c": "ปุ่มพิเศษบนคีย์บอร์ดเกมมิ่ง", "choice_d": "อุปกรณ์เสริมสำหรับทำความสะอาดจอภาพ",
                "correct_choice": "A", "explanation": "HTTP Cookie เป็นไฟล์ข้อมูลขนาดเล็กที่เบราว์เซอร์เก็บไว้เพื่อช่วยจำการล็อกอินและการตั้งค่าของผู้ใช้"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หน่วยวัดความเร็วสัญญาณนาฬิกาของซีพียูคอมพิวเตอร์ในปัจจุบันนิยมใช้หน่วยใด?",
                "choice_a": "Gigahertz (GHz)", "choice_b": "Gigabyte (GB)", "choice_c": "Megabit (Mb)", "choice_d": "DPI",
                "correct_choice": "A", "explanation": "ความเร็วสัญญาณนาฬิกา (Clock Speed) ของ CPU วัดเป็น Hertz เช่น GHz (พันล้านรอบต่อวินาที)"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โปรแกรมประเภท 'Driver' (ไดรเวอร์) มีความสำคัญอย่างไรต่อคอมพิวเตอร์?",
                "choice_a": "เป็นโปรแกรมตัวกลางที่ช่วยให้ระบบปฏิบัติการสื่อสารและควบคุมฮาร์ดแวร์ได้อย่างถูกต้อง", "choice_b": "เป็นเกมขับรถสำหรับคอมพิวเตอร์", "choice_c": "เป็นแอปพลิเคชันสำหรับส่งข้อความ", "choice_d": "เป็นโปรแกรมล้างไฟล์ขยะ",
                "correct_choice": "A", "explanation": "Device Driver ทำหน้าที่เป็นตัวแปลคำสั่งระหว่าง OS กับอุปกรณ์ฮาร์ดแวร์ เช่น การ์ดจอ หรือเครื่องพิมพ์"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "การเข้ารหัสข้อมูล (Encryption) มีประโยชน์อย่างไรในระบบคอมพิวเตอร์?",
                "choice_a": "แปลงข้อมูลให้อยู่ในรูปแบบที่อ่านไม่ออก เพื่อป้องกันไม่ให้ผู้ไม่มีสิทธิ์เข้าถึงข้อมูลได้", "choice_b": "ลดขนาดไฟล์รูปภาพให้เล็กลง", "choice_c": "เพิ่มเสียงให้ไมโครโฟน", "choice_d": "ทำให้แบตเตอรี่หมดช้าลง",
                "correct_choice": "A", "explanation": "Encryption เป็นการแปลงข้อความให้อยู่ในรูปของรหัสลับ (Ciphertext) โดยมีเพียงผู้ถือกุญแจถอดรหัสเท่านั้นที่อ่านได้"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โปรโตคอล 'HTTPS' แตกต่างจาก 'HTTP' ทั่วไปอย่างไร?",
                "choice_a": "HTTPS มีการเข้ารหัสความปลอดภัยผ่าน SSL/TLS ป้องกันการดักจับข้อมูล", "choice_b": "HTTPS ใช้งานได้เฉพาะบนโทรศัพท์มือถือ", "choice_c": "HTTPS มีความเร็วในการโหลดช้ากว่า 10 เท่า", "choice_d": "HTTPS เป็นเว็บไซต์ที่ต้องเสียค่าเข้าชม",
                "correct_choice": "A", "explanation": "HTTPS (S = Secure) มีการเข้ารหัสข้อมูลที่รับส่งระหว่างเครื่องผู้ใช้กับเซิร์ฟเวอร์เพื่อความปลอดภัย"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "อุปกรณ์ 'Motherboard' (เมนบอร์ด) ทำหน้าที่เปรียบเสมือนอะไรในเครื่องคอมพิวเตอร์?",
                "choice_a": "แผงวงจรหลักที่เป็นศูนย์กลางเชื่อมต่ออุปกรณ์ทุกชิ้นเข้าด้วยกัน", "choice_b": "แบตเตอรี่สำรองไฟ", "choice_c": "เลนส์กล้องบันทึกภาพ", "choice_d": "ลำโพงส่งเสียงเพลง",
                "correct_choice": "A", "explanation": "Mainboard / Motherboard คือแผงวงจรอิเล็กทรอนิกส์หลักที่เชื่อมโยง CPU, RAM, การ์ดจอ และอุปกรณ์ทุกส่วนเข้าด้วยกัน"
            },
            {
                "category": cat_basic, "difficulty": "ปานกลาง", "is_active": True,
                "text": "คำว่า 'Bandwidth' ในระบบเครือข่ายอินเทอร์เน็ตหมายถึงสิ่งใด?",
                "choice_a": "ปริมาณข้อมูลสูงสุดที่สามารถส่งผ่านช่องทางเครือข่ายได้ในหนึ่งหน่วยเวลา", "choice_b": "ความยาวของสายแลนที่ต่อในบ้าน", "choice_c": "น้ำหนักของตัวเครื่องเราเตอร์", "choice_d": "จำนวนเสาสัญญาณบนกล่อง Wi-Fi",
                "correct_choice": "A", "explanation": "Bandwidth คือความกว้างของช่องสัญญาณหรือปริมาณการถ่ายโอนข้อมูลสูงสุดในเวลาที่กำหนด (เช่น Mbps)"
            },

            # =========================================================================
            # [หมวด: คอมพิวเตอร์เบื้องต้น] - ระดับยาก (HARD) 25 ข้อ
            # =========================================================================
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หน่วยความจำแคช 'Cache Memory' (L1, L2, L3) มีบทบาทสำคัญอย่างไรต่อการทำงานของ CPU?",
                "choice_a": "เป็นหน่วยความจำความเร็วสูงมากที่อยู่ใกล้หรือในตัว CPU ช่วยลดเวลาหน่วงในการดึงข้อมูลจาก RAM", "choice_b": "ใช้เก็บไฟล์ขนาดใหญ่ที่ไม่ค่อยได้ใช้งาน", "choice_c": "ช่วยทำความสะอาดฝุ่นในเคสคอมพิวเตอร์", "choice_d": "ลดการใช้พลังงานของจอภาพ",
                "correct_choice": "A", "explanation": "Cache Memory มีความเร็วสูงกว่า RAM ทั่วไปหลายเท่า ใช้เก็บคำสั่งและข้อมูลที่ CPU เรียกใช้บ่อยเพื่อลด Latency"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบเฟิร์มแวร์ 'UEFI' ได้รับการพัฒนาขึ้นมาทดแทนระบบ 'BIOS' ดั้งเดิมด้วยข้อได้เปรียบใด?",
                "choice_a": "รองรับฮาร์ดดิสก์ความจุมากกว่า 2.2 TB (GPT), บูตได้เร็วกว่า และมีระบบความปลอดภัย Secure Boot", "choice_b": "ทำให้คอมพิวเตอร์ไม่ต้องใช้แรม", "choice_c": "ช่วยแปลงไฟล์วิดีโอเป็น 8K", "choice_d": "ทำให้คีย์บอร์ดพิมพ์เร็วขึ้น 2 เท่า",
                "correct_choice": "A", "explanation": "UEFI รองรับระบบพาร์ติชัน GPT ทำให้ใช้ดิสก์ขนาดใหญ่เกิน 2.2 TB ได้ และรองรับฟีเจอร์ความปลอดภัยอย่าง Secure Boot"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบปฏิบัติการแบบ 64-bit แตกต่างจาก 32-bit ในแง่การจัดการหน่วยความจำ RAM อย่างไร?",
                "choice_a": "32-bit รองรับ RAM สูงสุดเพียง 4 GB ส่วน 64-bit รองรับ RAM ได้มหาศาลเกิน 4 GB", "choice_b": "32-bit ทำงานเร็วกว่า 64-bit เสมอ", "choice_c": "64-bit ใช้ได้เฉพาะเครื่องที่ไม่มีฮาร์ดดิสก์", "choice_d": "ทั้งสองแบบรองรับ RAM สูงสุดเท่ากันที่ 4 GB",
                "correct_choice": "A", "explanation": "ระบบ 32-bit มีขีดจำกัดแอดเดรสหน่วยความจำ 2^32 ไบต์ หรือประมาณ 4 GB ในขณะที่ 64-bit รองรับได้ถึง 16 Exabytes"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "เทคโนโลยี 'NVMe' (Non-Volatile Memory Express) ใน SSD ทำงานผ่านบัสใดของเมนบอร์ดที่ทำให้มีความเร็วสูงมาก?",
                "choice_a": "PCIe (PCI Express)", "choice_b": "SATA 1.0", "choice_c": "IDE / PATA", "choice_d": "VGA Port",
                "correct_choice": "A", "explanation": "SSD แบบ NVMe เชื่อมต่อโดยตรงกับบัส PCIe ทำให้มี Bandwidth และความเร็วในการรับส่งข้อมูลสูงกว่าบัส SATA มาก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ในการบูตคอมพิวเตอร์ กระบวนการ 'POST' (Power-On Self-Test) ทำหน้าที่อะไร?",
                "choice_a": "ตรวจสอบความพร้อมและความสมบูรณ์ของอุปกรณ์ฮาร์ดแวร์หลักทั้งหมดก่อนเริ่มโหลด OS", "choice_b": "โพสต์สถานะการเปิดเครื่องลงโซเชียลมีเดีย", "choice_c": "สแกนไวรัสในไฟล์เอกสาร", "choice_d": "ดาวน์โหลดอัปเดตของวินโดวส์",
                "correct_choice": "A", "explanation": "POST เป็นโปรแกรมทดสอบฮาร์ดแวร์พื้นฐาน (CPU, RAM, การ์ดจอ) ในช่วงเปิดเครื่อง หากพบปัญหาจะส่งเสียง Beep Code เตือน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'RAID 1' ในการจัดเก็บข้อมูลมีรูปแบบการทำงานและจุดประสงค์เพื่ออะไร?",
                "choice_a": "Mirroring (เขียนข้อมูลซ้ำกันลงดิสก์ 2 ตัว) เพื่อป้องกันข้อมูลสูญหายเมื่อดิสก์ตัวใดตัวหนึ่งเสีย", "choice_b": "Striping เพื่อเร่งความเร็วอย่างเดียวโดยไม่มีการสำรองข้อมูล", "choice_c": "บีบอัดไฟล์เพลงให้เล็กลง", "choice_d": "ลบไฟล์ขยะอัตโนมัติ",
                "correct_choice": "A", "explanation": "RAID 1 สำเนาข้อมูลเหมือนกันลงบนไดรฟ์คู่ขนาน (Disk Mirroring) ทำให้มีความปลอดภัยสูงหากไดรฟ์ใดชำรุด"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "อาการคอขวด 'Bottleneck' ในการประกอบคอมพิวเตอร์หมายถึงเหตุการณ์ใด?",
                "choice_a": "อุปกรณ์ชิ้นหนึ่งมีประสิทธิภาพต่ำกว่าชิ้นอื่นมาก จนฉุดรั้งประสิทธิภาพรวมของระบบ", "choice_b": "สายไฟในเคสถูกมัดแน่นเกินไปจนไฟเดินไม่สะดวก", "choice_c": "ช่องพัดลมระบายความร้อนมีขนาดเล็กเกินไป", "choice_d": "การเปิดใช้งานโปรแกรมพร้อมกันมากเกินไป",
                "correct_choice": "A", "explanation": "Bottleneck เกิดขึ้นเมื่ออุปกรณ์ชิ้นใดชิ้นหนึ่งทำงานช้า (เช่น CPU ช้าเกินไปเมื่อจับคู่กับการ์ดจอระดับท็อป) จนจำกัดประสิทธิภาพรวม"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ตราสัญลักษณ์ '80 PLUS' (เช่น Bronze, Gold, Platinum) บนพาวเวอร์ซัพพลาย (PSU) บ่งบอกถึงสิ่งใด?",
                "choice_a": "ประสิทธิภาพการแปลงพลังงานไฟฟ้า (Energy Efficiency) สูงกว่า 80%", "choice_b": "รับประกันการใช้งานยาวนาน 80 ปี", "choice_c": "รองรับอุณหภูมิห้องสูงสุด 80 องศาเซลเซียส", "choice_d": "จ่ายกำลังไฟได้ไม่เกิน 80 วัตต์",
                "correct_choice": "A", "explanation": "80 PLUS คือมาตรฐานรับรองประสิทธิภาพการแปลงไฟกระแสสลับ (AC) เป็นกระแสตรง (DC) โดยสูญเสียพลังงานเป็นความร้อนน้อย"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หน่วยความจำเสมือน 'Virtual Memory' (หรือ Paging File) ในระบบปฏิบัติการทำงานอย่างไรเมื่อ RAM เต็ม?",
                "choice_a": "นำพื้นที่บางส่วนของฮาร์ดดิสก์หรือ SSD มาจำลองใช้เป็นหน่วยความจำชั่วคราวเพื่อป้องกันโปรแกรมค้าง", "choice_b": "ส่งข้อมูลไปเก็บไว้บนดาวเทียมอวกาศ", "choice_c": "ปิดคอมพิวเตอร์โดยอัตโนมัติเพื่อระบายความร้อน", "choice_d": "ลบไฟล์รูปภาพออกจากเครื่องถาวร",
                "correct_choice": "A", "explanation": "Virtual Memory ช่วยขยายขีดความสามารถของ RAM โดยพักข้อมูลหน้าเพจที่ไม่ได้ใช้งานลงในพื้นที่สตอเรจชั่วคราว"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "กฎการสำรองข้อมูลมาตรฐาน '3-2-1 Backup Rule' มีหลักการอย่างไร?",
                "choice_a": "สำรองข้อมูล 3 ชุด บนสื่อบันทึก 2 ประเภทที่ต่างกัน และมี 1 ชุดเก็บไว้นอกสถานที่ (Off-site)", "choice_b": "สำรองข้อมูลสัปดาห์ละ 3 ครั้ง ครั้งละ 2 ชั่วโมง นาน 1 เดือน", "choice_c": "ใช้คอมพิวเตอร์ 3 เครื่อง ฮาร์ดดิสก์ 2 ตัว แฟลชไดรฟ์ 1 อัน", "choice_d": "นับถอยหลัง 3 2 1 ก่อนกดบันทึกไฟล์",
                "correct_choice": "A", "explanation": "3-2-1 Backup Rule คือหลักความปลอดภัยที่ดีที่สุด: 3 ชุดข้อมูล, 2 ชนิดสื่อจัดเก็บ (เช่น Cloud + External HDD), 1 สำเนาเก็บต่างสถานที่"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "หมายเลข 'MAC Address' แตกต่างจาก 'IP Address' อย่างไร?",
                "choice_a": "MAC Address เป็นหมายเลขทางกายภาพที่ฝังมากับการ์ดเครือข่าย ส่วน IP Address เป็นหมายเลขเชิงตรรกะที่กำหนดตามระบบเครือข่าย", "choice_b": "MAC Address ใช้เฉพาะเครื่อง Mac ของ Apple เท่านั้น", "choice_c": "IP Address ไม่สามารถเปลี่ยนแปลงได้ แต่ MAC เปลี่ยนได้ตลอดเวลา", "choice_d": "ทั้งสองตัวเป็นหมายเลขชนิดเดียวกันทุกประการ",
                "correct_choice": "A", "explanation": "MAC Address เป็น Physical Address ฮาร์ดแวร์ระดับ Layer 2 ส่วน IP Address เป็น Logical Address ระดับ Layer 3"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "พอร์ต 'DisplayPort' แตกต่างจากพอร์ต 'HDMI' อย่างไรในงานคอมพิวเตอร์ระดับสูง?",
                "choice_a": "DisplayPort ออกแบบมาสำหรับจอมอนิเตอร์คอมพิวเตอร์ รองรับ Refresh Rate สูงและเทคโนโลยี Daisy Chaining", "choice_b": "DisplayPort ไม่สามารถส่งสัญญาณเสียงได้", "choice_c": "HDMI ให้ความละเอียดภาพสูงกว่า DisplayPort เสมอ", "choice_d": "DisplayPort ต้องใช้แบตเตอรี่ในการจ่ายไฟ",
                "correct_choice": "A", "explanation": "DisplayPort นิยมในวงการเกมมิ่งและกราฟิกเนื่องจากมีแบนด์วิดท์สูง รองรับ G-Sync/FreeSync และต่อจอหลายตัวผ่านพอร์ตเดียวได้ (MST)"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การทำ 'Overclocking' (OC) อุปกรณ์คอมพิวเตอร์คืออะไรและมีความเสี่ยงสำคัญอย่างไร?",
                "choice_a": "การปรับเพิ่มความเร็วสัญญาณนาฬิกาให้สูงกว่าค่ามาตรฐานของโรงงาน ทำให้ความร้อนสูงขึ้นและอาจลดอายุการใช้งาน", "choice_b": "การตั้งเวลาเปิด-ปิดเครื่องคอมพิวเตอร์ตามนาฬิกาปลุก", "choice_c": "การเปลี่ยนเคสคอมพิวเตอร์ใหม่", "choice_d": "การปิดพัดลมระบายความร้อนเพื่อให้เครื่องเงียบ",
                "correct_choice": "A", "explanation": "Overclocking คือการเร่งประสิทธิภาพชิ้นส่วน (CPU/GPU/RAM) เกินสเปกมาตรฐาน ซึ่งต้องแลกมาด้วยความร้อนและการใช้พลังงานที่สูงขึ้น"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'Multi-threading' (หรือ Hyper-Threading) ใน CPU มีประโยชน์อย่างไร?",
                "choice_a": "ช่วยให้ 1 คอร์ประมวลผลทางกายภาพสามารถประมวลผลงานได้ 2 Thread พร้อมกัน เพิ่มประสิทธิภาพการทำงานคู่ขนาน", "choice_b": "ช่วยให้พัดลมหมุนได้ 2 ทิศทาง", "choice_c": "เพิ่มขนาดความจุของฮาร์ดดิสก์เป็น 2 เท่า", "choice_d": "ลดขนาดหน้าจอให้เล็กลงครึ่งหนึ่ง",
                "correct_choice": "A", "explanation": "Hyper-Threading ช่วยจำลองคอร์เสมือน (Logical Core) ทำให้ CPU จัดสรรคิวและประมวลผลคำสั่งได้อย่างคุ้มค่าในแต่ละรอบสัญญาณนาฬิกา"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบความปลอดภัยแบบ 'VPN' (Virtual Private Network) ทำงานอย่างไรในการปกป้องข้อมูลผู้ใช้?",
                "choice_a": "สร้างอุโมงค์เชื่อมต่อแบบเข้ารหัส (Encrypted Tunnel) และซ่อนหมายเลข IP ที่แท้จริงจากเครือข่ายสาธารณะ", "choice_b": "ล้างข้อมูลไวรัสทั้งหมดในเครื่องโดยอัตโนมัติ", "choice_c": "เพิ่มความเร็วสัญญาณอินเทอร์เน็ตให้เร็วขึ้น 10 เท่าเสมอ", "choice_d": "ป้องกันไม่ให้แบตเตอรี่เสื่อม",
                "correct_choice": "A", "explanation": "VPN เข้ารหัสเส้นทางรับส่งข้อมูลระหว่างเครื่องผู้ใช้กับเซิร์ฟเวอร์ VPN ช่วยเพิ่มความปลอดภัยและความเป็นส่วนตัวบนเน็ตสาธารณะ"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ซิลิโคนระบายความร้อน (Thermal Paste) ที่ทาอยู่ระหว่าง CPU กับ Heatsink มีหน้าที่อะไร?",
                "choice_a": "อุดช่องว่างระดับจุลภาคระหว่างผิวสัมผัสเพื่อถ่ายเทความร้อนจาก CPU ไปยังชุดระบายความร้อนได้อย่างมีประสิทธิภาพ", "choice_b": "ติดกาวให้ CPU ไม่หลุดออกจากซ็อกเก็ต", "choice_c": "เป็นฉนวนป้องกันไฟฟ้ารั่วเข้าสู่บอร์ด", "choice_d": "ช่วยเพิ่มความจุหน่วยความจำแคช",
                "correct_choice": "A", "explanation": "Thermal Paste ทำหน้าที่แทนที่ช่องว่างอากาศที่มีคุณสมบัตินำความร้อนแย่ เพื่อช่วยให้การส่งผ่านความร้อนไปยัง Heatsink ราบรื่น"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ข้อใดคือความหมายของ 'Subnet Mask' ในการตั้งค่าเครือข่าย IPv4?",
                "choice_a": "ตัวเลขที่ใช้แบ่งแยกว่าส่วนใดของ IP Address เป็น Network ID และส่วนใดเป็น Host ID", "choice_b": "รหัสลับสำหรับเชื่อมต่อเราเตอร์", "choice_c": "โปรแกรมสำหรับซ่อนชื่อคอมพิวเตอร์", "choice_d": "หมายเลขซีเรียลของการ์ดแลน",
                "correct_choice": "A", "explanation": "Subnet Mask (เช่น 255.255.255.0) ช่วยให้ระบบระบุได้ว่าคอมพิวเตอร์ปลายทางอยู่ในเครือข่ายย่อยเดียวกันหรือเครือข่ายภายนอก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบ 'Default Gateway' ในการตั้งค่าเครือข่ายคอมพิวเตอร์หมายถึงอะไร?",
                "choice_a": "เราเตอร์หรือโหนดที่เป็นประตูทางออกเพื่อส่งข้อมูลออกไปยังเครือข่ายอื่นหรืออินเทอร์เน็ต", "choice_b": "โปรแกรมป้องกันการเข้าเว็บไซต์อันตราย", "choice_c": "พอร์ตเสียบสายชาร์จโน้ตบุ๊ก", "choice_d": "หน้าจอเข้าสู่ระบบของวินโดวส์",
                "correct_choice": "A", "explanation": "Default Gateway เป็นที่อยู่ IP ของเราเตอร์ที่เครื่องคอมพิวเตอร์ใช้เป็นช่องทางหลักในการสื่อสารกับภายนอกเครือข่ายวงแลน"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "เหตุใดแรมมาตรฐาน 'DDR5' จึงมีประสิทธิภาพเหนือกว่า 'DDR4'?",
                "choice_a": "มีแบนด์วิดท์ถ่ายโอนข้อมูลสูงขึ้น มี On-die ECC ในตัว และใช้พลังงานต่ำลง (1.1V)", "choice_b": "มีขนาดแผงวงจรใหญ่กว่า DDR4 สองเท่า", "choice_c": "สามารถเสียบใช้งานบนสล็อตของ DDR4 ได้โดยตรง", "choice_d": "ไม่ต้องใช้กระแสไฟฟ้าในการทำงาน",
                "correct_choice": "A", "explanation": "DDR5 มีความเร็ว Bus เริ่มต้นสูงกว่า DDR4 มาก และรวมระบบจัดการพลังงาน PMIC ไว้บนตัวแผงแรมโดยตรง"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "ระบบไฟล์แบบ 'NTFS' มีฟีเจอร์สำคัญใดเหนือกว่า 'FAT32' ในระบบปฏิบัติการ Windows?",
                "choice_a": "รองรับไฟล์ขนาดใหญ่เกิน 4 GB และมีระบบความปลอดภัย Permissions/Journaling", "choice_b": "ใช้งานได้บนแฟลชไดรฟ์ทุกชนิดโดยไม่ต้องฟอร์แมต", "choice_c": "รองรับเฉพาะไฟล์เพลง MP3 เท่านั้น", "choice_d": "ทำให้คอมพิวเตอร์เปิดติดทันทีใน 1 วินาที",
                "correct_choice": "A", "explanation": "FAT32 รองรับไฟล์เดี่ยวได้ไม่เกิน 4 GB ส่วน NTFS รองรับไฟล์ขนาดใหญ่มาก และมีระบบบันทึกความปลอดภัยของข้อมูล (Journaling)"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "อาการจอฟ้ามรณะ 'Blue Screen of Death' (BSOD) บน Windows มีสาเหตุหลักมาจากสิ่งใด?",
                "choice_a": "เกิดข้อผิดพลาดระดับวิกฤตของเคอร์เนลระบบ (Kernel Fault) หรือฮาร์ดแวร์/ไดรเวอร์ชำรุดจนระบบไม่สามารถทำงานต่อได้อย่างปลอดภัย", "choice_b": "ผู้ใช้เปิดหน้าต่างโปรแกรมมากกว่า 5 หน้าต่าง", "choice_c": "หลอดไฟในจอภาพเปลี่ยนสีเป็นสีน้ำเงิน", "choice_d": "คอมพิวเตอร์ดาวน์โหลดเพลงเสร็จสมบูรณ์",
                "correct_choice": "A", "explanation": "BSOD เป็นกลไกป้องกันความเสียหายของ Windows เมื่อเกิดความผิดพลาดขั้นวิกฤตระดับ Kernel/Driver เพื่อหยุดระบบก่อนข้อมูลเสียหายถาวร"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "พอร์ต 'Thunderbolt' (เช่น Thunderbolt 4) เหนือกว่าพอร์ต USB ทั่วไปในด้านใด?",
                "choice_a": "รวมช่องทาง PCIe, DisplayPort และจ่ายไฟ Power Delivery ด้วยความเร็วสูงสุดถึง 40 Gbps", "choice_b": "สามารถต่อเข้ากับปลั๊กไฟบ้านได้โดยตรง", "choice_c": "ใช้เชื่อมต่อเฉพาะเครื่องพิมพ์เท่านั้น", "choice_d": "เป็นพอร์ตที่ไม่มีวันชำรุด",
                "correct_choice": "A", "explanation": "Thunderbolt มีแบนด์วิดท์สูงมากถึง 40 Gbps สามารถต่อการ์ดจอภายนอก (eGPU) หน้าจอความละเอียดสูง และอุปกรณ์ความเร็วสูงได้ในพอร์ตเดียว"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การเชื่อมต่อดิสก์แบบ 'RAID 0' (Striping) มีข้อควรระวังที่สำคัญที่สุดคือข้อใด?",
                "choice_a": "หากดิสก์ตัวใดตัวหนึ่งเสียหาย ข้อมูลทั้งหมดในชุด RAID จะสูญหายทันทีโดยไม่มีการสำรองข้อมูล", "choice_b": "ความเร็วในการอ่านเขียนจะช้าลงครึ่งหนึ่ง", "choice_c": "ไม่สามารถเก็บไฟล์ขนาดใหญ่ได้", "choice_d": "ต้องใช้ไฟเลี้ยงจากแบตเตอรี่เท่านั้น",
                "correct_choice": "A", "explanation": "RAID 0 นำดิสก์มารวมกันเพื่อแบ่งกระจายข้อมูลเร่งความเร็ว แต่ไม่มี Fault Tolerance เลย หากไดรฟ์เสีย 1 ลูก ข้อมูลพังทั้งหมด"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "มัลแวร์ประเภท 'Ransomware' (มัลแวร์เรียกค่าไถ่) มีพฤติกรรมทำร้ายระบบอย่างไร?",
                "choice_a": "เข้ารหัสไฟล์ทั้งหมดในระบบด้วยอัลกอริทึมที่ซับซ้อน และเรียกร้องเงินค่าไถ่เพื่อแลกกับกุญแจถอดรหัส", "choice_b": "ทำให้พัดลมเคสหมุนเสียงดังตลอดเวลา", "choice_c": "เปลี่ยนภาพพื้นหลังหน้าจอเป็นสีดำ", "choice_d": "ปิดสัญญาณเน็ต Wi-Fi ถาวร",
                "correct_choice": "A", "explanation": "Ransomware ทำการจับไฟล์ข้อมูลสำคัญเป็นตัวประกันโดยการเข้ารหัสลับ (Encryption) ที่แข็งแกร่ง และเรียกร้องเงินสกุลดิจิทัลเพื่อปลดล็อก"
            },
            {
                "category": cat_basic, "difficulty": "ยาก", "is_active": True,
                "text": "การโจมตีทางไซเบอร์แบบ 'DDoS' (Distributed Denial of Service) มีรูปแบบการทำงานอย่างไร?",
                "choice_a": "ระดมส่งคำขอปริมาณมหาศาลจากเครือข่ายบอตเน็ต (Botnet) เข้าใส่เซิร์ฟเวอร์จนทรัพยากรล้นและระบบล่มหยุดให้บริการ", "choice_b": "การแอบดักจับรหัสผ่านผ่านไมโครโฟน", "choice_c": "การตัดสายไฟเบอร์ออปติกใต้ดิน", "choice_d": "การส่งสติกเกอร์ในแชท",
                "correct_choice": "A", "explanation": "DDoS มุ่งเน้นการทำให้บริการหรือเว็บไซต์เป้าหมายล่ม โดยระดมทราฟฟิกข้อมูลขนาดมหาศาลจากเครื่องคอมพิวเตอร์นับหมื่นเครื่องพร้อมกัน"
            },

            # =========================================================================
            # [หมวด: สาขาวิทยาการคอมพิวเตอร์เบื้องต้น] 10 ข้อ
            # =========================================================================
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "หัวใจและแก่นแท้ของการศึกษาใน 'สาขาวิทยาการคอมพิวเตอร์' (Computer Science) มุ่งเน้นศึกษาเกี่ยวกับสิ่งใดเป็นหลัก?",
                "choice_a": "การศึกษาทฤษฎีการคำนวณ ขั้นตอนวิธี (Algorithms) และการแก้ปัญหาเชิงคำนวณอย่างเป็นระบบ", "choice_b": "การซ่อมและประกอบคอมพิวเตอร์หน้าร้าน", "choice_c": "การพิมพ์เอกสารและการใช้โปรแกรมสำนักงาน", "choice_d": "การเดินสายไฟเบอร์ออปติกตามอาคาร",
                "correct_choice": "A", "explanation": "วิทยาการคอมพิวเตอร์ (Computer Science) ศึกษาลึกซึ้งในด้านทฤษฎีการคำนวณ โครงสร้างข้อมูล อัลกอริทึม และการออกแบบระบบซอฟต์แวร์"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "ทักษะ 'การคิดเชิงคำนวณ' (Computational Thinking) ซึ่งเป็นพื้นฐานสำคัญของนักวิทยาการคอมพิวเตอร์ ประกอบด้วย 4 เสาหลักคือข้อใด?",
                "choice_a": "Decomposition (ย่อยปัญหา), Pattern Recognition (หารูปแบบ), Abstraction (คิดเชิงนามธรรม), Algorithm Design (ออกแบบขั้นตอนวิธี)", "choice_b": "Input, Process, Output, Storage", "choice_c": "Coding, Testing, Debugging, Deploying", "choice_d": "Hardware, Software, Peopleware, Data",
                "correct_choice": "A", "explanation": "Computational Thinking 4 เสาหลักคือ การย่อยปัญหาใหญ่, การมองหารูปแบบ, การตัดรายละเอียดที่ไม่จำเป็น, และการออกแบบอัลกอริทึมทีละขั้นตอน"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "วิชา 'Data Structures and Algorithms' (โครงสร้างข้อมูลและขั้นตอนวิธี) มีความสำคัญสูงสุดต่อนักศึกษา CS อย่างไร?",
                "choice_a": "เป็นวิชาหลักในการฝึกจัดเก็บข้อมูลอย่างมีแบบแผนและเลือกใช้อัลกอริทึมที่มีประสิทธิภาพสูงสุดในการแก้ปัญหา", "choice_b": "สอนวิธีการประกอบการ์ดจอและซีพียู", "choice_c": "สอนการวาดภาพกราฟิกด้วย Photoshop", "choice_d": "สอนการติดตั้งระบบปฏิบัติการ Windows",
                "correct_choice": "A", "explanation": "โครงสร้างข้อมูล (เช่น Array, Stack, Tree) และอัลกอริทึม เป็นกระดูกสันหลังในการเขียนโปรแกรมให้มีประสิทธิภาพ ประหยัดเวลา และประหยัดหน่วยความจำ"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "ในการวิเคราะห์ประสิทธิภาพของอัลกอริทึม สัญกรณ์ 'Big-O Notation' (เช่น O(1), O(n), O(n²)) ใช้วัดสิ่งใด?",
                "choice_a": "อัตราการเติบโตของการใช้เวลา (Time Complexity) และการใช้พื้นที่หน่วยความจำ (Space Complexity) เมื่อขนาดข้อมูลนำเข้าเพิ่มขึ้น", "choice_b": "ขนาดความจุของฮาร์ดดิสก์ที่ใช้ติดตั้งโปรแกรม", "choice_c": "จำนวนบรรทัดของโค้ดที่เขียนในโปรแกรม", "choice_d": "ความเร็วในการพิมพ์คีย์บอร์ดของโปรแกรมเมอร์",
                "correct_choice": "A", "explanation": "Big-O ใช้วิเคราะห์และเปรียบเทียบประสิทธิภาพของอัลกอริทึมในกรณีแย่ที่สุด (Worst-case) โดยไม่ขึ้นกับความเร็วของฮาร์ดแวร์"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โครงสร้างข้อมูลพื้นฐานแบบ 'Stack' (สแต็ก) มีคุณลักษณะในการเข้าและออกของข้อมูลแบบใด?",
                "choice_a": "LIFO (Last-In, First-Out: ข้อมูลที่ใส่เข้าไปทีหลังสุดจะถูกดึงออกมาใช้งานก่อน)", "choice_b": "FIFO (First-In, First-Out: ข้อมูลที่เข้ามาก่อนจะได้ออกไปก่อน)", "choice_c": "Random Access (เข้าถึงตำแหน่งใดก็ได้พร้อมกัน)", "choice_d": "Priority First (ข้อมูลที่มีขนาดใหญ่สุดจะออกก่อน)",
                "correct_choice": "A", "explanation": "Stack ทำงานแบบ LIFO เปรียบเสมือนจานที่ซ้อนกัน ใบที่วางบนสุดจะถูกหยิบออกก่อน นิยมใช้ในคำสั่ง Undo และ Call Stack"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "โครงสร้างข้อมูลแบบ 'Queue' (คิว) มีหลักการทำงานในการจัดการข้อมูลอย่างไร?",
                "choice_a": "FIFO (First-In, First-Out: ข้อมูลที่เข้ามาก่อนจะถูกประมวลผลและออกไปก่อน)", "choice_b": "LIFO (Last-In, First-Out)", "choice_c": "Binary Tree Search", "choice_d": "Circular Reverse",
                "correct_choice": "A", "explanation": "Queue ทำงานแบบ FIFO เปรียบเหมือนการเข้าคิวรอซื้อตั๋ว คนที่มาก่อนจะได้รับบริการก่อนเสมอ เช่น Print Queue หรือ Message Queue"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "สายงานและอาชีพใดต่อไปนี้เป็นบทบาทหลักที่ผู้สำเร็จการศึกษาสาขาวิทยาการคอมพิวเตอร์สามารถประกอบอาชีพได้?",
                "choice_a": "Software Engineer, Data Scientist, AI/ML Specialist, และ Cyber Security Analyst", "choice_b": "ช่างเดินสายไฟฟ้าภายในอาคาร", "choice_c": "พนักงานพิมพ์ดีดประจำสำนักงาน", "choice_d": "ช่างซ่อมมอเตอร์ไซค์",
                "correct_choice": "A", "explanation": "บัณฑิตวิทยาการคอมพิวเตอร์มีความรู้ครอบคลุมทั้งการพัฒนาซอฟต์แวร์, ปัญญาประดิษฐ์, วิทยาศาสตร์ข้อมูล และความมั่นคงปลอดภัยไซเบอร์"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "ความแตกต่างหลักระหว่างสาขา 'วิทยาการคอมพิวเตอร์' (CS) และสาขา 'เทคโนโลยีสารสนเทศ' (IT) คือข้อใด?",
                "choice_a": "CS มุ่งเน้นการสร้างสรรค์ ทฤษฎีการคำนวณ พัฒนาซอฟต์แวร์และอัลกอริทึม ส่วน IT เน้นการประยุกต์ใช้และดูแลโครงสร้างพื้นฐานระบบ", "choice_b": "CS เรียนเฉพาะการเล่นเกม ส่วน IT เรียนการซ่อมคอมพิวเตอร์", "choice_c": "IT ต้องเขียนโปรแกรมยากกว่า CS ทุกด้าน", "choice_d": "ทั้งสองสาขาไม่มีความแตกต่างกันเลยในหลักสูตร",
                "correct_choice": "A", "explanation": "Computer Science เน้นวิจัย สร้างสรรค์โค้ด สถาปัตยกรรม และอัลกอริทึม ขณะที่ Information Technology เน้นนำเทคโนโลยีและระบบเครือข่ายมาประยุกต์ใช้ในองค์กร"
            },
            {
                "category": cat_cs, "difficulty": "ปานกลาง", "is_active": True,
                "text": "เครื่องมือ 'Git' และแพลตฟอร์มเช่น 'GitHub' มีความสำคัญอย่างไรต่อนักพัฒนาซอฟต์แวร์?",
                "choice_a": "เป็นระบบควบคุมเวอร์ชัน (Version Control System) ใช้ติดตามประวัติการแก้ไขโค้ดและทำงานร่วมกันในทีม", "choice_b": "เป็นโปรแกรมสำหรับดูหนังและฟังเพลงออนไลน์", "choice_c": "เป็นแอนติไวรัสช่วยสแกนเครื่องคอมพิวเตอร์", "choice_d": "เป็นภาษาโปรแกรมสำหรับการเขียนเว็บ",
                "correct_choice": "A", "explanation": "Git คือ Version Control System มาตรฐานสากลที่ช่วยให้นักพัฒนาหลายคนทำงานบนโค้ดเดียวกันได้โดยไม่ทับซ้อนกัน และบันทึกประวัติการเปลี่ยนแปลงทุกจุด"
            },
            {
                "category": cat_cs, "difficulty": "ยาก", "is_active": True,
                "text": "วิชาคณิตศาสตร์แขนง 'คณิตศาสตร์ไม่ต่อเนื่อง' (Discrete Mathematics) มีความจำเป็นต่อสายงานวิทยาการคอมพิวเตอร์อย่างไร?",
                "choice_a": "เป็นรากฐานของตรรกศาสตร์ (Logic), ทฤษฎีกราฟ (Graph Theory), เซต, และความน่าจะเป็น ซึ่งใช้ในการออกแบบอัลกอริทึมและโครงสร้างข้อมูล", "choice_b": "ใช้คำนวณราคาสินค้าหน้าร้านสะดวกซื้อ", "choice_c": "ใช้สำหรับคำนวณภาษีมูลค่าเพิ่มในใบเสร็จ", "choice_d": "ใช้สำหรับออกแบบกราฟิกสองมิติ",
                "correct_choice": "A", "explanation": "Discrete Math คือรากฐานทางคณิตศาสตร์ของคอมพิวเตอร์ ทั้งตรรกศาสตร์บูลีน, ทฤษฎีกราฟที่ใช้ในเครือข่ายและระบบค้นหา, รวมถึงการพิสูจน์ความถูกต้องของโปรแกรม"
            },
        ]

        # 6. บันทึกคำถามลงใน SQLite
        self.stdout.write(self.style.NOTICE(f"3. กำลังบันทึกคำถาม {len(raw_questions)} ข้อลง SQLite..."))
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

        # 7. ซิงค์ไปยัง Firebase Firestore แบบขนาน (Parallel Fast Sync)
        self.stdout.write(self.style.NOTICE(f"4. กำลังซิงค์คำถาม {success_db} ข้อไปยัง Firebase Firestore..."))
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=15) as executor:
            sync_results = list(executor.map(sync_question_to_firestore, created_questions))
            success_fb = sum(1 for r in sync_results if r)
        self.stdout.write(self.style.SUCCESS(f"[OK] ซิงค์ขึ้น Firebase Firestore สำเร็จ ({success_fb}/{success_db} ข้อ)"))

        # สรุปผล
        self.stdout.write(self.style.SUCCESS(f"\n======================================================="))
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] กระบวนการเสร็จสมบูรณ์ 100%!"))
        self.stdout.write(self.style.SUCCESS(f"  - บันทึกลง SQLite: {success_db}/{len(raw_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - ซิงค์ขึ้น Firebase: {success_fb}/{len(raw_questions)} ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวดคอมพิวเตอร์เบื้องต้น: ง่าย 40 ข้อ, ปานกลาง 25 ข้อ, ยาก 25 ข้อ (รวม 90 ข้อ)"))
        self.stdout.write(self.style.SUCCESS(f"  - หมวดสาขาวิทยาการคอมพิวเตอร์เบื้องต้น: 10 ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"  - รวมทั้งหมด: 100 ข้อ"))
        self.stdout.write(self.style.SUCCESS(f"======================================================="))
