#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask application from app.py
# Note: app.py imports from app/ directory (create_app), but defines all routes
from app import create_app
from models import get_student, get_parent, save_otp, verify_otp
from chatbot import detect_intent, handle_chat, get_help_menu

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Add backward-compatible routes for the existing chatbot
from flask import request, jsonify, session, render_template, redirect, url_for
from datetime import datetime, timedelta
import random, string

# ─── In-memory OTP store (for demo) ───
pending_logins = {}  # phone -> {reg_no, otp, expiry}

def generate_otp():
    return "".join(random.choices(string.digits, k=6))

# ─── PAGES ────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login_page():
    return render_template("index.html")

@app.route("/admin/login")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/student/login")
def student_login_page():
    return render_template("student_login.html")

@app.route("/faculty/login")
def faculty_login_page():
    return render_template("faculty_login.html")

@app.route("/student/dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/faculty/dashboard")
def faculty_dashboard():
    return render_template("faculty_dashboard.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/chat")
def chat():
    if not session.get("authenticated"):
        return redirect(url_for("login_page"))
    return render_template("chat.html",
                           student_name=session.get("student_name", "Student"),
                           reg_no=session.get("reg_no", ""))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ─── AUTH API ─────────────────────────

@app.route("/api/verify_reg", methods=["POST"])
def verify_reg():
    data = request.json
    reg_no = data.get("reg_no", "").strip().upper()
    student = get_student(reg_no)
    if not student:
        return jsonify({"success": False, "message": "Registration number not found. Please check and try again."})
    
    # Handle both old and new student document structures
    if "name" in student:
        student_name = student["name"]
        branch = student.get("branch", "")
    else:
        # New structure with nested personal_info and academic
        personal = student.get("personal_info", {})
        academic = student.get("academic", {})
        student_name = f"{personal.get('first_name', '')} {personal.get('last_name', '')}".strip() or student.get("reg_no", "")
        branch = academic.get("branch", "")
    
    return jsonify({"success": True, "student_name": student_name, "branch": branch})

@app.route("/api/send_otp", methods=["POST"])
def send_otp():
    data = request.json
    reg_no = data.get("reg_no", "").strip().upper()
    phone = data.get("phone", "").strip()

    parent = get_parent(reg_no, phone)
    if not parent:
        return jsonify({"success": False, "message": "Phone number not registered for this student. Contact the academic office."})

    otp = generate_otp()
    expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
    save_otp(phone, otp, expiry)
    pending_logins[phone] = {"reg_no": reg_no, "otp": otp, "expiry": expiry}

    # In production: send via SMS API. For demo, we return it.
    print(f"[OTP] Phone: {phone} | OTP: {otp}")
    return jsonify({
        "success": True,
        "message": f"OTP sent to ******{phone[-4:]}",
        "demo_otp": otp  # Remove in production
    })

@app.route("/api/verify_otp", methods=["POST"])
def verify_otp_route():
    data = request.json
    reg_no = data.get("reg_no", "").strip().upper()
    phone = data.get("phone", "").strip()
    otp_entered = data.get("otp", "").strip()

    if not verify_otp(phone, otp_entered):
        return jsonify({"success": False, "message": "Invalid or expired OTP. Please try again."})

    student = get_student(reg_no)
    
    # Handle both old and new student document structures
    if "name" in student:
        student_name = student["name"]
    else:
        personal = student.get("personal_info", {})
        student_name = f"{personal.get('first_name', '')} {personal.get('last_name', '')}".strip() or student.get("reg_no", "")
    
    session["authenticated"] = True
    session["reg_no"] = reg_no
    session["student_name"] = student_name
    session["parent_phone"] = phone
    session.permanent = False

    return jsonify({"success": True, "message": "Login successful!", "student_name": student_name})

# ─── CHAT API ─────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat_api():
    if not session.get("authenticated"):
        return jsonify({"success": False, "message": "Session expired. Please login again.", "redirect": "/"})

    data = request.json
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"success": False, "message": "Please type a message."})

    reg_no = session.get("reg_no")
    intent = detect_intent(user_msg)
    response = handle_chat(intent, reg_no)

    if response == "LOGOUT":
        session.clear()
        return jsonify({"success": True, "message": "👋 Session ended securely. Goodbye!", "logout": True})

    return jsonify({"success": True, "message": response, "intent": intent})

@app.route("/api/quick_reply", methods=["POST"])
def quick_reply():
    if not session.get("authenticated"):
        return jsonify({"success": False, "message": "Session expired."})

    data = request.json
    action = data.get("action", "")
    reg_no = session.get("reg_no")
    
    # Map quick reply actions to intents
    action_map = {
        "attendance": "attendance",
        "marks": "marks", 
        "cgpa": "cgpa",
        "fees": "fees",
        "backlogs": "backlogs",
        "notifications": "notifications",
        "faculty": "faculty",
        "counselor": "counselor",
        "suggestions": "suggestions",
        "class_advisor": "class_advisor",
        "year_data": "year_semester",
        "help": "help",
        "logout": "logout"
    }
    
    intent = action_map.get(action, action)
    response = handle_chat(intent, reg_no)
    
    if response == "LOGOUT":
        session.clear()
        return jsonify({"success": True, "message": "👋 Session ended securely. Goodbye!", "logout": True})
    
    return jsonify({"success": True, "message": response})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
