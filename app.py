from __future__ import annotations

import os
import sqlite3
import json
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # python-dotenv yoksa .env okunmaz ama os.getenv yine çalışır


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "takvim.db"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me")


def _table_columns(db: sqlite3.Connection, table: str) -> set[str]:
    rows = db.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def ensure_learn_schema(db: sqlite3.Connection) -> None:
    """Creates PPL learning platform tables (additive - never drops existing data)."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS learn_subjects (
            id         TEXT    PRIMARY KEY,
            code       TEXT    NOT NULL DEFAULT '',
            title      TEXT    NOT NULL,
            icon       TEXT    DEFAULT '📖',
            color      TEXT    DEFAULT '#3b82f6',
            overview   TEXT    DEFAULT '',
            sort_order INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS learn_chapters (
            id            TEXT    PRIMARY KEY,
            subject_id    TEXT    NOT NULL REFERENCES learn_subjects(id),
            title         TEXT    NOT NULL,
            sort_order    INTEGER DEFAULT 0,
            exam_relevant INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS learn_sections (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id TEXT    NOT NULL REFERENCES learn_chapters(id),
            type       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            extra      TEXT    DEFAULT NULL,
            sort_order INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS learn_quiz (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id  TEXT    NOT NULL REFERENCES learn_chapters(id),
            question    TEXT    NOT NULL,
            options     TEXT    NOT NULL,
            answer      INTEGER NOT NULL,
            explanation TEXT    DEFAULT '',
            is_official INTEGER DEFAULT 0,
            sort_order  INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS learn_flashcards (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id TEXT    NOT NULL REFERENCES learn_chapters(id),
            front      TEXT    NOT NULL,
            back       TEXT    NOT NULL,
            sort_order INTEGER DEFAULT 0
        )
    """)
    try:
        db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS learn_fts USING fts5(
                chapter_id    UNINDEXED,
                subject_id    UNINDEXED,
                chapter_title,
                subject_title UNINDEXED,
                content,
                tokenize = 'unicode61 remove_diacritics 1'
            )
        """)
    except Exception:
        pass
    db.commit()


def ensure_schema(db: sqlite3.Connection) -> None:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            color TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            color TEXT,
            username TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(date, user_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            comment TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            token TEXT
        )
    """)
    res_cols = _table_columns(db, "reservations")
    if "username"  not in res_cols: db.execute("ALTER TABLE reservations ADD COLUMN username TEXT")
    if "timestamp" not in res_cols: db.execute("ALTER TABLE reservations ADD COLUMN timestamp TEXT")
    if "color"     not in res_cols: db.execute("ALTER TABLE reservations ADD COLUMN color TEXT")
    user_cols = _table_columns(db, "users")
    if "color"    not in user_cols: db.execute("ALTER TABLE users ADD COLUMN color TEXT")
    if "email"    not in user_cols: db.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
    if "is_admin" not in user_cols:
        db.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        # Hiç admin yoksa ilk kaydı admin yap
        db.execute("UPDATE users SET is_admin = 1 WHERE id = (SELECT MIN(id) FROM users)")
    elif not db.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone():
        # Kolon var ama admin atanmamışsa yine ilk kaydı admin yap
        db.execute("UPDATE users SET is_admin = 1 WHERE id = (SELECT MIN(id) FROM users)")
    com_cols = _table_columns(db, "comments")
    if "timestamp" not in com_cols: db.execute("ALTER TABLE comments ADD COLUMN timestamp TEXT")
    tok_cols = _table_columns(db, "reset_tokens")
    if "expires_at" not in tok_cols: db.execute("ALTER TABLE reset_tokens ADD COLUMN expires_at TEXT")

    ensure_learn_schema(db)
    ensure_private_calendar_schema(db)
    ensure_services_schema(db)
    ensure_day_notes_schema(db)
    db.commit()


def ensure_day_notes_schema(db) -> None:
    """Per-day notes on the shared calendar."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS day_notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date       TEXT    NOT NULL,
            note       TEXT    NOT NULL,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date)
        )
    """)
    db.commit()


