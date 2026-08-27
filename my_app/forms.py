from django import forms
from .models import Question, Category


class QuestionForm(forms.ModelForm):
    """ฟอร์มสำหรับเพิ่ม/แก้ไขคำถาม ปรับแต่ง Widget ให้ตรงกับ UI Mockup"""
    class Meta:
        model = Question
        fields = [
            "category",
            "text",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
            "difficulty",
            "explanation",
            "correct_choice",
            "is_active",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select", "id": "id_category"}),
            "text": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 3, 
                "placeholder": "ระบุข้อความคำถาม",
                "id": "id_text"
            }),
            "choice_a": forms.TextInput(attrs={"class": "form-control", "placeholder": "ระบุตัวเลือก A", "id": "id_choice_a"}),
            "choice_b": forms.TextInput(attrs={"class": "form-control", "placeholder": "ระบุตัวเลือก B", "id": "id_choice_b"}),
            "choice_c": forms.TextInput(attrs={"class": "form-control", "placeholder": "ระบุตัวเลือก C", "id": "id_choice_c"}),
            "choice_d": forms.TextInput(attrs={"class": "form-control", "placeholder": "ระบุตัวเลือก D", "id": "id_choice_d"}),
            "difficulty": forms.Select(attrs={"class": "form-select", "id": "id_difficulty"}),
            "explanation": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 4, 
                "placeholder": "อธิบายคำตอบ (จะแสดงตอนเฉลย)",
                "id": "id_explanation"
            }),
            "correct_choice": forms.Select(attrs={"class": "form-select", "id": "id_correct_choice"}),
            "is_active": forms.CheckboxInput(attrs={"class": "toggle-switch-input", "id": "id_is_active"}),
        }
        labels = {
            "category": "ประเภทคำถาม",
            "text": "คำถาม",
            "choice_a": "ตัวเลือก A",
            "choice_b": "ตัวเลือก B",
            "choice_c": "ตัวเลือก C",
            "choice_d": "ตัวเลือก D",
            "difficulty": "ระดับความยาก",
            "explanation": "คำอธิบาย (เฉลย)",
            "correct_choice": "คำตอบที่ถูกต้อง",
            "is_active": "เปิดใช้งาน",
        }


class CategoryForm(forms.ModelForm):
    """ฟอร์มสำหรับเพิ่ม/แก้ไขประเภทคำถาม"""
    class Meta:
        model = Category
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "เช่น ความรู้ CS, Programming", "id": "id_name"}),
            "color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color", "id": "id_color"}),
        }
        labels = {
            "name": "ชื่อประเภทคำถาม",
            "color": "สีประจำประเภท",
        }
