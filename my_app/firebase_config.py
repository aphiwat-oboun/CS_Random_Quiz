"""
Firebase Firestore Integration for CS Random Quiz.
ใช้ Firebase Web Config (apiKey, projectId, appId) เชื่อมต่อง่ายๆ โดยไม่ต้องใช้ Private Key!
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
    return bool(FIREBASE_PROJECT_ID)


def sync_question_to_firestore(question):
    """
    บันทึกคำถามไปยัง Firebase Firestore ผ่าน REST API โดยใช้เพียง Project ID (ไม่ต้องใช้ Private Key)
    """
    if not FIREBASE_PROJECT_ID:
        return False

    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/questions/{question.id}"
    payload = {
        "fields": {
            "id": {"integerValue": str(question.id)},
            "text": {"stringValue": question.text},
            "category": {"stringValue": question.category.name},
            "choice_a": {"stringValue": question.choice_a},
            "choice_b": {"stringValue": question.choice_b},
            "choice_c": {"stringValue": question.choice_c},
            "choice_d": {"stringValue": question.choice_d},
            "correct_choice": {"stringValue": question.correct_choice},
            "explanation": {"stringValue": question.explanation or ""},
            "difficulty": {"stringValue": question.difficulty},
            "is_active": {"booleanValue": question.is_active},
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="PATCH")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Firebase REST Sync Notice] {e}")
        return False


def delete_question_from_firestore(question_id):
    """ลบคำถามออกจาก Firestore ผ่าน REST API"""
    if not FIREBASE_PROJECT_ID:
        return False

    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/questions/{question_id}"
    try:
        req = urllib.request.Request(url, method="DELETE")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[Firebase REST Delete Notice] {e}")
        return False


def sync_quiz_log_to_firestore(question_id, question_text, category_name, correct_choice):
    """บันทึกประวัติการเล่นไปยัง Firestore quiz_logs ผ่าน REST API"""
    if not FIREBASE_PROJECT_ID:
        return False

    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/quiz_logs"
    payload = {
        "fields": {
            "question_id": {"integerValue": str(question_id)},
            "question_text": {"stringValue": question_text},
            "category": {"stringValue": category_name},
            "correct_choice": {"stringValue": correct_choice},
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[Firebase REST Log Notice] {e}")
        return False