def ensure_private_calendar_schema(db: sqlite3.Connection) -> None:
    """Creates private calendar tables (additive – never drops existing data)."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS private_calendars (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name       TEXT    NOT NULL DEFAULT 'Özel Takvimim',
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS private_invites (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar_id INTEGER NOT NULL REFERENCES private_calendars(id) ON DELETE CASCADE,
            invitee_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status      TEXT    NOT NULL DEFAULT 'pending',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(calendar_id, invitee_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS private_notifications (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            calendar_id      INTEGER NOT NULL REFERENCES private_calendars(id) ON DELETE CASCADE,
            invited_by_name  TEXT    NOT NULL,
            calendar_name    TEXT    NOT NULL,
            created_at       TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS private_reservations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar_id INTEGER NOT NULL REFERENCES private_calendars(id) ON DELETE CASCADE,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date        TEXT    NOT NULL,
            color       TEXT,
            username    TEXT,
            timestamp   TEXT    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(calendar_id, date, user_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS private_calendar_comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar_id INTEGER NOT NULL REFERENCES private_calendars(id) ON DELETE CASCADE,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            comment     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


def get_db() -> sqlite3.Connection:
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        ensure_schema(db)
    return db


@app.teardown_appcontext
def close_connection(_exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


@app.before_request
def sync_admin_flag():
    pass  # artık kullanılmıyor, rota bazlı DB kontrolü yapılıyor




# ══════════════════════════════════════════════════════════════════
# i18n – Translations  (tr / en / de)
# learn.html is EXCLUDED – stays in German (language of the PDF book)
# ══════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "tr": {
        # ── Generic ──────────────────────────────────────────────
        "save": "Kaydet",
        "cancel": "İptal",
        "delete": "Sil",
        "edit": "Düzenle",
        "back": "Geri",
        "yes": "Evet",
        "no": "Hayır",
        "loading": "Yükleniyor…",
        "error": "Hata",
        "success": "Başarılı",
        "server_error": "Sunucuya bağlanılamadı.",
        "no_changes": "Kaydedilecek değişiklik yok.",
        "unsaved_changes": "Kaydedilmemiş değişiklikler var. Devam edilsin mi?",
        "saved": "Kaydedildi!",
        # ── Auth ─────────────────────────────────────────────────
        "login_title": "Giriş Yap",
        "login_subtitle": "Hesabınıza erişim sağlayın",
        "login_btn": "Giriş Yap",
        "username": "Kullanıcı adı",
        "password": "Şifre",
        "forgot_link": "Şifremi unuttum",
        "register_link": "Yeni hesap oluştur",
        "home_link": "Ana sayfaya dön",
        "register_title": "Kayıt Ol",
        "register_subtitle": "Yeni hesap oluşturun",
        "register_btn": "Kayıt Ol",
        "email": "E-posta adresi",
        "fav_color": "Favori Renk:",
        "already_account": "Zaten hesabınız var mı? Giriş yapın",
        "forgot_title": "Şifremi Unuttum",
        "forgot_lead": "Kayıtlı e-posta adresinizi girin. Sıfırlama bağlantısı o adrese gönderilecek.",
        "forgot_email_ph": "E-posta adresiniz",
        "forgot_btn": "Sıfırlama bağlantısı iste",
        "back_to_login": "Girişe dön",
        "reset_title": "Yeni Şifre Belirle",
        "reset_lead": "Lütfen yeni şifrenizi girin.",
        "new_password_ph": "Yeni şifre (en az 4 karakter)",
        "update_password_btn": "Şifremi güncelle",
        # ── Settings ─────────────────────────────────────────────
        "settings_title": "Kullanıcı Ayarları",
        "settings_btn": "Ayarları Güncelle",
        "back_to_calendar": "Takvime Dön",
        "logout": "Çıkış Yap",
        "new_password_lbl": "Yeni Şifre:",
        "new_password_opt": "Yeni şifreyi girin (opsiyonel)",
        "email_lbl": "E-posta:",
        "username_lbl": "Kullanıcı Adı:",
        # ── Admin ─────────────────────────────────────────────────
        "admin_title": "Admin Paneli",
        "admin_users_section": "Kullanıcılar",
        "admin_accounts": "hesap",
        "admin_user_list": "Kullanıcı Listesi & Şifre Yönetimi",
        "admin_new_pass_ph": "Yeni şifre",
        "admin_apply": "Uygula",
        "admin_remove_admin": "Admin kaldır",
        "admin_make_admin": "Admin yap",
        "admin_you": "Sen",
        "admin_confirm_pass": "kullanıcısının şifresi değiştirilecek. Emin misiniz?",
        "admin_confirm_toggle": "kullanıcısının admin durumu değiştirilecek.",
        "admin_confirm_delete": "ve tüm verileri (rezervasyonlar, yorumlar, quiz skorları) kalıcı olarak silinecek.\n\nEmin misiniz?",
        # ── Calendar ─────────────────────────────────────────────
        "cal_title": "Bodrum / Güzelyalı Takvimi",
        "cal_welcome": "Hoş geldin,",
        "cal_tab_main": "📅 Ana Takvim",
        "cal_tab_private": "🔒 Kişisel Takvimler",
        "cal_month_title": "Takvim",
        "cal_click_hint": "Tıkla → rezerve et / iptal et",
        "cal_unsaved_badge": "Kaydedilmemiş değişiklik",
        "cal_notice": "Renkler kullanıcıları gösterir. Başkasının gününü değiştiremezsin.",
        "cal_weather": "Bodrum Hava Durumu",
        "cal_chat_title": "Duyuru / Chat",
        "cal_chat_sub": "Bu ayın sohbeti",
        "cal_chat_ph": "Mesaj yazın…",
        "cal_send": "Gönder",
        "cal_admin_btn": "🔧 Admin",
        "cal_learn_btn": "✈️ PPL Lernen",
        "cal_settings_btn": "⚙️ Ayarlar",
        "cal_logout": "Çıkış",
        "cal_notif_title": "Bildirimler",
        "cal_conflict": "Bazı günler kaydedilemedi (çakışma):",
        "cal_conflict_by": "başkası:",
        "cal_comment_fail": "Yorum gönderilemedi.",
        "cal_logout_confirm": "Çıkış yapmak istediğinizden emin misiniz?",
        "cal_reservation_saved": "Rezervasyonlar kaydedildi!",
        # ── Private Calendar ─────────────────────────────────────
        "priv_title": "🔒 Kişisel Takvimler",
        "priv_new_ph": "Yeni takvim adı…",
        "priv_create_btn": "+ Yeni Takvim",
        "priv_no_cal": "Henüz takvim yok.",
        "priv_rename_btn": "✎ Yeniden Adlandır",
        "priv_delete_btn": "🗑 Sil",
        "priv_save_btn": "💾 Kaydet",
        "priv_unsaved": "Kaydedilmemiş",
        "priv_members": "👥 Üyeler",
        "priv_no_members": "Henüz üye yok.",
        "priv_invite_btn": "Davet Et",
        "priv_no_invitable": "Davet edilebilecek başka kullanıcı yok.",
        "priv_select_user": "— Kullanıcı seç —",
        "priv_name_empty": "İsim boş olamaz.",
        "priv_select_user_alert": "Bir kullanıcı seçin.",
        "priv_invited": "davet edildi.",
        "priv_invite_fail": "Davet gönderilemedi.",
        "priv_remove_confirm": "Bu üyeyi takvimden çıkarmak istiyor musunuz?",
        "priv_remove_fail": "Kaldırılamadı.",
        "priv_delete_confirm": "Bu takvimi silmek istediğinize emin misiniz? Tüm rezervasyonlar silinir.",
        "priv_delete_fail": "Silinemedi.",
        "priv_create_fail": "Oluşturulamadı.",
        "priv_load_fail": "Yüklenemedi.",
        "priv_rename_fail": "Hata",
        "priv_save_fail": "Kayıt hatası.",
        "priv_default_name": "Özel Takvimim",
        "priv_owner": "👤",
        # ── Notifications ─────────────────────────────────────────
        "notif_title": "📬 Takvim Daveti",
        "notif_invited_you": "sizi",
        "notif_invited_to": "takvimine davet etti.",
        "notif_accept": "✓ Kabul Et",
        "notif_dismiss": "Reddet",
        "notif_empty": "Yeni bildirim yok.",
        # ── Flash messages ────────────────────────────────────────
        "flash_wrong_credentials": "Kullanıcı adı veya parola yanlış!",
        "flash_fields_required": "Kullanıcı adı, şifre ve e-posta gerekli.",
        "flash_username_taken": "Bu kullanıcı adı zaten alınmış!",
        "flash_email_taken": "Bu e-posta adresi zaten kayıtlı!",
        "flash_registered": "Kayıt başarılı! Giriş yapabilirsiniz.",
        "flash_email_other": "Bu e-posta başka bir hesapta kayıtlı.",
        "flash_settings_saved": "Ayarlar güncellendi!",
        "flash_reset_sent": "E-posta adresiniz sistemde kayıtlıysa sıfırlama bağlantısı gönderildi.",
        "flash_invalid_link": "Geçersiz veya kullanılmış bağlantı.",
        "flash_link_expired": "Bağlantının süresi dolmuş. Lütfen tekrar talep edin.",
        "flash_pass_short": "Şifre en az 4 karakter olmalı.",
        "flash_pass_updated": "Şifreniz güncellendi. Giriş yapabilirsiniz.",
        "flash_no_access": "Bu bölüme erişim yetkiniz yok.",
        "flash_no_page_access": "Bu sayfaya erişim yetkiniz yok.",
        "flash_user_not_found": "Kullanıcı bulunamadı.",
        "flash_cant_delete_self": "Kendi hesabınızı silemezsiniz.",
        "flash_cant_toggle_self": "Kendi admin durumunuzu değiştiremezsiniz.",
        "flash_admin_pass_updated": "kullanıcısının şifresi güncellendi.",
        "flash_user_deleted": "ve tüm verileri silindi.",
        "flash_admin_added": "artık admin.",
        "flash_admin_removed": "admin değil.",
        # ── Language switcher ─────────────────────────────────────
        "lang_switcher_label": "Dil:",
    },

    "en": {
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "back": "Back",
        "yes": "Yes",
        "no": "No",
        "loading": "Loading…",
        "error": "Error",
        "success": "Success",
        "server_error": "Could not connect to server.",
        "no_changes": "No changes to save.",
        "unsaved_changes": "You have unsaved changes. Continue?",
        "saved": "Saved!",
        "login_title": "Sign In",
        "login_subtitle": "Access your account",
        "login_btn": "Sign In",
        "username": "Username",
        "password": "Password",
        "forgot_link": "Forgot password",
        "register_link": "Create new account",
        "home_link": "Back to home",
        "register_title": "Register",
        "register_subtitle": "Create a new account",
        "register_btn": "Register",
        "email": "Email address",
        "fav_color": "Favourite Colour:",
        "already_account": "Already have an account? Sign in",
        "forgot_title": "Forgot Password",
        "forgot_lead": "Enter your registered email. A reset link will be sent to that address.",
        "forgot_email_ph": "Your email address",
        "forgot_btn": "Request reset link",
        "back_to_login": "Back to sign in",
        "reset_title": "Set New Password",
        "reset_lead": "Please enter your new password.",
        "new_password_ph": "New password (at least 4 characters)",
        "update_password_btn": "Update password",
        "settings_title": "User Settings",
        "settings_btn": "Save Settings",
        "back_to_calendar": "Back to Calendar",
        "logout": "Sign Out",
        "new_password_lbl": "New Password:",
        "new_password_opt": "Enter new password (optional)",
        "email_lbl": "Email:",
        "username_lbl": "Username:",
        "admin_title": "Admin Panel",
        "admin_users_section": "Users",
        "admin_accounts": "accounts",
        "admin_user_list": "User List & Password Management",
        "admin_new_pass_ph": "New password",
        "admin_apply": "Apply",
        "admin_remove_admin": "Remove admin",
        "admin_make_admin": "Make admin",
        "admin_you": "You",
        "admin_confirm_pass": "user's password will be changed. Are you sure?",
        "admin_confirm_toggle": "user's admin status will be changed.",
        "admin_confirm_delete": "and all their data (reservations, comments, quiz scores) will be permanently deleted.\n\nAre you sure?",
        "cal_title": "Bodrum / Güzelyalı Calendar",
        "cal_welcome": "Welcome,",
        "cal_tab_main": "📅 Main Calendar",
        "cal_tab_private": "🔒 Personal Calendars",
        "cal_month_title": "Calendar",
        "cal_click_hint": "Click → reserve / cancel",
        "cal_unsaved_badge": "Unsaved changes",
        "cal_notice": "Colours indicate users. You cannot change another person's day.",
        "cal_weather": "Bodrum Weather",
        "cal_chat_title": "Announcements / Chat",
        "cal_chat_sub": "This month's conversation",
        "cal_chat_ph": "Type a message…",
        "cal_send": "Send",
        "cal_admin_btn": "🔧 Admin",
        "cal_learn_btn": "✈️ PPL Learn",
        "cal_settings_btn": "⚙️ Settings",
        "cal_logout": "Sign Out",
        "cal_notif_title": "Notifications",
        "cal_conflict": "Some days could not be saved (conflict):",
        "cal_conflict_by": "reserved by:",
        "cal_comment_fail": "Comment could not be sent.",
        "cal_logout_confirm": "Are you sure you want to sign out?",
        "cal_reservation_saved": "Reservations saved!",
        "priv_title": "🔒 Personal Calendars",
        "priv_new_ph": "New calendar name…",
        "priv_create_btn": "+ New Calendar",
        "priv_no_cal": "No calendars yet.",
        "priv_rename_btn": "✎ Rename",
        "priv_delete_btn": "🗑 Delete",
        "priv_save_btn": "💾 Save",
        "priv_unsaved": "Unsaved",
        "priv_members": "👥 Members",
        "priv_no_members": "No members yet.",
        "priv_invite_btn": "Invite",
        "priv_no_invitable": "No other users to invite.",
        "priv_select_user": "— Select user —",
        "priv_name_empty": "Name cannot be empty.",
        "priv_select_user_alert": "Please select a user.",
        "priv_invited": "was invited.",
        "priv_invite_fail": "Could not send invite.",
        "priv_remove_confirm": "Remove this member from the calendar?",
        "priv_remove_fail": "Could not remove.",
        "priv_delete_confirm": "Delete this calendar? All reservations will be lost.",
        "priv_delete_fail": "Could not delete.",
        "priv_create_fail": "Could not create.",
        "priv_load_fail": "Could not load.",
        "priv_rename_fail": "Error",
        "priv_save_fail": "Save error.",
        "priv_default_name": "My Private Calendar",
        "priv_owner": "👤",
        "notif_title": "📬 Calendar Invitation",
        "notif_invited_you": "invited you to",
        "notif_invited_to": "calendar.",
        "notif_accept": "✓ Accept",
        "notif_dismiss": "Decline",
        "notif_empty": "No new notifications.",
        "flash_wrong_credentials": "Incorrect username or password!",
        "flash_fields_required": "Username, password and email are required.",
        "flash_username_taken": "This username is already taken!",
        "flash_email_taken": "This email address is already registered!",
        "flash_registered": "Registration successful! You can now sign in.",
        "flash_email_other": "This email is registered to another account.",
        "flash_settings_saved": "Settings updated!",
        "flash_reset_sent": "If your email address is registered, a reset link has been sent.",
        "flash_invalid_link": "Invalid or already used link.",
        "flash_link_expired": "Link has expired. Please request again.",
        "flash_pass_short": "Password must be at least 4 characters.",
        "flash_pass_updated": "Your password has been updated. You can now sign in.",
        "flash_no_access": "You do not have permission to access this section.",
        "flash_no_page_access": "You do not have permission to access this page.",
        "flash_user_not_found": "User not found.",
        "flash_cant_delete_self": "You cannot delete your own account.",
        "flash_cant_toggle_self": "You cannot change your own admin status.",
        "flash_admin_pass_updated": "user's password has been updated.",
        "flash_user_deleted": "and all their data have been deleted.",
        "flash_admin_added": "is now an admin.",
        "flash_admin_removed": "is no longer an admin.",
        "lang_switcher_label": "Language:",
    },

    "de": {
        "save": "Speichern",
        "cancel": "Abbrechen",
        "delete": "Löschen",
        "edit": "Bearbeiten",
        "back": "Zurück",
        "yes": "Ja",
        "no": "Nein",
        "loading": "Laden…",
        "error": "Fehler",
        "success": "Erfolg",
        "server_error": "Verbindung zum Server fehlgeschlagen.",
        "no_changes": "Keine Änderungen zum Speichern.",
        "unsaved_changes": "Es gibt ungespeicherte Änderungen. Fortfahren?",
        "saved": "Gespeichert!",
        "login_title": "Anmelden",
        "login_subtitle": "Zugang zu Ihrem Konto",
        "login_btn": "Anmelden",
        "username": "Benutzername",
        "password": "Passwort",
        "forgot_link": "Passwort vergessen",
        "register_link": "Neues Konto erstellen",
        "home_link": "Zur Startseite",
        "register_title": "Registrieren",
        "register_subtitle": "Neues Konto erstellen",
        "register_btn": "Registrieren",
        "email": "E-Mail-Adresse",
        "fav_color": "Lieblingsfarbe:",
        "already_account": "Bereits ein Konto? Anmelden",
        "forgot_title": "Passwort vergessen",
        "forgot_lead": "Geben Sie Ihre registrierte E-Mail-Adresse ein. Ein Zurücksetzungslink wird dorthin gesendet.",
        "forgot_email_ph": "Ihre E-Mail-Adresse",
        "forgot_btn": "Zurücksetzungslink anfordern",
        "back_to_login": "Zurück zur Anmeldung",
        "reset_title": "Neues Passwort festlegen",
        "reset_lead": "Bitte geben Sie Ihr neues Passwort ein.",
        "new_password_ph": "Neues Passwort (mindestens 4 Zeichen)",
        "update_password_btn": "Passwort aktualisieren",
        "settings_title": "Benutzereinstellungen",
        "settings_btn": "Einstellungen speichern",
        "back_to_calendar": "Zum Kalender",
        "logout": "Abmelden",
        "new_password_lbl": "Neues Passwort:",
        "new_password_opt": "Neues Passwort eingeben (optional)",
        "email_lbl": "E-Mail:",
        "username_lbl": "Benutzername:",
        "admin_title": "Admin-Panel",
        "admin_users_section": "Benutzer",
        "admin_accounts": "Konten",
        "admin_user_list": "Benutzerliste & Passwortverwaltung",
        "admin_new_pass_ph": "Neues Passwort",
        "admin_apply": "Anwenden",
        "admin_remove_admin": "Admin entfernen",
        "admin_make_admin": "Zum Admin machen",
        "admin_you": "Du",
        "admin_confirm_pass": "Passwort wird geändert. Sind Sie sicher?",
        "admin_confirm_toggle": "Admin-Status wird geändert.",
        "admin_confirm_delete": "und alle Daten (Reservierungen, Kommentare, Quiz-Ergebnisse) werden dauerhaft gelöscht.\n\nSind Sie sicher?",
        "cal_title": "Bodrum / Güzelyalı Kalender",
        "cal_welcome": "Willkommen,",
        "cal_tab_main": "📅 Hauptkalender",
        "cal_tab_private": "🔒 Persönliche Kalender",
        "cal_month_title": "Kalender",
        "cal_click_hint": "Klicken → reservieren / stornieren",
        "cal_unsaved_badge": "Ungespeicherte Änderungen",
        "cal_notice": "Farben kennzeichnen Benutzer. Sie können den Tag einer anderen Person nicht ändern.",
        "cal_weather": "Bodrum Wetter",
        "cal_chat_title": "Ankündigungen / Chat",
        "cal_chat_sub": "Gespräch dieses Monats",
        "cal_chat_ph": "Nachricht eingeben…",
        "cal_send": "Senden",
        "cal_admin_btn": "🔧 Admin",
        "cal_learn_btn": "✈️ PPL Lernen",
        "cal_settings_btn": "⚙️ Einstellungen",
        "cal_logout": "Abmelden",
        "cal_notif_title": "Benachrichtigungen",
        "cal_conflict": "Einige Tage konnten nicht gespeichert werden (Konflikt):",
        "cal_conflict_by": "reserviert von:",
        "cal_comment_fail": "Kommentar konnte nicht gesendet werden.",
        "cal_logout_confirm": "Möchten Sie sich wirklich abmelden?",
        "cal_reservation_saved": "Reservierungen gespeichert!",
        "priv_title": "🔒 Persönliche Kalender",
        "priv_new_ph": "Neuer Kalendername…",
        "priv_create_btn": "+ Neuer Kalender",
        "priv_no_cal": "Noch keine Kalender.",
        "priv_rename_btn": "✎ Umbenennen",
        "priv_delete_btn": "🗑 Löschen",
        "priv_save_btn": "💾 Speichern",
        "priv_unsaved": "Ungespeichert",
        "priv_members": "👥 Mitglieder",
        "priv_no_members": "Noch keine Mitglieder.",
        "priv_invite_btn": "Einladen",
        "priv_no_invitable": "Keine weiteren Benutzer einladbar.",
        "priv_select_user": "— Benutzer auswählen —",
        "priv_name_empty": "Name darf nicht leer sein.",
        "priv_select_user_alert": "Bitte einen Benutzer auswählen.",
        "priv_invited": "wurde eingeladen.",
        "priv_invite_fail": "Einladung konnte nicht gesendet werden.",
        "priv_remove_confirm": "Dieses Mitglied aus dem Kalender entfernen?",
        "priv_remove_fail": "Konnte nicht entfernt werden.",
        "priv_delete_confirm": "Diesen Kalender löschen? Alle Reservierungen gehen verloren.",
        "priv_delete_fail": "Konnte nicht gelöscht werden.",
        "priv_create_fail": "Konnte nicht erstellt werden.",
        "priv_load_fail": "Konnte nicht geladen werden.",
        "priv_rename_fail": "Fehler",
        "priv_save_fail": "Speicherfehler.",
        "priv_default_name": "Mein privater Kalender",
        "priv_owner": "👤",
        "notif_title": "📬 Kalendereinladung",
        "notif_invited_you": "hat Sie zum Kalender",
        "notif_invited_to": "eingeladen.",
        "notif_accept": "✓ Annehmen",
        "notif_dismiss": "Ablehnen",
        "notif_empty": "Keine neuen Benachrichtigungen.",
        "flash_wrong_credentials": "Benutzername oder Passwort falsch!",
        "flash_fields_required": "Benutzername, Passwort und E-Mail sind erforderlich.",
        "flash_username_taken": "Dieser Benutzername ist bereits vergeben!",
        "flash_email_taken": "Diese E-Mail-Adresse ist bereits registriert!",
        "flash_registered": "Registrierung erfolgreich! Sie können sich jetzt anmelden.",
        "flash_email_other": "Diese E-Mail ist einem anderen Konto zugeordnet.",
        "flash_settings_saved": "Einstellungen aktualisiert!",
        "flash_reset_sent": "Falls Ihre E-Mail-Adresse registriert ist, wurde ein Reset-Link gesendet.",
        "flash_invalid_link": "Ungültiger oder bereits verwendeter Link.",
        "flash_link_expired": "Link ist abgelaufen. Bitte erneut anfordern.",
        "flash_pass_short": "Passwort muss mindestens 4 Zeichen lang sein.",
        "flash_pass_updated": "Ihr Passwort wurde aktualisiert. Sie können sich jetzt anmelden.",
        "flash_no_access": "Sie haben keine Berechtigung, auf diesen Bereich zuzugreifen.",
        "flash_no_page_access": "Sie haben keine Berechtigung, auf diese Seite zuzugreifen.",
        "flash_user_not_found": "Benutzer nicht gefunden.",
        "flash_cant_delete_self": "Sie können Ihr eigenes Konto nicht löschen.",
        "flash_cant_toggle_self": "Sie können Ihren eigenen Admin-Status nicht ändern.",
        "flash_admin_pass_updated": "Passwort des Benutzers wurde aktualisiert.",
        "flash_user_deleted": "und alle Daten wurden gelöscht.",
        "flash_admin_added": "ist jetzt Admin.",
        "flash_admin_removed": "ist kein Admin mehr.",
        "lang_switcher_label": "Sprache:",
    },
}

SUPPORTED_LANGS = ("tr", "en", "de")
LANG_FLAGS = {"tr": "🇹🇷", "en": "🇬🇧", "de": "🇩🇪"}
LANG_NAMES = {"tr": "TR", "en": "EN", "de": "DE"}


def get_lang() -> str:
    return session.get("lang", "tr") if "tr" in TRANSLATIONS else "tr"


def t(key: str) -> str:
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["tr"]).get(key, TRANSLATIONS["tr"].get(key, key))


@app.context_processor
def inject_i18n():
    lang = get_lang()
    td   = TRANSLATIONS.get(lang, TRANSLATIONS["tr"])
    return dict(t=td, lang=lang, lang_flags=LANG_FLAGS, lang_names=LANG_NAMES)


@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


# ── Existing Routes (100% unchanged) ─────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("calendar_view"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["color"]    = user["color"]
            session["is_admin"] = bool(user["is_admin"])
            return redirect(url_for("calendar_view"))
        flash(t("flash_wrong_credentials"), "error")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email    = request.form.get("email", "").strip().lower()
        color    = request.form.get("color") or "#4caf50"
        if not username or not password or not email:
            flash(t("flash_fields_required"), "error")
            return redirect(url_for("register"))
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            flash(t("flash_username_taken"), "error")
            return redirect(url_for("register"))
        if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            flash(t("flash_email_taken"), "error")
            return redirect(url_for("register"))
        db.execute("INSERT INTO users (username, password, email, color) VALUES (?, ?, ?, ?)",
                   (username, generate_password_hash(password), email, color))
        db.commit()
        flash(t("flash_registered"), "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/calendar")
def calendar_view():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    user_id = int(session["user_id"])
    urow = db.execute("SELECT id, username, color, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if not urow:
        return redirect(url_for("logout"))
    current_user = {"id": urow["id"], "name": urow["username"], "color": urow["color"] or "#4caf50", "is_admin": bool(urow["is_admin"])}
    users = [dict(r) for r in db.execute("SELECT id, username, color FROM users ORDER BY username").fetchall()]
    now   = datetime.now()
    year  = int(request.args.get("year",  now.year))
    month = int(request.args.get("month", now.month))
    month = max(1, min(12, month))
    prefix = f"{year}-{month:02d}"
    rows = db.execute("""
        SELECT r.date, u.username, u.color, u.id AS user_id, r.timestamp
        FROM reservations r JOIN users u ON r.user_id = u.id
        WHERE substr(r.date, 1, 7) = ?
        ORDER BY COALESCE(r.timestamp, '') DESC
    """, (prefix,)).fetchall()
    reservation_data: dict[str, dict] = {}
    for r in rows:
        if r["date"] not in reservation_data:
            reservation_data[r["date"]] = {
                "userId": r["user_id"], "username": r["username"],
                "color":  r["color"],   "timestamp": r["timestamp"],
            }
    com_rows = db.execute("""
        SELECT c.date, c.comment, c.user_id, u.username, u.color,
               COALESCE(c.timestamp, '') AS timestamp
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE substr(c.date, 1, 7) = ?
        ORDER BY c.timestamp ASC
    """, (prefix,)).fetchall()
    comments = [dict(r) for r in com_rows]
    month_names = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                   "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    return render_template("calendar.html", current_user=current_user, users=users,
        reservation_data=reservation_data, comments=comments,
        year=year, month=month, month_name=month_names[month])


@app.route("/save_reservations", methods=["POST"])
def save_reservations():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    changes = payload.get("changes") or payload.get("reservations") or {}
    if not isinstance(changes, dict):
        return jsonify({"success": False, "error": "Bad payload"}), 400
    db = get_db()
    user_id   = int(session["user_id"])
    conflicts = []
    for date, info in changes.items():
        if not isinstance(date, str) or len(date) != 10:
            continue
        if info is None:
            db.execute("DELETE FROM reservations WHERE user_id = ? AND date = ?", (user_id, date))
            continue
        color     = (info.get("color") if isinstance(info, dict) else None) or session.get("color") or "#4caf50"
        username  = session.get("username") or ""
        timestamp = (info.get("timestamp") if isinstance(info, dict) else None) or datetime.utcnow().isoformat(timespec="seconds")
        other = db.execute("""
            SELECT u.username FROM reservations r JOIN users u ON r.user_id = u.id
            WHERE r.date = ? AND r.user_id != ? LIMIT 1
        """, (date, user_id)).fetchone()
        if other:
            conflicts.append({"date": date, "by": other["username"]}); continue
        db.execute("DELETE FROM reservations WHERE user_id = ? AND date = ?", (user_id, date))
        db.execute("INSERT INTO reservations (user_id, date, color, username, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (user_id, date, color, username, timestamp))
    db.commit()
    return jsonify({"success": True, "conflicts": conflicts})


@app.route("/add_comment", methods=["POST"])
def add_comment():
    if "user_id" not in session:
        return jsonify(success=False, message="Giriş yapılmamış"), 401
    date = request.form.get("date")
    text = (request.form.get("comment") or "").strip()
    if not date or not text:
        return jsonify(success=False, message="Tarih ve yorum gerekli."), 400
    db = get_db()
    db.execute("INSERT INTO comments (user_id, date, comment) VALUES (?, ?, ?)", (session["user_id"], date, text))
    db.commit()
    return jsonify(success=True)


@app.route("/api/day_notes/<string:date>")
def day_notes_get(date):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    rows = db.execute("""
        SELECT dn.id, dn.user_id, dn.date, dn.note, dn.created_at,
               u.username, u.color
        FROM day_notes dn JOIN users u ON u.id = dn.user_id
        WHERE dn.date = ?
        ORDER BY dn.created_at
    """, (date,)).fetchall()
    return jsonify({"success": True, "notes": [dict(r) for r in rows]})


@app.route("/api/day_notes", methods=["POST"])
def day_notes_save():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    uid  = int(session["user_id"])
    data = request.get_json(silent=True) or {}
    date = data.get("date", "")
    note = (data.get("note") or "").strip()
    if not date or not note:
        return jsonify({"success": False, "error": "Tarih ve not gerekli"}), 400
    db.execute("""
        INSERT INTO day_notes (user_id, date, note) VALUES (?,?,?)
        ON CONFLICT(user_id, date) DO UPDATE SET note=excluded.note, created_at=CURRENT_TIMESTAMP
    """, (uid, date, note))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/day_notes/<string:date>", methods=["DELETE"])
def day_notes_delete(date):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM day_notes WHERE user_id=? AND date=?", (int(session["user_id"]), date))
    db.commit()
    return jsonify({"success": True})



@app.route("/api/day_notes/month/<string:ym>")
def day_notes_month(ym):
    """Return all dates that have notes in a given YYYY-MM month."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT date FROM day_notes WHERE date LIKE ? ORDER BY date",
        (ym + "-%",)
    ).fetchall()
    return jsonify({"success": True, "dates": [r["date"] for r in rows]})


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db      = get_db()
    user_id = int(session["user_id"])
    if request.method == "POST":
        new_color = request.form.get("color")
        new_pass  = request.form.get("password")
        new_email = request.form.get("email", "").strip().lower()
        if new_color:
            db.execute("UPDATE users SET color = ? WHERE id = ?", (new_color, user_id))
            session["color"] = new_color
        if new_pass:
            db.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(new_pass), user_id))
        if new_email:
            existing = db.execute("SELECT id FROM users WHERE email = ? AND id != ?", (new_email, user_id)).fetchone()
            if existing:
                flash(t("flash_email_other"), "error")
                return redirect(url_for("settings"))
            db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
        db.commit()
        flash(t("flash_settings_saved"), "success")
        return redirect(url_for("settings"))
    user = db.execute("SELECT username, color, email FROM users WHERE id = ?", (user_id,)).fetchone()
    return render_template("settings.html", user=user)


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        db    = get_db()
        user  = db.execute("SELECT id, username, email FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            token      = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat(timespec="seconds")
            db.execute("DELETE FROM reset_tokens WHERE email = ?", (email,))
            db.execute("INSERT INTO reset_tokens (email, token, expires_at) VALUES (?, ?, ?)",
                       (email, token, expires_at))
            db.commit()
            reset_url = os.getenv("BASE_URL", "").rstrip("/")
            if reset_url:
                reset_url = f"{reset_url}/reset/{token}"
            else:
                reset_url = url_for("reset_password", token=token, _external=True)
            _send_reset_email(user["username"], email, reset_url)
        flash(t("flash_reset_sent"), "info")
        return redirect(url_for("forgot"))
    return render_template("forgot.html")


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    db  = get_db()
    row = db.execute(
        "SELECT email, expires_at FROM reset_tokens WHERE token = ?", (token,)
    ).fetchone()
    if not row:
        flash(t("flash_invalid_link"), "error")
        return redirect(url_for("login"))
    if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
        db.execute("DELETE FROM reset_tokens WHERE token = ?", (token,))
        db.commit()
        flash(t("flash_link_expired"), "error")
        return redirect(url_for("forgot"))
    if request.method == "POST":
        new_pass = request.form.get("password", "")
        if len(new_pass) < 4:
            flash(t("flash_pass_short"), "error")
            return render_template("reset.html", token=token)
        db.execute("UPDATE users SET password = ? WHERE email = ?",
                   (generate_password_hash(new_pass), row["email"]))
        db.execute("DELETE FROM reset_tokens WHERE token = ?", (token,))
        db.commit()
        flash(t("flash_pass_updated"), "success")
        return redirect(url_for("login"))
    return render_template("reset.html", token=token)


def _send_reset_email(username: str, recipient: str, reset_url: str) -> None:
    sender   = os.getenv("MAIL_SENDER", "")
    password = os.getenv("MAIL_PASSWORD", "")
    if not sender or not password:
        app.logger.warning("MAIL_SENDER veya MAIL_PASSWORD .env'de tanımlı değil — e-posta gönderilmedi.")
        return
    app.logger.info(f"E-posta gönderiliyor: {sender} → {recipient}")
    body = f"""Merhaba {username},

Şifre sıfırlama talebiniz alındı.
Aşağıdaki bağlantıya tıklayarak 1 saat içinde yeni şifrenizi belirleyebilirsiniz:

{reset_url}

Bu talebi siz yapmadıysanız bu e-postayı dikkate almayın.
"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Şifre Sıfırlama"
    msg["From"]    = sender
    msg["To"]      = recipient
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, recipient, msg.as_string())
        app.logger.info("E-posta başarıyla gönderildi.")
    except smtplib.SMTPAuthenticationError:
        app.logger.error("SMTP AUTH HATASI: Gmail uygulama şifresi yanlış veya 2FA aktif değil.")
    except smtplib.SMTPException as e:
        app.logger.error(f"SMTP hatası: {e}")
    except Exception as e:
        app.logger.error(f"Beklenmeyen hata: {type(e).__name__}: {e}")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/learn")
def learn():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db      = get_db()
    user_id = int(session["user_id"])
    urow    = db.execute("SELECT id, username, color, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if not urow:
        return redirect(url_for("logout"))
    current_user = {
        "id":       urow["id"],
        "name":     urow["username"],
        "color":    urow["color"] or "#4caf50",
        "is_admin": bool(urow["is_admin"]),
    }
    return render_template("learn.html", current_user=current_user)


@app.route("/health")
def health():
    return jsonify({"ok": True})


# ── Quiz Score Routes (existing - field renamed wrong_q_indexes→wrong_q_ids) ─

def ensure_quiz_tables(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            chapter_id TEXT    NOT NULL,
            correct    INTEGER DEFAULT 0,
            wrong      INTEGER DEFAULT 0,
            wrong_q_ids TEXT   DEFAULT '[]',
            updated_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, chapter_id)
        )
    """)
    # backward-compat migration
    cols = _table_columns(db, "quiz_scores")
    if "wrong_q_ids" not in cols and "wrong_q_indexes" in cols:
        db.execute("ALTER TABLE quiz_scores ADD COLUMN wrong_q_ids TEXT DEFAULT '[]'")
    db.commit()


