# 🔥 คู่มือการตั้งค่า Firebase Web Config และ Deploy ลง Vercel

ระบบรองรับการเชื่อมต่อกับ **Firebase** ผ่าน **Firebase Web Config** (`apiKey`, `projectId`, `authDomain`, `appId`) โดยตรง **ไม่ต้องสร้าง Service Account หรือ Private Key ให้ยุ่งยากอีกต่อไป!**

---

## 1. ค่า Firebase Config ที่ใช้งานในโปรเจกต์

คุณสามารถนำค่า `firebaseConfig` จาก Firebase Console มาใส่ใน `.env` หรือตั้งค่าใน Vercel ได้ทันที:

```env
FIREBASE_PROJECT_ID="random-cs-57d01"
FIREBASE_API_KEY="AIzaSyCASWXjm222OjJ1Bm90on46qNA0dPLuwkE"
FIREBASE_AUTH_DOMAIN="random-cs-57d01.firebaseapp.com"
FIREBASE_STORAGE_BUCKET="random-cs-57d01.firebasestorage.app"
FIREBASE_MESSAGING_SENDER_ID="967552966443"
FIREBASE_APP_ID="1:967552966443:web:5ca944015aebd47fff2f6e"
```

---

## 2. ขั้นตอนการ Deploy ขึ้น Vercel

1. Push โค้ดขึ้น GitHub Repository
2. ไปที่ [Vercel Dashboard](https://vercel.com/dashboard) กด **Add New Project**
3. เพิ่ม Environment Variable บน Vercel:
   - `FIREBASE_PROJECT_ID`: `random-cs-57d01`
   - `FIREBASE_API_KEY`: `AIzaSyCASWXjm222OjJ1Bm90on46qNA0dPLuwkE`
   - `SECRET_KEY`: `django-insecure-cs-random-quiz-super-key-2026`
4. กด **Deploy** สำเร็จทันที!
