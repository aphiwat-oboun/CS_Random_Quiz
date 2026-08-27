import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Category, Question, QuizLog
from .forms import QuestionForm, CategoryForm
from .firebase_config import (
    sync_quiz_log_to_firestore, 
    sync_question_to_firestore, 
    delete_question_from_firestore
)


# ==========================================
# 1. หน้าเวที / ผู้เล่น (Player & Stage Views)
# ==========================================

def home_view(request):
    """หน้าหลัก Stage Mode พร้อมบรรยากาศเวทีสปอตไลท์และปุ่มสุ่ม"""
    total_questions = Question.objects.filter(is_active=True).count()
    return render(request, "home.html", {
        "total_questions": total_questions,
    })


def random_quiz_view(request):
    """
    ระบบสุ่มคำถามแบบไม่ซ้ำ (จนกว่าจะครบทุกข้อ)
    ใช้ Django Session เก็บ ID คำถามที่เล่นไปแล้ว
    """
    active_questions = list(Question.objects.filter(is_active=True).values_list("id", flat=True))
    
    if not active_questions:
        messages.warning(request, "ยังไม่มีคำถามที่เปิดใช้งานในระบบ กรุณาเพิ่มคำถามก่อน")
        return redirect("home")
    
    # ดึงรายการข้อที่เคยสุ่มไปแล้วจาก session
    played_ids = request.session.get("played_question_ids", [])
    
    # กรองเฉพาะข้อที่ยังไม่ได้เล่น
    unplayed_ids = [qid for qid in active_questions if qid not in played_ids]
    
    # หากสุ่มครบหมดทุกข้อแล้ว ให้รีเซ็ตประวัติการสุ่มใน session เพื่อเริ่มรอบใหม่
    if not unplayed_ids:
        played_ids = []
        unplayed_ids = active_questions
    
    # สุ่มเลือก 1 ข้อ
    chosen_id = random.choice(unplayed_ids)
    played_ids.append(chosen_id)
    request.session["played_question_ids"] = played_ids
    
    # ส่งต่อไปยังหน้าแสดง Animation สล็อตตัวเลข
    return redirect("rolling_animation", question_id=chosen_id)


def rolling_animation_view(request, question_id):
    """หน้าจำลองแอนิเมชันสล็อตสุ่มตัวเลข 7 ช่อง ก่อนแสดงคำถามจริง"""
    question = get_object_or_404(Question, id=question_id, is_active=True)
    all_active_ids = list(Question.objects.filter(is_active=True).order_by("id").values_list("id", flat=True))
    
    # หาว่าคำถามนี้เป็นคำถามลำดับที่เท่าไรในระบบ
    try:
        question_index = all_active_ids.index(question.id) + 1
    except ValueError:
        question_index = question.id

    return render(request, "random_animation.html", {
        "question": question,
        "question_number": question_index,
        "question_id": question.id,
    })


def question_view(request, question_id):
    """หน้าแสดงคำถามขนาดใหญ่บนเวที พร้อมตัวจับเวลานับถอยหลัง 15 วินาที"""
    question = get_object_or_404(Question, id=question_id)
    all_active_ids = list(Question.objects.filter(is_active=True).order_by("id").values_list("id", flat=True))
    
    try:
        current_number = all_active_ids.index(question.id) + 1
    except ValueError:
        current_number = question.id
        
    total_active = len(all_active_ids)

    return render(request, "question.html", {
        "question": question,
        "current_number": current_number,
        "total_active": total_active,
    })


def answer_view(request, question_id):
    """หน้าแสดงเฉลยคำตอบ พร้อมบันทึกสถิติการเล่นลง QuizLog และซิงค์ไปยัง Firebase Firestore (ถ้าเชื่อมต่อไว้)"""
    question = get_object_or_404(Question, id=question_id)
    
    # 1. บันทึกประวัติการเล่นลงฐานข้อมูล Django ORM
    QuizLog.objects.create(question=question)

    # 2. ซิงค์ประวัติไปยัง Firebase Firestore อัตโนมัติ (หากมีการตั้งค่า)
    sync_quiz_log_to_firestore(
        question_id=question.id,
        question_text=question.text,
        category_name=question.category.name,
        correct_choice=question.correct_choice
    )

    return render(request, "answer.html", {
        "question": question,
    })