@app.route("/api/quiz/save", methods=["POST"])
def quiz_save():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload    = request.get_json(silent=True) or {}
    chapter_id = payload.get("chapter_id", "")
    correct    = int(payload.get("correct", 0))
    wrong      = int(payload.get("wrong", 0))
    wrong_ids  = json.dumps(payload.get("wrong_q_ids", []))
    if not chapter_id:
        return jsonify({"success": False, "error": "Missing chapter_id"}), 400
    db = get_db()
    ensure_quiz_tables(db)
    db.execute("""
        INSERT INTO quiz_scores (user_id, chapter_id, correct, wrong, wrong_q_ids, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, chapter_id) DO UPDATE SET
            correct     = excluded.correct,
            wrong       = excluded.wrong,
            wrong_q_ids = excluded.wrong_q_ids,
            updated_at  = excluded.updated_at
    """, (session["user_id"], chapter_id, correct, wrong, wrong_ids,
          datetime.utcnow().isoformat(timespec="seconds")))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/quiz/scores")
def quiz_scores():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    ensure_quiz_tables(db)
    rows = db.execute(
        "SELECT chapter_id, correct, wrong, wrong_q_ids FROM quiz_scores WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()
    result = {}
    for r in rows:
        result[r["chapter_id"]] = {
            "correct":    r["correct"],
            "wrong":      r["wrong"],
            "wrong_q_ids": json.loads(r["wrong_q_ids"] or "[]")
        }
    return jsonify({"success": True, "scores": result})


@app.route("/api/quiz/reset", methods=["POST"])
def quiz_reset():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload    = request.get_json(silent=True) or {}
    chapter_id = payload.get("chapter_id")
    db         = get_db()
    ensure_quiz_tables(db)
    if chapter_id:
        db.execute("DELETE FROM quiz_scores WHERE user_id = ? AND chapter_id = ?", (session["user_id"], chapter_id))
    else:
        db.execute("DELETE FROM quiz_scores WHERE user_id = ?", (session["user_id"],))
    db.commit()
    return jsonify({"success": True})


# ── Learning Platform API ─────────────────────────────────────────────────────

@app.route("/api/learn/subjects")
def api_learn_subjects():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    rows = db.execute("""
        SELECT s.id, s.code, s.title, s.icon, s.color, s.overview, s.sort_order,
               COUNT(DISTINCT c.id) AS chapter_count,
               COUNT(DISTINCT q.id) AS quiz_count
        FROM learn_subjects s
        LEFT JOIN learn_chapters c ON c.subject_id = s.id
        LEFT JOIN learn_quiz     q ON q.chapter_id = c.id
        GROUP BY s.id
        ORDER BY s.sort_order, s.code
    """).fetchall()
    return jsonify({"success": True, "subjects": [dict(r) for r in rows]})


@app.route("/api/learn/subject/<subject_id>")
def api_learn_subject(subject_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db   = get_db()
    subj = db.execute("SELECT * FROM learn_subjects WHERE id = ?", (subject_id,)).fetchone()
    if not subj:
        return jsonify({"success": False, "error": "Not found"}), 404
    chapters = db.execute("""
        SELECT c.id, c.title, c.sort_order, c.exam_relevant,
               COUNT(q.id) AS quiz_count
        FROM learn_chapters c
        LEFT JOIN learn_quiz q ON q.chapter_id = c.id
        WHERE c.subject_id = ?
        GROUP BY c.id ORDER BY c.sort_order
    """, (subject_id,)).fetchall()
    return jsonify({"success": True, "subject": dict(subj), "chapters": [dict(c) for c in chapters]})


@app.route("/api/learn/chapter/<chapter_id>")
def api_learn_chapter(chapter_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    ch = db.execute("""
        SELECT c.*, s.title AS subject_title, s.icon AS subject_icon,
               s.color AS subject_color, s.id AS subject_id
        FROM learn_chapters c
        JOIN learn_subjects s ON s.id = c.subject_id
        WHERE c.id = ?
    """, (chapter_id,)).fetchone()
    if not ch:
        return jsonify({"success": False, "error": "Not found"}), 404
    secs = db.execute("""
        SELECT type, content, extra FROM learn_sections
        WHERE chapter_id = ? ORDER BY sort_order, id
    """, (chapter_id,)).fetchall()
    quiz_rows = db.execute("""
        SELECT id, question, options, answer, explanation, is_official, image_path
        FROM learn_quiz WHERE chapter_id = ? ORDER BY sort_order, id
    """, (chapter_id,)).fetchall()
    structured = {"summaries": [], "facts": [], "focuses": [], "tables": [], "sources": []}
    for s in secs:
        t = s["type"]
        if   t == "summary":   structured["summaries"].append(s["content"])
        elif t == "fact":      structured["facts"].append(s["content"])
        elif t == "focus":     structured["focuses"].append(s["content"])
        elif t == "table_row": structured["tables"].append([s["content"], s["extra"] or ""])
        elif t == "source":    structured["sources"].append({"label": s["content"], "url": s["extra"] or "#"})
    quiz = []
    for q in quiz_rows:
        try:   opts = json.loads(q["options"])
        except Exception: opts = []
        quiz.append({"id": q["id"], "q": q["question"], "options": opts,
                     "answer": q["answer"], "explanation": q["explanation"] or "",
                     "is_official": bool(q["is_official"]),
                     "image_path": q["image_path"] or ""})
    secs_raw = [{"type": s["type"], "content": s["content"], "extra": s["extra"]} for s in secs]
    return jsonify({"success": True, "chapter": dict(ch), "sections": structured, "sections_raw": secs_raw, "quiz": quiz})


@app.route("/api/learn/search")
def api_learn_search():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"success": True, "results": []})
    db      = get_db()
    results = []
    try:
        safe_q = q.replace('"', '').replace("'", "") + "*"
        rows   = db.execute("""
            SELECT DISTINCT chapter_id, subject_id, chapter_title, subject_title
            FROM learn_fts WHERE learn_fts MATCH ? LIMIT 15
        """, (safe_q,)).fetchall()
        results = [dict(r) for r in rows]
    except Exception:
        rows = db.execute("""
            SELECT DISTINCT c.id AS chapter_id, c.subject_id,
                   c.title AS chapter_title, s.title AS subject_title
            FROM learn_sections sec
            JOIN learn_chapters c ON c.id = sec.chapter_id
            JOIN learn_subjects s ON s.id = c.subject_id
            WHERE LOWER(sec.content) LIKE LOWER(?) OR LOWER(c.title) LIKE LOWER(?)
            LIMIT 15
        """, (f"%{q}%", f"%{q}%")).fetchall()
        results = [dict(r) for r in rows]
    return jsonify({"success": True, "results": results})


@app.route("/api/learn/toc")
def api_learn_toc():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db       = get_db()
    subjects = db.execute("""
        SELECT id, code, title, icon, color FROM learn_subjects ORDER BY sort_order, code
    """).fetchall()
    toc = []
    for s in subjects:
        chapters = db.execute("""
            SELECT id, title, exam_relevant FROM learn_chapters
            WHERE subject_id = ? ORDER BY sort_order
        """, (s["id"],)).fetchall()
        toc.append({"id": s["id"], "code": s["code"], "title": s["title"],
                    "icon": s["icon"], "color": s["color"],
                    "chapters": [dict(c) for c in chapters]})
    return jsonify({"success": True, "toc": toc})


@app.route("/api/learn/flashcards/<chapter_id>")
def api_learn_flashcards(chapter_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    rows = db.execute("""
        SELECT id, front, back, sort_order FROM learn_flashcards
        WHERE chapter_id = ? ORDER BY sort_order, id
    """, (chapter_id,)).fetchall()
    cards = [dict(r) for r in rows]
    return jsonify({"success": True, "flashcards": cards, "count": len(cards)})


@app.route("/api/learn/wrong_questions", methods=["POST"])
def api_learn_wrong_questions():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    ids     = payload.get("ids", [])
    if not ids:
        return jsonify({"success": True, "questions": []})
    db           = get_db()
    placeholders = ",".join("?" * len(ids))
    rows         = db.execute(f"""
        SELECT q.id, q.question, q.options, q.answer, q.explanation, q.is_official,
               q.chapter_id, c.title AS chapter_title,
               s.id AS subject_id, s.title AS subject_title, s.icon AS subject_icon
        FROM learn_quiz q
        JOIN learn_chapters c ON c.id = q.chapter_id
        JOIN learn_subjects  s ON s.id = c.subject_id
        WHERE q.id IN ({placeholders})
    """, ids).fetchall()
    questions = []
    for r in rows:
        try:   opts = json.loads(r["options"])
        except Exception: opts = []
        questions.append({
            "id": r["id"], "q": r["question"], "options": opts,
            "answer": r["answer"], "explanation": r["explanation"] or "",
            "is_official": bool(r["is_official"]),
            "image_path": r["image_path"] or "",
            "chapter_id": r["chapter_id"], "chapter_title": r["chapter_title"],
            "subject_id": r["subject_id"], "subject_title": r["subject_title"],
            "subject_icon": r["subject_icon"]
        })
    return jsonify({"success": True, "questions": questions})




# ── Admin Panel ───────────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        db  = get_db()
        row = db.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        if not row or not row["is_admin"]:
            flash(t("flash_no_page_access"), "error")
            return redirect(url_for("calendar_view"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin")
@admin_required
def admin_panel():
    db = get_db()
    users = db.execute(
        "SELECT id, username, email, color, is_admin FROM users ORDER BY id"
    ).fetchall()
    return render_template("admin.html", users=users,
                           current_user={"name": session.get("username"),
                                         "id": int(session["user_id"])})


@app.route("/admin/user/<int:uid>/setpass", methods=["POST"])
@admin_required
def admin_setpass(uid):
    new_pass = (request.form.get("password") or "").strip()
    if len(new_pass) < 4:
        flash(t("flash_pass_short"), "error")
        return redirect(url_for("admin_panel"))
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (uid,)).fetchone()
    if not user:
        flash(t("flash_user_not_found"), "error")
        return redirect(url_for("admin_panel"))
    db.execute("UPDATE users SET password = ? WHERE id = ?",
               (generate_password_hash(new_pass), uid))
    db.commit()
    flash(f"'{user['username']}' " + t("flash_admin_pass_updated"), "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/user/<int:uid>/delete", methods=["POST"])
@admin_required
def admin_delete_user(uid):
    if uid == int(session["user_id"]):
        flash(t("flash_cant_delete_self"), "error")
        return redirect(url_for("admin_panel"))
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (uid,)).fetchone()
    if not user:
        flash(t("flash_user_not_found"), "error")
        return redirect(url_for("admin_panel"))
    # Kullanıcıya ait tüm verileri temizle
    db.execute("DELETE FROM reservations WHERE user_id = ?", (uid,))
    db.execute("DELETE FROM comments WHERE user_id = ?", (uid,))
    db.execute("DELETE FROM quiz_scores WHERE user_id = ?", (uid,))
    db.execute("DELETE FROM users WHERE id = ?", (uid,))
    db.commit()
    flash(f"'{user['username']}' " + t("flash_user_deleted"), "success")
    return redirect(url_for("admin_panel"))



@app.route("/admin/user/<int:uid>/toggle_admin", methods=["POST"])
@admin_required
def admin_toggle(uid):
    db = get_db()
    # Kendini admin'den çıkaramaz
    if uid == int(session["user_id"]):
        flash(t("flash_cant_toggle_self"), "error")
        return redirect(url_for("admin_panel"))
    user = db.execute("SELECT username, is_admin FROM users WHERE id = ?", (uid,)).fetchone()
    if not user:
        flash(t("flash_user_not_found"), "error")
        return redirect(url_for("admin_panel"))
    new_val = 0 if user["is_admin"] else 1
    db.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_val, uid))
    db.commit()
    label = "admin yapıldı" if new_val else "admin yetkisi kaldırıldı"
    flash(f"'{user['username']}' {label}.", "success")
    return redirect(url_for("admin_panel"))



