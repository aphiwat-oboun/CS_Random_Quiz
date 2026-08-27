from django.db import models


class Category(models.Model):
    """โมเดลสำหรับจัดหมวดหมู่ประเภทของคำถาม"""
    name = models.CharField(max_length=100, verbose_name="ชื่อประเภทคำถาม")
    color = models.CharField(
        max_length=20, 
        default="#3b82f6", 
        verbose_name="รหัสสี HEX (สำหรับกราฟ/ป้าย)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")

    class Meta:
        verbose_name = "ประเภทคำถาม"
        verbose_name_plural = "ประเภทคำถามทั้งหมด"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Question(models.Model):
    """โมเดลสำหรับเก็บคำถาม ตัวเลือก และเฉลย"""
    DIFFICULTY_CHOICES = [
        ("ง่าย", "ง่าย"),
        ("ปานกลาง", "ปานกลาง"),
        ("ยาก", "ยาก"),
    ]

    CORRECT_CHOICES = [
        ("A", "ตัวเลือก A"),
        ("B", "ตัวเลือก B"),
        ("C", "ตัวเลือก C"),
        ("D", "ตัวเลือก D"),
    ]

    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="questions",
        verbose_name="ประเภทคำถาม"
    )
    text = models.TextField(verbose_name="ข้อความคำถาม")
    choice_a = models.CharField(max_length=255, verbose_name="ตัวเลือก A")
    choice_b = models.CharField(max_length=255, verbose_name="ตัวเลือก B")
    choice_c = models.CharField(max_length=255, verbose_name="ตัวเลือก C")
    choice_d = models.CharField(max_length=255, verbose_name="ตัวเลือก D")
    correct_choice = models.CharField(
        max_length=1, 
        choices=CORRECT_CHOICES, 
        default="A", 
        verbose_name="คำตอบที่ถูกต้อง"
    )
    explanation = models.TextField(
        blank=True, 
        verbose_name="คำอธิบายเฉลย"
    )
    difficulty = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_CHOICES, 
        default="ง่าย", 
        verbose_name="ระดับความยาก"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="เปิดใช้งาน"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="สร้างเมื่อ"
    )

    class Meta:
        verbose_name = "คำถาม"
        verbose_name_plural = "คำถามทั้งหมด"
        ordering = ["id"]

    def __str__(self):
        return f"[{self.category.name}] {self.text[:50]}"

    @property
    def correct_answer_text(self):
        """ส่งคืนข้อความตัวเลือกที่เป็นคำตอบที่ถูกต้อง"""
        mapping = {
            "A": self.choice_a,
            "B": self.choice_b,
            "C": self.choice_c,
            "D": self.choice_d,
        }
        return mapping.get(self.correct_choice, "")


class QuizLog(models.Model):
    """โมเดลบันทึกประวัติการสุ่มและแสดงคำถาม"""
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name="logs",
        verbose_name="คำถามที่เล่น"
    )
    played_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="เวลาที่เล่น"
    )
    is_correct = models.BooleanField(
        null=True, 
        blank=True, 
        verbose_name="ตอบถูกต้องหรือไม่"
    )

    class Meta:
        verbose_name = "ประวัติการสุ่มคำถาม"
        verbose_name_plural = "ประวัติการสุ่มคำถามทั้งหมด"
        ordering = ["-played_at"]

    def __str__(self):
        return f"Log #{self.id}: Question #{self.question.id} at {self.played_at.strftime('%Y-%m-%d %H:%M')}"