# ==========================================
# 2. ระบบเข้าสู่ระบบแอดมิน (Admin Routing)
# ==========================================

def admin_login_view(request):
    """ส่งต่อไปยังหน้า Admin Dashboard ทันทีโดยไม่ต้องล็อกอิน"""
    return redirect("admin_dashboard")


def admin_logout_view(request):
    """กลับสู่หน้าหลัก"""
    messages.info(request, "กลับสู่หน้าหลักเรียบร้อยแล้ว")
    return redirect("home")


# ==========================================
# 3. แดชบอร์ดและสถิติ (Admin Dashboard & Analytics)
# ==========================================

def admin_dashboard_view(request):
    """หน้าแดชบอร์ดหลักของแอดมิน สรุปการ์ด 4 ใบ และกราฟโดนัทหมวดหมู่คำถาม"""
    total_questions = Question.objects.count()
    active_questions = Question.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_played = QuizLog.objects.count()

    # ข้อมูลสำหรับกราฟโดนัท (Doughnut Chart)
    categories = Category.objects.annotate(q_count=Count("questions")).filter(q_count__gt=0)
    
    chart_labels = []
    chart_data = []
    chart_colors = []
    category_breakdown = []
    
    # ถ้ามีคำถามทั้งหมด ให้คำนวณ %
    total_in_categories = sum([c.q_count for c in categories]) if categories else 0

    for cat in categories:
        chart_labels.append(cat.name)
        chart_data.append(cat.q_count)
        chart_colors.append(cat.color or "#3b82f6")
        
        pct = round((cat.q_count / total_in_categories * 100), 1) if total_in_categories > 0 else 0
        category_breakdown.append({
            "name": cat.name,
            "count": cat.q_count,
            "color": cat.color,
            "percentage": pct,
        })

    # รายการบันทึกการเล่นล่าสุด
    recent_logs = QuizLog.objects.select_related("question", "question__category").order_by("-played_at")[:5]

    context = {
        "total_questions": total_questions,
        "active_questions": active_questions,
        "total_categories": total_categories,
        "total_played": total_played,
        "chart_labels_json": json.dumps(chart_labels, ensure_ascii=False),
        "chart_data_json": json.dumps(chart_data),
        "chart_colors_json": json.dumps(chart_colors),
        "category_breakdown": category_breakdown,
        "recent_logs": recent_logs,
    }
    return render(request, "admin_dashboard.html", context)


# ==========================================
# 4. การจัดการคำถาม (Question Management CRUD)
# ==========================================

def admin_question_list_view(request):
    """หน้ารายการจัดการคำถาม พร้อมระบบค้นหาและตัวกรองตามหมวดหมู่"""
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")
    status = request.GET.get("status", "")

    questions = Question.objects.select_related("category").order_by("-created_at")

    if query:
        questions = questions.filter(text__icontains=query)
    if category_id:
        questions = questions.filter(category_id=category_id)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if status == "active":
        questions = questions.filter(is_active=True)
    elif status == "inactive":
        questions = questions.filter(is_active=False)

    paginator = Paginator(questions, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, "question_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "selected_difficulty": difficulty,
        "selected_status": status,
        "total_count": questions.count(),
    })


def admin_question_add_view(request):
    """หน้าเพิ่มคำถามใหม่ ฟอร์ม 2 คอลัมน์ตาม Mockup พร้อมซิงค์ Firebase"""
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save()
            sync_question_to_firestore(q)
            messages.success(request, "บันทึกคำถามใหม่เรียบร้อยแล้ว (ซิงค์ Firebase สำเร็จ)!")
            return redirect("admin_question_list")
    else:
        form = QuestionForm()

    return render(request, "question_form.html", {
        "form": form,
        "is_edit": False,
        "title": "เพิ่มคำถามใหม่",
    })