# ── Wrong Answer removal (fix: remove from bank when correctly answered) ─────

@app.route("/api/quiz/remove_wrong", methods=["POST"])
def quiz_remove_wrong():
    """Remove specific question IDs from the wrong_q_ids bank after correct retry."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload    = request.get_json(silent=True) or {}
    remove_ids = payload.get("remove_ids", [])   # list of question IDs to remove
    if not remove_ids:
        return jsonify({"success": True})
    db = get_db()
    ensure_quiz_tables(db)
    rows = db.execute(
        "SELECT id, chapter_id, wrong_q_ids FROM quiz_scores WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()
    for row in rows:
        try:
            ids = json.loads(row["wrong_q_ids"] or "[]")
        except Exception:
            ids = []
        new_ids = [i for i in ids if i not in remove_ids]
        if len(new_ids) != len(ids):
            wrong_count = db.execute(
                "SELECT wrong FROM quiz_scores WHERE id = ?", (row["id"],)
            ).fetchone()
            removed_count = len(ids) - len(new_ids)
            new_wrong = max(0, (wrong_count["wrong"] if wrong_count else 0) - removed_count)
            db.execute(
                "UPDATE quiz_scores SET wrong_q_ids=?, wrong=? WHERE id=?",
                (json.dumps(new_ids), new_wrong, row["id"])
            )
    db.commit()
    return jsonify({"success": True})


# ── Test Simulation ──────────────────────────────────────────────────────────

def ensure_test_sim_tables(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS test_simulations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            started_at  TEXT    NOT NULL,
            finished_at TEXT    DEFAULT NULL,
            subject_ids TEXT    NOT NULL DEFAULT '[]',
            total_q     INTEGER DEFAULT 0,
            correct     INTEGER DEFAULT 0,
            wrong       INTEGER DEFAULT 0,
            score_pct   REAL    DEFAULT 0,
            status      TEXT    DEFAULT 'in_progress',
            question_data TEXT  DEFAULT '[]',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.commit()


@app.route("/api/test/start", methods=["POST"])
def test_start():
    """Start a new test simulation session."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload     = request.get_json(silent=True) or {}
    subject_ids = payload.get("subject_ids", [])   # empty = all subjects
    question_count = int(payload.get("count", 30))
    question_count = max(5, min(60, question_count))

    db = get_db()
    ensure_test_sim_tables(db)

    # Fetch questions
    if subject_ids:
        placeholders = ",".join("?" * len(subject_ids))
        rows = db.execute(f"""
            SELECT q.id, q.question, q.options, q.answer, q.explanation, q.is_official,
                   q.image_path, q.chapter_id, c.title AS chapter_title,
                   s.id AS subject_id, s.title AS subject_title, s.icon AS subject_icon
            FROM learn_quiz q
            JOIN learn_chapters c ON c.id = q.chapter_id
            JOIN learn_subjects s ON s.id = c.subject_id
            WHERE s.id IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT ?
        """, (*subject_ids, question_count)).fetchall()
    else:
        rows = db.execute("""
            SELECT q.id, q.question, q.options, q.answer, q.explanation, q.is_official,
                   q.image_path, q.chapter_id, c.title AS chapter_title,
                   s.id AS subject_id, s.title AS subject_title, s.icon AS subject_icon
            FROM learn_quiz q
            JOIN learn_chapters c ON c.id = q.chapter_id
            JOIN learn_subjects s ON s.id = c.subject_id
            ORDER BY RANDOM()
            LIMIT ?
        """, (question_count,)).fetchall()

    questions = []
    for r in rows:
        try:   opts = json.loads(r["options"])
        except Exception: opts = []
        questions.append({
            "id": r["id"], "q": r["question"], "options": opts,
            "answer": r["answer"], "explanation": r["explanation"] or "",
            "is_official": bool(r["is_official"]),
            "image_path": r["image_path"] or "",
            "chapter_id": r["chapter_id"], "chapter_title": r["chapter_title"],
            "subject_id": r["subject_id"], "subject_title": r["subject_title"],
            "subject_icon": r["subject_icon"]
        })

    started_at = datetime.utcnow().isoformat(timespec="seconds")
    cur = db.execute("""
        INSERT INTO test_simulations (user_id, started_at, subject_ids, total_q, status, question_data)
        VALUES (?,?,?,?,?,?)
    """, (session["user_id"], started_at,
          json.dumps(subject_ids), len(questions), "in_progress",
          json.dumps(questions)))
    db.commit()

    sim_id = cur.lastrowid
    return jsonify({"success": True, "sim_id": sim_id, "questions": questions, "started_at": started_at})


