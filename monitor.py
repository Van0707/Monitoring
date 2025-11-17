import subprocess
import requests
from datetime import datetime
import json

# ==========================
# CONFIGURATION
# ==========================
GEMINI_API_KEY = "AIzaSyA8Y2v7K-kzChPgzMUQLa2fDAp7OEZA2AY"   # <-- GANTI DI SINI
FONNTE_TOKEN = "XdH2YJbSGY9XvzsbLzz2"    # Token
TARGET_NUMBER = "6282290090567"               # Nomor WA tujuan

SERVICES = [
    ("apache2", "Apache Web Server"),
    ("mysql", "MySQL Database"),
    ("node", "NodeJS Backend")
]


# ==========================
# FUNCTION: Check Systemd Services
# ==========================
def check_service(service_name):
    try:
        status = subprocess.check_output(
            ["systemctl", "is-active", service_name],
            stderr=subprocess.STDOUT
        ).decode().strip()
        return status
    except:
        return "unknown"


# ==========================
# FUNCTION: Check NodeJS (non-systemd)
# ==========================
def check_nodejs():
    try:
        subprocess.check_output(["pgrep", "-f", "node"])
        return "active"
    except:
        return "inactive"


# ==========================
# GEMINI AI ANALYSIS
# ==========================
def analyze_issue(name, status):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Service Monitoring Report:
    Service: {name}
    Status: {status}

    Jelaskan kemungkinan penyebab service ini mati atau error.
    Berikan penjelasan singkat & jelas.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "AI Analysis Error."


# ==========================
# WHATSAPP ALERT (FONNTE)
# ==========================
def send_whatsapp(message):
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_TOKEN}
    
    data = {
        "target": TARGET_NUMBER,
        "message": message,
    }

    response = requests.post(url, headers=headers, data=data)
    return response.text


# ==========================
# MAIN PROGRAM
# ==========================
if __name__ == "__main__":
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alert_messages = []

    print("=== CHECKING SERVICES ===")

    for service, display_name in SERVICES:

        if service == "node":
            status = check_nodejs()
        else:
            status = check_service(service)

        print(f"{display_name}: {status}")

        if status != "active":
            ai_reason = analyze_issue(display_name, status)
            alert_messages.append(
                f"🚨 SERVICE ALERT ({timestamp})\n"
                f"Service: {display_name}\n"
                f"Status: {status}\n\n"
                f"💡 Gemini AI Analysis:\n{ai_reason}\n"
                "--------------------------------------\n"
            )

    if alert_messages:
        final_message = "\n".join(alert_messages)
        print("Sending WhatsApp alert...\n")
        result = send_whatsapp(final_message)
        print("WhatsApp Response:", result)
    else:
        print("[✓] All services running normally.")
