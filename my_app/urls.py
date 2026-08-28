from django.urls import path
from . import views

urlpatterns = [
    # 1. หน้าเวทีและผู้เล่น (Stage & Player Flow)
    path("", views.home_view, name="home"),
    path("quiz/random/", views.random_quiz_view, name="random_quiz"),
    path("quiz/reset-session/", views.reset_quiz_session_view, name="reset_quiz_session"),
    path("quiz/rolling/<int:question_id>/", views.rolling_animation_view, name="rolling_animation"),
    path("quiz/question/<int:question_id>/", views.question_view, name="question_view"),
    path("quiz/answer/<int:question_id>/", views.answer_view, name="answer_view"),

    # 2. ระบบเข้าสู่ระบบแอดมิน (Admin Authentication)
    path("admin-panel/login/", views.admin_login_view, name="admin_login"),
    path("admin-panel/logout/", views.admin_logout_view, name="admin_logout"),

    # 3. แดชบอร์ดแอดมิน (Admin Dashboard)
    path("admin-panel/dashboard/", views.admin_dashboard_view, name="admin_dashboard"),

    # 4. จัดการคำถาม (Question Management)
    path("admin-panel/questions/", views.admin_question_list_view, name="admin_question_list"),
    path("admin-panel/question/add/", views.admin_question_add_view, name="admin_question_add"),
    path("admin-panel/question/edit/<int:question_id>/", views.admin_question_edit_view, name="admin_question_edit"),
    path("admin-panel/question/delete/<int:question_id>/", views.admin_question_delete_view, name="admin_question_delete"),
    path("admin-panel/question/toggle/<int:question_id>/", views.admin_question_toggle_active_view, name="admin_question_toggle"),
    path("admin-panel/sync-firebase/", views.admin_sync_firebase_view, name="admin_sync_firebase"),

    # 5. จัดการประเภทคำถาม (Category Management)
    path("admin-panel/categories/", views.admin_category_list_view, name="admin_category_list"),
    path("admin-panel/category/edit/<int:category_id>/", views.admin_category_edit_view, name="admin_category_edit"),
    path("admin-panel/category/delete/<int:category_id>/", views.admin_category_delete_view, name="admin_category_delete"),

    # 6. สถิติการใช้งานและการตั้งค่า (Logs & Settings)
    path("admin-panel/logs/", views.admin_logs_view, name="admin_logs"),
    path("admin-panel/settings/", views.admin_settings_view, name="admin_settings"),

    # 7. Real-time Firebase Background Sync API
    path("api/sync-firestore/", views.api_sync_firestore_view, name="api_sync_firestore"),
]