@app.route("/api/test/finish", methods=["POST"])
def test_finish():
    """Finish a test simulation and save results."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    payload  = request.get_json(silent=True) or {}
    sim_id   = payload.get("sim_id")
    correct  = int(payload.get("correct", 0))
    wrong    = int(payload.get("wrong", 0))
    total    = correct + wrong
    score    = round(correct / total * 100, 1) if total > 0 else 0

    db = get_db()
    ensure_test_sim_tables(db)
    finished_at = datetime.utcnow().isoformat(timespec="seconds")
    db.execute("""
        UPDATE test_simulations
        SET finished_at=?, correct=?, wrong=?, score_pct=?, status='completed'
        WHERE id=? AND user_id=?
    """, (finished_at, correct, wrong, score, sim_id, session["user_id"]))
    db.commit()

    # Keep only the 10 most recent simulations per user – delete older ones
    db.execute("""
        DELETE FROM test_simulations
        WHERE user_id=?
          AND id NOT IN (
              SELECT id FROM test_simulations
              WHERE user_id=?
              ORDER BY started_at DESC
              LIMIT 10
          )
    """, (session["user_id"], session["user_id"]))
    db.commit()

    return jsonify({"success": True, "score_pct": score})


@app.route("/api/test/history")
def test_history():
    """Get test simulation history for the current user."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    ensure_test_sim_tables(db)
    rows = db.execute("""
        SELECT id, started_at, finished_at, total_q, correct, wrong, score_pct, status
        FROM test_simulations WHERE user_id=?
        ORDER BY started_at DESC LIMIT 10
    """, (session["user_id"],)).fetchall()
    return jsonify({"success": True, "history": [dict(r) for r in rows]})