def admin_question_edit_view(request, question_id):
    """หน้าแก้ไขคำถาม พร้อมซิงค์ Firebase"""
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            q = form.save()
            sync_question_to_firestore(q)
            messages.success(request, "อัปเดตข้อมูลคำถามเรียบร้อยแล้ว (ซิงค์ Firebase สำเร็จ)!")
            return redirect("admin_question_list")
    else:
        form = QuestionForm(instance=question)

    return render(request, "question_form.html", {
        "form": form,
        "is_edit": True,
        "question": question,
        "title": f"แก้ไขคำถาม #{question.id}",
    })


def admin_question_delete_view(request, question_id):
    """ลบคำถาม และลบออกจาก Firebase Firestore"""
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        delete_question_from_firestore(question.id)
        question.delete()
        messages.success(request, "ลบคำถามสำเร็จแล้ว")
        return redirect("admin_question_list")
    return render(request, "confirm_delete.html", {
        "object": question,
        "type": "คำถาม",
        "cancel_url": "admin_question_list",
    })


def admin_question_toggle_active_view(request, question_id):
    """เปิด/ปิด การใช้งานคำถามอย่างรวดเร็ว"""
    question = get_object_or_404(Question, id=question_id)
    question.is_active = not question.is_active
    question.save()
    status_text = "เปิดใช้งาน" if question.is_active else "ปิดการใช้งาน"
    messages.info(request, f"{status_text} คำถาม #{question.id} แล้ว")
    return redirect(request.META.get("HTTP_REFERER", "admin_question_list"))


# ==========================================
# 5. การจัดการประเภทคำถาม (Category Management CRUD)
# ==========================================

def admin_category_list_view(request):
    """หน้ารายการและเพิ่มประเภทคำถาม"""
    categories = Category.objects.annotate(q_count=Count("questions")).order_by("id")
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มประเภทคำถามใหม่สำเร็จ!")
            return redirect("admin_category_list")
    else:
        form = CategoryForm()

    return render(request, "category_list.html", {
        "categories": categories,
        "form": form,
    })


def admin_category_edit_view(request, category_id):
    """แก้ไขประเภทคำถาม"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "อัปเดตประเภทคำถามเรียบร้อยแล้ว!")
            return redirect("admin_category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "category_form.html", {
        "form": form,
        "category": category,
    })


def admin_category_delete_view(request, category_id):
    """ลบประเภทคำถาม"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "ลบประเภทคำถามเรียบร้อยแล้ว")
        return redirect("admin_category_list")
    return render(request, "confirm_delete.html", {
        "object": category,
        "type": "ประเภทคำถาม",
        "cancel_url": "admin_category_list",
    })


# ==========================================
# 6. ประวัติการเล่นและการตั้งค่า (Logs & Settings)
# ==========================================

def admin_logs_view(request):
    """หน้าดูประวัติการสุ่มคำถามทั้งหมด"""
    logs = QuizLog.objects.select_related("question", "question__category").order_by("-played_at")
    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "log_list.html", {
        "page_obj": page_obj,
        "total_count": logs.count(),
    })


def admin_settings_view(request):
    """หน้าตั้งค่าและรีเซ็ตประวัติการสุ่ม"""
    if request.method == "POST" and "reset_session" in request.POST:
        request.session["played_question_ids"] = []
        messages.success(request, "รีเซ็ตคลังคำถามที่สุ่มไปแล้วเรียบร้อย!")
        return redirect("admin_settings")

    if request.method == "POST" and "clear_logs" in request.POST:
        QuizLog.objects.all().delete()
        messages.success(request, "ล้างประวัติการสุ่มคำถามทั้งหมดเรียบร้อย!")
        return redirect("admin_settings")

    played_ids = request.session.get("played_question_ids", [])
    active_count = Question.objects.filter(is_active=True).count()

    return render(request, "admin_settings.html", {
        "played_count": len(played_ids),
        "active_count": active_count,
    })
