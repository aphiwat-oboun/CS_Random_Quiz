"""
Firebase Firestore Integration for CS Random Quiz.
ใช้ Firebase Web Config (apiKey, projectId, appId) เชื่อมต่อ Firestore ผ่าน REST API
รองรับการ Sync ข้อมูลคำถามแบบสองทาง (Two-way Synchronization)
"""
import os
import json
import urllib.request
import urllib.error

# Project Config Defaults (ดึงจาก Env หรือค่าเริ่มต้นของโปรเจกต์)
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "random-cs-57d01")
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "AIzaSyCASWXjm222OjJ1Bm90on46qNA0dPLuwkE")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "random-cs-57d01.firebaseapp.com")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "random-cs-57d01.firebasestorage.app")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "967552966443")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "1:967552966443:web:5ca944015aebd47fff2f6e")


def is_firebase_connected():
    """ตรวจสอบว่ามีการตั้งค่า Project ID หรือไม่"""
    return bool(FIREBASE_PROJECT_ID and FIREBASE_API_KEY)


def sync_question_to_firestore(question):
    """
    บันทึกคำถามไปยัง Firebase Firestore ผ่าน REST API
    """
    if not FIREBASE_PROJECT_ID:
        return False

    api_key_query = f"?key={FIREBASE_API_KEY}" if FIREBASE_API_KEY else ""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/questions/{question.id}{api_key_query}"
    payload = {
        "fields": {
            "id": {"integerValue": str(question.id)},
            "text": {"stringValue": str(question.text)},
            "category": {"stringValue": str(question.category.name if question.category else "ทั่วไป")},
            "choice_a": {"stringValue": str(question.choice_a)},
            "choice_b": {"stringValue": str(question.choice_b)},
            "choice_c": {"stringValue": str(question.choice_c)},
            "choice_d": {"stringValue": str(question.choice_d)},
            "correct_choice": {"stringValue": str(question.correct_choice)},
            "explanation": {"stringValue": str(question.explanation or "")},
            "difficulty": {"stringValue": str(question.difficulty)},
            "is_active": {"booleanValue": bool(question.is_active)},
        }
    }

    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json; charset=utf-8"}, 
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Firebase REST Sync Question Notice] {e}")
        return False


def delete_question_from_firestore(question_id):
    """ลบคำถามออกจาก Firestore ผ่าน REST API"""
    if not FIREBASE_PROJECT_ID:
        return False

    api_key_query = f"?key={FIREBASE_API_KEY}" if FIREBASE_API_KEY else ""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/questions/{question_id}{api_key_query}"
    try:
        req = urllib.request.Request(url, method="DELETE")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[Firebase REST Delete Question Notice] {e}")
        return False


def sync_quiz_log_to_firestore(question_id, question_text, category_name, correct_choice):
    """บันทึกประวัติการเล่นไปยัง Firestore quiz_logs ผ่าน REST API"""
    if not FIREBASE_PROJECT_ID:
        return False

    api_key_query = f"?key={FIREBASE_API_KEY}" if FIREBASE_API_KEY else ""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/quiz_logs{api_key_query}"
    payload = {
        "fields": {
            "question_id": {"integerValue": str(question_id)},
            "question_text": {"stringValue": str(question_text)},
            "category": {"stringValue": str(category_name)},
            "correct_choice": {"stringValue": str(correct_choice)},
        }
    }

    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json; charset=utf-8"}, 
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[Firebase REST Log Notice] {e}")
        return False


def fetch_all_questions_from_firestore():
    """ดึงข้อมูลคำถามทั้งหมดจาก Firestore (รองรับ Pagination)"""
    if not FIREBASE_PROJECT_ID:
        return []

    docs = []
    page_token = ""
    api_key_query = f"&key={FIREBASE_API_KEY}" if FIREBASE_API_KEY else ""

    try:
        while True:
            token_param = f"&pageToken={page_token}" if page_token else ""
            url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/questions?pageSize=100{api_key_query}{token_param}"
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs.extend(data.get("documents", []))
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
        return docs
    except Exception as e:
        print(f"[Firebase Fetch Questions Notice] {e}")
        return []


def sync_firestore_to_sqlite():
    """
    ดึงข้อมูลคำถามทั้งหมดจาก Firebase Firestore มาบันทึกลงใน SQLite
    ส่งคืนจำนวนคำถามที่ซิงค์สำเร็จ
    """
    docs = fetch_all_questions_from_firestore()
    if not docs:
        return 0

    try:
        from my_app.models import Question, Category
        synced_count = 0
        valid_ids = []

        for doc in docs:
            fields = doc.get("fields", {})
            doc_name = doc.get("name", "").split("/")[-1]
            raw_id = fields.get("id", {}).get("integerValue") or doc_name
            try:
                qid = int(raw_id)
            except (ValueError, TypeError):
                qid = None

            cat_name = fields.get("category", {}).get("stringValue", "คอมพิวเตอร์เบื้องต้น")
            category, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={"color": "#8b5cf6" if ("วิทยาการ" in cat_name or "CS" in cat_name) else "#0ea5e9"}
            )

            defaults = {
                "category": category,
                "text": fields.get("text", {}).get("stringValue", ""),
                "choice_a": fields.get("choice_a", {}).get("stringValue", ""),
                "choice_b": fields.get("choice_b", {}).get("stringValue", ""),
                "choice_c": fields.get("choice_c", {}).get("stringValue", ""),
                "choice_d": fields.get("choice_d", {}).get("stringValue", ""),
                "correct_choice": fields.get("correct_choice", {}).get("stringValue", "A"),
                "explanation": fields.get("explanation", {}).get("stringValue", ""),
                "difficulty": fields.get("difficulty", {}).get("stringValue", "ง่าย"),
                "is_active": fields.get("is_active", {}).get("booleanValue", True),
            }

            if qid:
                obj, _ = Question.objects.update_or_create(id=qid, defaults=defaults)
                valid_ids.append(obj.id)
            else:
                obj = Question.objects.create(**defaults)
                valid_ids.append(obj.id)
            synced_count += 1

        # ซิงค์คำถามใน SQLite ที่ยังไม่มีบน Firestore ส่งขึ้นไปเพิ่ม (Additive Two-way Merge ไม่ลบข้อมูลเดิม)
        missing_on_cloud = Question.objects.exclude(id__in=valid_ids)
        for local_q in missing_on_cloud:
            sync_question_to_firestore(local_q)

        return synced_count
    except Exception as e:
        print(f"[Firebase Sync to SQLite Notice] {e}")
        return 0


def sync_all_sqlite_to_firestore():
    """
    ส่งข้อมูลคำถามทั้งหมดจาก SQLite ไปเก็บไว้ใน Firebase Firestore
    """
    try:
        from my_app.models import Question
        questions = Question.objects.all()
        success_count = 0
        for q in questions:
            if sync_question_to_firestore(q):
                success_count += 1
        return success_count
    except Exception as e:
        print(f"[Firebase Sync to Firestore Notice] {e}")
        return 0