@app.route("/api/test/subjects")
def test_subjects():
    """Return subjects with quiz question counts for test configuration."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    db = get_db()
    rows = db.execute("""
        SELECT s.id, s.title, s.icon, s.color, COUNT(q.id) AS quiz_count
        FROM learn_subjects s
        LEFT JOIN learn_chapters c ON c.subject_id = s.id
        LEFT JOIN learn_quiz q ON q.chapter_id = c.id
        GROUP BY s.id
        HAVING quiz_count > 0
        ORDER BY s.sort_order
    """).fetchall()
    return jsonify({"success": True, "subjects": [dict(r) for r in rows]})


# ── Private Calendar helpers ──────────────────────────────────────────────────

def _send_invite_email(invitee_name, invitee_email, owner_name, cal_name, base_url):
    sender   = os.getenv("MAIL_SENDER", "")
    password = os.getenv("MAIL_PASSWORD", "")
    if not sender or not password or not invitee_email:
        return
    body = f"""Merhaba {invitee_name},

{owner_name} sizi "{cal_name}" adli ozel takvimine davet etti.

Daveti gormek ve kabul etmek icin su adresi ziyaret edin:
{base_url}/calendar

Takvim sayfasinda bildirim ikonuna tiklayarak daveti kabul edebilirsiniz.
"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"{owner_name} sizi ozel takvimine davet etti"
    msg["From"]    = sender
    msg["To"]      = invitee_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, invitee_email, msg.as_string())
    except Exception as e:
        app.logger.warning(f"Davet e-postasi gonderilemedi: {e}")


def _can_access_calendar(db, user_id, is_admin, calendar_id):
    cal = db.execute("SELECT * FROM private_calendars WHERE id=?", (calendar_id,)).fetchone()
    if not cal:
        return None
    if is_admin or cal["owner_id"] == user_id:
        return cal
    inv = db.execute(
        "SELECT 1 FROM private_invites WHERE calendar_id=? AND invitee_id=? AND status='accepted'",
        (calendar_id, user_id)
    ).fetchone()
    return cal if inv else None


@app.route("/api/private/calendars")
def private_calendars_list():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    if is_admin:
        rows = db.execute("""
            SELECT pc.*, u.username AS owner_name
            FROM private_calendars pc JOIN users u ON u.id=pc.owner_id
            ORDER BY pc.created_at DESC
        """).fetchall()
    else:
        rows = db.execute("""
            SELECT pc.*, u.username AS owner_name,
                   CASE WHEN pc.owner_id=? THEN 1 ELSE 0 END AS is_owner
            FROM private_calendars pc JOIN users u ON u.id=pc.owner_id
            WHERE pc.owner_id=?
               OR pc.id IN (
                   SELECT calendar_id FROM private_invites
                   WHERE invitee_id=? AND status='accepted'
               )
            ORDER BY pc.created_at DESC
        """, (user_id, user_id, user_id)).fetchall()
    return jsonify({"success": True, "calendars": [dict(r) for r in rows]})


@app.route("/api/private/calendar/create", methods=["POST"])
def private_calendar_create():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    name    = (request.get_json(silent=True) or {}).get("name", "").strip() or "Ozel Takvimim"
    cur = db.execute("INSERT INTO private_calendars (owner_id, name) VALUES (?,?)", (user_id, name))
    db.commit()
    cal = db.execute(
        "SELECT pc.*, u.username AS owner_name FROM private_calendars pc JOIN users u ON u.id=pc.owner_id WHERE pc.id=?",
        (cur.lastrowid,)
    ).fetchone()
    return jsonify({"success": True, "calendar": dict(cal)})


