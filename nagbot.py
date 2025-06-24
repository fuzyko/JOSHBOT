# nagbot.py  –  fires once, then exits
import os, json, requests, random, string, datetime as dt
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────
SUBDOMAIN         = "pay.alexschupak.com"          # verified in Resend
RESEND_API_KEY    = os.getenv("RESEND_API_KEY")

FRIEND_EMAIL      = os.getenv("FRIEND_EMAIL")
FRIEND_PHONE_SMTP = os.getenv("FRIEND_PHONE_SMTP")  # e.g. 5551234567@vtext.com
FRIEND_PHONE_NUM  = os.getenv("FRIEND_PHONE_NUM")   # digits only (Textbelt fallback)
# ──────────────────────────────────────────────────────────

def random_from() -> str:
    local = "nag" + "".join(random.choices(string.ascii_lowercase, k=6))
    return f"{local}@{SUBDOMAIN}"

def send_email(sender: str, html: str) -> None:
    payload = {
        "from":   f"JOSHBOT <{sender}>",
        "to":     [FRIEND_EMAIL] + ([FRIEND_PHONE_SMTP] if FRIEND_PHONE_SMTP else []),
        "subject": "Friendly reminder – ask her out!",
        "html":    html,
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json",
        },
        data=json.dumps(payload),
        timeout=15,
    )
    r.raise_for_status()

def send_sms(text: str) -> None:
    r = requests.post(
        "https://textbelt.com/text",
        data={"phone": FRIEND_PHONE_NUM, "message": text, "key": "textbelt"},
        timeout=10,
    )
    print("Textbelt:", r.json())

def main() -> None:
    sender = random_from()
    html   = "<p>HI&nbsp; — PAY <br>ME</p>"   # ← edit message here
    send_email(sender, html)
    if not FRIEND_PHONE_SMTP and FRIEND_PHONE_NUM:
        send_sms("YOU OWE ME MONEY")
    print(f"[{dt.datetime.now()}] sent from {sender}")

if __name__ == "__main__":
    main()
