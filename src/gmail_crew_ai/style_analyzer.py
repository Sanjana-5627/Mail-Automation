import os
import json
import imaplib
import email
from datetime import datetime, timedelta
from typing import Dict, Any, List

DATA_DIR = "data"
STYLE_FILE = os.path.join(DATA_DIR, "writing_style.json")

DEFAULT_STYLE = """
Writing Style Guidelines:
- Tone: Professional, warm, concise, and direct.
- Greeting: "Hi [Name]," or "Hello [Name],"
- Sign-off: "Best regards,\nTony Kipkemboi"
- Formatting: Short paragraphs, clear bullet points when explaining steps.
"""

def get_user_writing_style() -> str:
    """Retrieve or generate writing style summary based on sent emails."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(STYLE_FILE):
        try:
            with open(STYLE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                updated_at_str = data.get("updated_at")
                if updated_at_str:
                    updated_at = datetime.fromisoformat(updated_at_str)
                    if datetime.now() - updated_at < timedelta(days=7):
                        return data.get("style_summary", DEFAULT_STYLE)
        except Exception:
            pass

    # Attempt IMAP fetch from Sent folder if credentials exist
    email_address = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("APP_PASSWORD")

    style_summary = DEFAULT_STYLE
    if email_address and app_password:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_address, app_password)
            sent_folders = ['"[Gmail]/Sent Mail"', 'Sent', '[Gmail]/Sent']
            for folder in sent_folders:
                res, _ = mail.select(folder, readonly=True)
                if res == "OK":
                    res, data = mail.search(None, "ALL")
                    if res == "OK" and data[0]:
                        msg_ids = data[0].split()[-10:]
                        greetings = []
                        signoffs = []
                        for msg_id in msg_ids:
                            res, msg_data = mail.fetch(msg_id, "(RFC822)")
                            if res == "OK" and msg_data[0]:
                                msg = email.message_from_bytes(msg_data[0][1])
                                # Extract basic text
                                payload = msg.get_payload()
                                if isinstance(payload, str):
                                    lines = [l.strip() for l in payload.split("\n") if l.strip()]
                                    if lines:
                                        greetings.append(lines[0])
                                        signoffs.append(lines[-1])
                        if greetings and signoffs:
                            style_summary = f"""
Writing Style Guidelines (Analyzed from Sent Emails):
- Most Common Greeting: {greetings[0]}
- Most Common Sign-off: {signoffs[-1]}
- Tone: Direct, responsive, helpful.
"""
                    break
            mail.logout()
        except Exception as e:
            print(f"Note: Could not analyze Sent folder for writing style ({e}). Using default style.")

    # Save to cache
    try:
        with open(STYLE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "updated_at": datetime.now().isoformat(),
                "style_summary": style_summary
            }, f, indent=2)
    except Exception:
        pass

    return style_summary