@app.route("/api/private/calendar/<int:cal_id>/rename", methods=["POST"])
def private_calendar_rename(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    cal = db.execute("SELECT * FROM private_calendars WHERE id=?", (cal_id,)).fetchone()
    if not cal:
        return jsonify({"success": False, "error": "Bulunamadi"}), 404
    if not is_admin and cal["owner_id"] != user_id:
        return jsonify({"success": False, "error": "Yetkisiz"}), 403
    name = (request.get_json(silent=True) or {}).get("name", "").strip()
    if not name:
        return jsonify({"success": False, "error": "Isim bos olamaz"}), 400
    db.execute("UPDATE private_calendars SET name=? WHERE id=?", (name, cal_id))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/private/calendar/<int:cal_id>", methods=["DELETE"])
def private_calendar_delete(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    cal = db.execute("SELECT * FROM private_calendars WHERE id=?", (cal_id,)).fetchone()
    if not cal:
        return jsonify({"success": False, "error": "Bulunamadi"}), 404
    if not is_admin and cal["owner_id"] != user_id:
        return jsonify({"success": False, "error": "Yetkisiz"}), 403
    db.execute("DELETE FROM private_reservations WHERE calendar_id=?", (cal_id,))
    db.execute("DELETE FROM private_notifications WHERE calendar_id=?", (cal_id,))
    db.execute("DELETE FROM private_invites WHERE calendar_id=?", (cal_id,))
    db.execute("DELETE FROM private_calendars WHERE id=?", (cal_id,))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/private/calendar/<int:cal_id>/data")
def private_calendar_data(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    cal = _can_access_calendar(db, user_id, is_admin, cal_id)
    if not cal:
        return jsonify({"success": False, "error": "Erisim yok"}), 403
    year   = int(request.args.get("year",  datetime.now().year))
    month  = int(request.args.get("month", datetime.now().month))
    prefix = f"{year}-{month:02d}"
    rows = db.execute("""
        SELECT pr.date, pr.color, pr.username, pr.user_id, pr.timestamp
        FROM private_reservations pr
        WHERE pr.calendar_id=? AND substr(pr.date,1,7)=?
        ORDER BY pr.timestamp DESC
    """, (cal_id, prefix)).fetchall()
    res = {}
    for r in rows:
        if r["date"] not in res:
            res[r["date"]] = {"userId": r["user_id"], "username": r["username"],
                              "color": r["color"],   "timestamp": r["timestamp"]}
    members = db.execute("""
        SELECT u.id, u.username, u.color FROM users u
        WHERE u.id=(SELECT owner_id FROM private_calendars WHERE id=?)
        UNION
        SELECT u.id, u.username, u.color FROM users u
        JOIN private_invites pi ON pi.invitee_id=u.id
        WHERE pi.calendar_id=? AND pi.status='accepted'
    """, (cal_id, cal_id)).fetchall()
    all_users = db.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    return jsonify({
        "success": True,
        "calendar": dict(cal),
        "reservations": res,
        "members": [dict(m) for m in members],
        "all_users": [dict(u) for u in all_users],
        "is_owner": (cal["owner_id"] == user_id) or is_admin
    })


@app.route("/api/private/calendar/<int:cal_id>/save", methods=["POST"])
def private_calendar_save(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    if not _can_access_calendar(db, user_id, is_admin, cal_id):
        return jsonify({"success": False, "error": "Erisim yok"}), 403
    changes  = (request.get_json(silent=True) or {}).get("changes", {})
    color    = session.get("color") or "#4caf50"
    username = session.get("username") or ""
    for date, info in changes.items():
        if not isinstance(date, str) or len(date) != 10:
            continue
        if info is None:
            db.execute("DELETE FROM private_reservations WHERE calendar_id=? AND user_id=? AND date=?",
                       (cal_id, user_id, date))
        else:
            ts = (info.get("timestamp") if isinstance(info, dict) else None) or datetime.utcnow().isoformat(timespec="seconds")
            db.execute("DELETE FROM private_reservations WHERE calendar_id=? AND user_id=? AND date=?",
                       (cal_id, user_id, date))
            db.execute("INSERT INTO private_reservations (calendar_id,user_id,date,color,username,timestamp) VALUES (?,?,?,?,?,?)",
                       (cal_id, user_id, date, color, username, ts))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/private/calendar/<int:cal_id>/invite", methods=["POST"])
def private_calendar_invite(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    cal = db.execute("SELECT * FROM private_calendars WHERE id=?", (cal_id,)).fetchone()
    if not cal:
        return jsonify({"success": False, "error": "Bulunamadi"}), 404
    if not is_admin and cal["owner_id"] != user_id:
        return jsonify({"success": False, "error": "Sadece sahip davet edebilir"}), 403
    invitee_id = int((request.get_json(silent=True) or {}).get("user_id", 0))
    if invitee_id == user_id:
        return jsonify({"success": False, "error": "Kendinizi davet edemezsiniz"}), 400
    invitee = db.execute("SELECT id, username, email FROM users WHERE id=?", (invitee_id,)).fetchone()
    if not invitee:
        return jsonify({"success": False, "error": "Kullanici bulunamadi"}), 404
    existing = db.execute("SELECT id, status FROM private_invites WHERE calendar_id=? AND invitee_id=?",
                          (cal_id, invitee_id)).fetchone()
    if existing and existing["status"] == "accepted":
        return jsonify({"success": False, "error": "Bu kisi zaten uye"}), 400
    if existing:
        db.execute("UPDATE private_invites SET status='pending' WHERE id=?", (existing["id"],))
    else:
        db.execute("INSERT INTO private_invites (calendar_id,invitee_id,status) VALUES (?,?,'pending')",
                   (cal_id, invitee_id))
    db.execute("DELETE FROM private_notifications WHERE user_id=? AND calendar_id=?", (invitee_id, cal_id))
    db.execute("INSERT INTO private_notifications (user_id,calendar_id,invited_by_name,calendar_name) VALUES (?,?,?,?)",
               (invitee_id, cal_id, session.get("username",""), cal["name"]))
    db.commit()
    base_url = os.getenv("BASE_URL", request.host_url.rstrip("/"))
    _send_invite_email(invitee["username"], invitee["email"] or "", session.get("username",""), cal["name"], base_url)
    return jsonify({"success": True, "invited": invitee["username"]})


@app.route("/api/private/calendar/<int:cal_id>/invite/<int:invitee_id>", methods=["DELETE"])
def private_calendar_remove_invite(cal_id, invitee_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    cal = db.execute("SELECT * FROM private_calendars WHERE id=?", (cal_id,)).fetchone()
    if not cal:
        return jsonify({"success": False}), 404
    if not is_admin and cal["owner_id"] != user_id:
        return jsonify({"success": False, "error": "Yetkisiz"}), 403
    db.execute("DELETE FROM private_invites WHERE calendar_id=? AND invitee_id=?", (cal_id, invitee_id))
    db.execute("DELETE FROM private_reservations WHERE calendar_id=? AND user_id=?", (cal_id, invitee_id))
    db.execute("DELETE FROM private_notifications WHERE calendar_id=? AND user_id=?", (cal_id, invitee_id))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/private/notifications")
def private_notifications():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    rows = db.execute("SELECT * FROM private_notifications WHERE user_id=? ORDER BY created_at DESC",
                      (int(session["user_id"]),)).fetchall()
    return jsonify({"success": True, "notifications": [dict(r) for r in rows]})


@app.route("/api/private/notification/<int:notif_id>/accept", methods=["POST"])
def private_notification_accept(notif_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    notif = db.execute("SELECT * FROM private_notifications WHERE id=? AND user_id=?",
                       (notif_id, user_id)).fetchone()
    if not notif:
        return jsonify({"success": False, "error": "Bildirim bulunamadi"}), 404
    db.execute("UPDATE private_invites SET status='accepted' WHERE calendar_id=? AND invitee_id=?",
               (notif["calendar_id"], user_id))
    db.execute("DELETE FROM private_notifications WHERE id=?", (notif_id,))
    db.commit()
    cal = db.execute(
        "SELECT pc.*, u.username AS owner_name FROM private_calendars pc JOIN users u ON u.id=pc.owner_id WHERE pc.id=?",
        (notif["calendar_id"],)
    ).fetchone()
    return jsonify({"success": True, "calendar": dict(cal) if cal else None})


@app.route("/api/private/notification/<int:notif_id>", methods=["DELETE"])
def private_notification_dismiss(notif_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM private_notifications WHERE id=? AND user_id=?",
               (notif_id, int(session["user_id"])))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/year_reservations")
def year_reservations():
    """Return all reservations for a given year (for year overview)."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    year = int(request.args.get("year", datetime.now().year))
    rows = db.execute("""
        SELECT r.date, u.username, u.color, u.id AS user_id
        FROM reservations r JOIN users u ON r.user_id = u.id
        WHERE substr(r.date, 1, 4) = ?
        ORDER BY r.date
    """, (str(year),)).fetchall()
    data = {}
    for r in rows:
        if r["date"] not in data:
            data[r["date"]] = {"username": r["username"], "color": r["color"], "userId": r["user_id"]}
    return jsonify({"success": True, "year": year, "reservations": data})


@app.route("/api/private/calendar/<int:cal_id>/comments")
def private_calendar_comments(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    if not _can_access_calendar(db, user_id, is_admin, cal_id):
        return jsonify({"success": False}), 403
    year  = int(request.args.get("year",  datetime.now().year))
    month = int(request.args.get("month", datetime.now().month))
    prefix = f"{year}-{month:02d}"
    rows = db.execute("""
        SELECT c.id, c.comment, c.created_at, u.username, u.color
        FROM private_calendar_comments c JOIN users u ON u.id=c.user_id
        WHERE c.calendar_id=? AND substr(c.created_at,1,7)=?
        ORDER BY c.created_at ASC
    """, (cal_id, prefix)).fetchall()
    return jsonify({"success": True, "comments": [dict(r) for r in rows]})


@app.route("/api/private/calendar/<int:cal_id>/comments", methods=["POST"])
def private_calendar_add_comment(cal_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    if not _can_access_calendar(db, user_id, is_admin, cal_id):
        return jsonify({"success": False}), 403
    text = (request.get_json(silent=True) or {}).get("comment", "").strip()
    if not text:
        return jsonify({"success": False, "error": "Boş mesaj"}), 400
    now = datetime.utcnow().isoformat(timespec="seconds")
    db.execute(
        "INSERT INTO private_calendar_comments (calendar_id, user_id, comment, created_at) VALUES (?,?,?,?)",
        (cal_id, user_id, text, now)
    )
    db.commit()
    urow = db.execute("SELECT username, color FROM users WHERE id=?", (user_id,)).fetchone()
    return jsonify({"success": True, "comment": {
        "comment": text, "created_at": now,
        "username": urow["username"], "color": urow["color"]
    }})



def ensure_services_schema(db) -> None:
    """Modular services: user preferences + rent + shopping."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_active_services (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            service_id   TEXT    NOT NULL,
            sort_order   INTEGER DEFAULT 0,
            activated_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, service_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS rental_properties (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name         TEXT    NOT NULL,
            address      TEXT    DEFAULT '',
            monthly_rent REAL    DEFAULT 0,
            payment_day  INTEGER DEFAULT 1,
            color        TEXT    DEFAULT '#3b82f6',
            notes        TEXT    DEFAULT '',
            tenant_name  TEXT    DEFAULT '',
            tenant_phone TEXT    DEFAULT '',
            created_at   TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS rental_payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount      REAL    NOT NULL,
            due_date    TEXT    NOT NULL,
            paid_date   TEXT,
            status      TEXT    DEFAULT 'pending',
            note        TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Additive migrations for existing tables
    rp_cols = _table_columns(db, "rental_properties") if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_properties'").fetchone() else set()
    if rp_cols and "tenant_name"  not in rp_cols: db.execute("ALTER TABLE rental_properties ADD COLUMN tenant_name TEXT DEFAULT ''")
    if rp_cols and "tenant_phone" not in rp_cols: db.execute("ALTER TABLE rental_properties ADD COLUMN tenant_phone TEXT DEFAULT ''")
    db.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name       TEXT    NOT NULL DEFAULT 'Alışveriş Listesi',
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS shopping_list_members (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(list_id, user_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS shopping_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id    INTEGER NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
            added_by   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name       TEXT    NOT NULL,
            quantity   TEXT    DEFAULT '',
            qty_num    REAL    DEFAULT 1,
            category   TEXT    DEFAULT '',
            checked    INTEGER DEFAULT 0,
            checked_by INTEGER,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS shopping_item_history (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name     TEXT    NOT NULL,
            category TEXT    DEFAULT '',
            use_count INTEGER DEFAULT 1,
            UNIQUE(user_id, name)
        )
    """)
    # Additive migrations for shopping_items
    si_cols = _table_columns(db, "shopping_items") if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopping_items'").fetchone() else set()
    if si_cols and "qty_num"  not in si_cols: db.execute("ALTER TABLE shopping_items ADD COLUMN qty_num REAL DEFAULT 1")
    if si_cols and "category" not in si_cols: db.execute("ALTER TABLE shopping_items ADD COLUMN category TEXT DEFAULT ''")
    db.commit()


AVAILABLE_SERVICES = [
    {"id": "personal_cal", "icon": "🔒", "title": "Kişisel Takvim",   "desc": "Sadece sana özel, paylaşılabilir takvim.", "admin_only": False},
    {"id": "rent",         "icon": "🏠", "title": "Kira Takibi",      "desc": "Daire kira ödemelerini takip et.",          "admin_only": False},
    {"id": "shopping",     "icon": "🛒", "title": "Ortak Alışveriş",  "desc": "Paylaşılan alışveriş listesi.",             "admin_only": False},
    {"id": "ppl",          "icon": "✈️", "title": "PPL Teori",        "desc": "Pilotaj sınav hazırlık platformu.",         "admin_only": False},
]


# ══════════════════════ SERVICES API ══════════════════════════════════════════

@app.route("/api/user/services")
def get_user_services():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db       = get_db()
    user_id  = int(session["user_id"])
    is_admin = bool(session.get("is_admin"))
    rows = db.execute(
        "SELECT service_id FROM user_active_services WHERE user_id=? ORDER BY sort_order",
        (user_id,)
    ).fetchall()
    active = [r["service_id"] for r in rows]
    services = [s for s in AVAILABLE_SERVICES if not s["admin_only"] or is_admin]
    return jsonify({"success": True, "active": active, "available": services})


@app.route("/api/user/services/<service_id>", methods=["POST"])
def activate_service(service_id):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    svc_ids = [s["id"] for s in AVAILABLE_SERVICES]
    if service_id not in svc_ids:
        return jsonify({"success": False, "error": "Bilinmeyen servis"}), 400
    db      = get_db()
    user_id = int(session["user_id"])
    count   = db.execute(
        "SELECT COUNT(*) FROM user_active_services WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    db.execute(
        "INSERT OR IGNORE INTO user_active_services (user_id, service_id, sort_order) VALUES (?,?,?)",
        (user_id, service_id, count)
    )
    db.commit()
    return jsonify({"success": True})


@app.route("/api/user/services/<service_id>", methods=["DELETE"])
def deactivate_service(service_id):
    """Remove service AND delete all associated user data."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    # Delete service-specific data
    if service_id == "personal_cal":
        cals = db.execute(
            "SELECT id FROM private_calendars WHERE owner_id=?", (user_id,)
        ).fetchall()
        for cal in cals:
            db.execute("DELETE FROM private_reservations     WHERE calendar_id=?", (cal["id"],))
            db.execute("DELETE FROM private_notifications    WHERE calendar_id=?", (cal["id"],))
            db.execute("DELETE FROM private_invites          WHERE calendar_id=?", (cal["id"],))
            db.execute("DELETE FROM private_calendar_comments WHERE calendar_id=?", (cal["id"],))
        db.execute("DELETE FROM private_calendars WHERE owner_id=?", (user_id,))
        db.execute("DELETE FROM private_notifications WHERE user_id=?", (user_id,))
    elif service_id == "rent":
        props = db.execute(
            "SELECT id FROM rental_properties WHERE user_id=?", (user_id,)
        ).fetchall()
        for p in props:
            db.execute("DELETE FROM rental_payments WHERE property_id=?", (p["id"],))
        db.execute("DELETE FROM rental_properties WHERE user_id=?", (user_id,))
    elif service_id == "shopping":
        lists = db.execute(
            "SELECT id FROM shopping_lists WHERE owner_id=?", (user_id,)
        ).fetchall()
        for l in lists:
            db.execute("DELETE FROM shopping_items          WHERE list_id=?", (l["id"],))
            db.execute("DELETE FROM shopping_list_members   WHERE list_id=?", (l["id"],))
        db.execute("DELETE FROM shopping_lists WHERE owner_id=?", (user_id,))
        # Also remove from shared lists
        db.execute("DELETE FROM shopping_list_members WHERE user_id=?", (user_id,))
    db.execute(
        "DELETE FROM user_active_services WHERE user_id=? AND service_id=?",
        (user_id, service_id)
    )
    db.commit()
    return jsonify({"success": True})


# ══════════════════════ RENT TRACKER API ══════════════════════════════════════

@app.route("/api/rent/properties")
def rent_properties():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    rows = db.execute(
        "SELECT * FROM rental_properties WHERE user_id=? ORDER BY created_at",
        (int(session["user_id"]),)
    ).fetchall()
    return jsonify({"success": True, "properties": [dict(r) for r in rows]})


@app.route("/api/rent/property", methods=["POST"])
def rent_add_property():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    data = request.get_json(silent=True) or {}
    cur  = db.execute(
        "INSERT INTO rental_properties (user_id,name,address,monthly_rent,payment_day,color,notes) VALUES (?,?,?,?,?,?,?)",
        (int(session["user_id"]), data.get("name","Daire"), data.get("address",""),
         float(data.get("monthly_rent",0)), int(data.get("payment_day",1)),
         data.get("color","#3b82f6"), data.get("notes",""))
    )
    db.commit()
    row = db.execute("SELECT * FROM rental_properties WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify({"success": True, "property": dict(row)})


@app.route("/api/rent/property/<int:pid>", methods=["PUT"])
def rent_update_property(pid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    data = request.get_json(silent=True) or {}
    db.execute(
        "UPDATE rental_properties SET name=?,address=?,monthly_rent=?,payment_day=?,color=?,notes=?,tenant_name=?,tenant_phone=? WHERE id=? AND user_id=?",
        (data.get("name"), data.get("address",""), float(data.get("monthly_rent",0)),
         int(data.get("payment_day",1)), data.get("color","#3b82f6"), data.get("notes",""),
         data.get("tenant_name",""), data.get("tenant_phone",""),
         pid, int(session["user_id"]))
    )
    db.commit()
    return jsonify({"success": True})


@app.route("/api/rent/property/<int:pid>", methods=["DELETE"])
def rent_delete_property(pid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM rental_payments WHERE property_id=?", (pid,))
    db.execute("DELETE FROM rental_properties WHERE id=? AND user_id=?", (pid, int(session["user_id"])))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/rent/property/<int:pid>/payments")
def rent_payments(pid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    year = int(request.args.get("year", datetime.now().year))
    rows = db.execute(
        "SELECT * FROM rental_payments WHERE property_id=? AND substr(due_date,1,4)=? ORDER BY due_date",
        (pid, str(year))
    ).fetchall()
    return jsonify({"success": True, "payments": [dict(r) for r in rows]})


@app.route("/api/rent/payment", methods=["POST"])
def rent_add_payment():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    data = request.get_json(silent=True) or {}
    cur  = db.execute(
        "INSERT INTO rental_payments (property_id,user_id,amount,due_date,paid_date,status,note) VALUES (?,?,?,?,?,?,?)",
        (int(data["property_id"]), int(session["user_id"]),
         float(data.get("amount",0)), data["due_date"],
         data.get("paid_date") or None,
         data.get("status","pending"), data.get("note",""))
    )
    db.commit()
    row = db.execute("SELECT * FROM rental_payments WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify({"success": True, "payment": dict(row)})


@app.route("/api/rent/payment/<int:pmid>", methods=["PUT"])
def rent_update_payment(pmid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    data = request.get_json(silent=True) or {}
    db.execute(
        "UPDATE rental_payments SET amount=?,due_date=?,paid_date=?,status=?,note=? WHERE id=? AND user_id=?",
        (float(data.get("amount",0)), data.get("due_date"), data.get("paid_date") or None,
         data.get("status","pending"), data.get("note",""), pmid, int(session["user_id"]))
    )
    db.commit()
    return jsonify({"success": True})


@app.route("/api/rent/payment/<int:pmid>", methods=["DELETE"])
def rent_delete_payment(pmid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM rental_payments WHERE id=? AND user_id=?", (pmid, int(session["user_id"])))
    db.commit()
    return jsonify({"success": True})


# ══════════════════════ SHOPPING LIST API ═════════════════════════════════════

@app.route("/api/shopping/lists")
def shopping_lists_api():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    rows = db.execute("""
        SELECT sl.*, u.username AS owner_name,
               CASE WHEN sl.owner_id=? THEN 1 ELSE 0 END AS is_owner
        FROM shopping_lists sl JOIN users u ON u.id=sl.owner_id
        WHERE sl.owner_id=?
           OR sl.id IN (SELECT list_id FROM shopping_list_members WHERE user_id=?)
        ORDER BY sl.created_at DESC
    """, (user_id, user_id, user_id)).fetchall()
    return jsonify({"success": True, "lists": [dict(r) for r in rows]})


@app.route("/api/shopping/list", methods=["POST"])
def shopping_create_list():
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    name = (request.get_json(silent=True) or {}).get("name","Alışveriş Listesi")
    uid  = int(session["user_id"])
    cur  = db.execute("INSERT INTO shopping_lists (owner_id,name) VALUES (?,?)", (uid, name))
    db.commit()
    row = db.execute(
        "SELECT sl.*,u.username AS owner_name,1 AS is_owner FROM shopping_lists sl JOIN users u ON u.id=sl.owner_id WHERE sl.id=?",
        (cur.lastrowid,)
    ).fetchone()
    return jsonify({"success": True, "list": dict(row)})


@app.route("/api/shopping/list/<int:lid>", methods=["DELETE"])
def shopping_delete_list(lid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM shopping_items WHERE list_id=?", (lid,))
    db.execute("DELETE FROM shopping_list_members WHERE list_id=?", (lid,))
    db.execute("DELETE FROM shopping_lists WHERE id=? AND owner_id=?", (lid, int(session["user_id"])))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/shopping/list/<int:lid>/items")
def shopping_items_api(lid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    rows = db.execute(
        "SELECT si.*,u.username AS added_by_name,u.color AS added_by_color FROM shopping_items si JOIN users u ON u.id=si.added_by WHERE si.list_id=? ORDER BY si.checked ASC, si.category ASC, si.created_at ASC",
        (lid,)
    ).fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})


@app.route("/api/shopping/list/<int:lid>/item", methods=["POST"])
def shopping_add_item(lid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    data    = request.get_json(silent=True) or {}
    name     = data.get("name","").strip()
    category = data.get("category","").strip()
    qty_num  = float(data.get("qty_num", 1) or 1)
    quantity = data.get("quantity","").strip()
    if not name:
        return jsonify({"success": False, "error": "İsim gerekli"}), 400
    cur = db.execute(
        "INSERT INTO shopping_items (list_id,added_by,name,quantity,qty_num,category) VALUES (?,?,?,?,?,?)",
        (lid, user_id, name, quantity, qty_num, category)
    )
    # Update history
    db.execute("""
        INSERT INTO shopping_item_history (user_id,name,category,use_count)
        VALUES (?,?,?,1)
        ON CONFLICT(user_id,name) DO UPDATE SET use_count=use_count+1, category=excluded.category
    """, (user_id, name, category))
    db.commit()
    row = db.execute(
        "SELECT si.*,u.username AS added_by_name, u.color AS added_by_color FROM shopping_items si JOIN users u ON u.id=si.added_by WHERE si.id=?",
        (cur.lastrowid,)
    ).fetchone()
    return jsonify({"success": True, "item": dict(row)})


@app.route("/api/shopping/item/<int:iid>/toggle", methods=["POST"])
def shopping_toggle_item(iid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db  = get_db()
    row = db.execute("SELECT * FROM shopping_items WHERE id=?", (iid,)).fetchone()
    if not row:
        return jsonify({"success": False}), 404
    new_checked = 0 if row["checked"] else 1
    db.execute(
        "UPDATE shopping_items SET checked=?,checked_by=? WHERE id=?",
        (new_checked, int(session["user_id"]) if new_checked else None, iid)
    )
    db.commit()
    return jsonify({"success": True, "checked": new_checked})


@app.route("/api/shopping/item/<int:iid>", methods=["DELETE"])
def shopping_delete_item(iid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM shopping_items WHERE id=?", (iid,))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/shopping/list/<int:lid>/invite", methods=["POST"])
def shopping_invite(lid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    lst     = db.execute("SELECT * FROM shopping_lists WHERE id=?", (lid,)).fetchone()
    if not lst or lst["owner_id"] != user_id:
        return jsonify({"success": False, "error": "Yetkisiz"}), 403
    inv_id  = int((request.get_json(silent=True) or {}).get("user_id", 0))
    db.execute("INSERT OR IGNORE INTO shopping_list_members (list_id,user_id) VALUES (?,?)", (lid, inv_id))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/shopping/list/<int:lid>/member/<int:mid>", methods=["DELETE"])
def shopping_remove_member(lid, mid):
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    db.execute("DELETE FROM shopping_list_members WHERE list_id=? AND user_id=?", (lid, mid))
    db.commit()
    return jsonify({"success": True})



@app.route("/api/shopping/history")
def shopping_history():
    """Return user's most-used shopping items for autocomplete."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db = get_db()
    rows = db.execute(
        "SELECT name, category FROM shopping_item_history WHERE user_id=? ORDER BY use_count DESC LIMIT 50",
        (int(session["user_id"]),)
    ).fetchall()
    return jsonify({"success": True, "history": [dict(r) for r in rows]})


@app.route("/api/rent/property/<int:pid>/generate_payments", methods=["POST"])
def rent_generate_payments(pid):
    """Auto-generate monthly payments for the next N months."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db      = get_db()
    user_id = int(session["user_id"])
    prop    = db.execute("SELECT * FROM rental_properties WHERE id=? AND user_id=?", (pid, user_id)).fetchone()
    if not prop:
        return jsonify({"success": False, "error": "Bulunamadı"}), 404
    data   = request.get_json(silent=True) or {}
    months = int(data.get("months", 12))
    from_date = data.get("from_date") or datetime.now().strftime("%Y-%m-01")
    year, month = int(from_date[:4]), int(from_date[5:7])
    created = 0
    for _ in range(months):
        import calendar as cal_mod
        last_day = cal_mod.monthrange(year, month)[1]
        day = min(prop["payment_day"], last_day)
        due = f"{year}-{month:02d}-{day:02d}"
        exists = db.execute(
            "SELECT 1 FROM rental_payments WHERE property_id=? AND due_date=?", (pid, due)
        ).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO rental_payments (property_id,user_id,amount,due_date,status) VALUES (?,?,?,?,'pending')",
                (pid, user_id, prop["monthly_rent"], due)
            )
            created += 1
        month += 1
        if month > 12:
            month = 1; year += 1
    db.commit()
    return jsonify({"success": True, "created": created})


@app.route("/api/rent/notifications")
def rent_notifications():
    """Return upcoming/overdue rent payments for notification badge."""
    if "user_id" not in session:
        return jsonify({"success": False}), 401
    db   = get_db()
    user_id = int(session["user_id"])
    today   = datetime.now().strftime("%Y-%m-%d")
    soon    = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    rows = db.execute("""
        SELECT rp.name AS prop_name, rpa.due_date, rpa.amount, rpa.status,
               rpa.id AS payment_id, rpa.property_id
        FROM rental_payments rpa
        JOIN rental_properties rp ON rp.id = rpa.property_id
        WHERE rpa.user_id=? AND rpa.status='pending'
          AND (rpa.due_date <= ? OR rpa.due_date <= ?)
        ORDER BY rpa.due_date
    """, (user_id, today, soon)).fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)