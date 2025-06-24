# nagbot.py  –  fires one reminder, then exits
import os, json, requests, random, string, datetime as dt
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────
SUBDOMAIN         = "pay.alexschupak.com"            # verified with Resend
RESEND_API_KEY    = os.getenv("RESEND_API_KEY")

# Comma-separated lists from GitHub secrets
EMAILS      = [e.strip() for e in os.getenv("FRIEND_EMAILS", "").split(",")      if e.strip()]
PHONE_SMTPS = [p.strip() for p in os.getenv("FRIEND_PHONE_SMTPS", "").split(",") if p.strip()]
PHONE_NUMS  = [n.strip() for n in os.getenv("FRIEND_PHONE_NUMS", "").split(",")  if n.strip()]
# ─────────────────────────────────────────────────────

def random_from() -> str:
    local = "nag" + "".join(random.choices(string.ascii_lowercase, k=6))
    return f"{local}@{SUBDOMAIN}"

def send_resend(to_list, sender, html):
    payload = {
        "from":   f"ALEX <{sender}>",
        "to":     to_list,
        "subject": "PAY ME",
        "html":    html,
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}",
                 "Content-Type":  "application/json"},
        data=json.dumps(payload),
        timeout=15,
    )
    r.raise_for_status()

def send_sms(number, text):
    r = requests.post("https://textbelt.com/text", {
        "phone": number, "message": text, "key": "textbelt"
    }, timeout=10)
    print(f"Textbelt {number}:", r.json())

def main():
    sender = random_from()
    html   = "<p>HI&nbsp; — PAY<br>ME</p>"

    # e-mail via Resend (normal inboxes + carrier SMTP addresses)
    to_all_emails = EMAILS + PHONE_SMTPS
    if to_all_emails:
        send_resend(to_all_emails, sender, html)

    # Textbelt fallback for plain numbers
    for num in PHONE_NUMS:
        if num:
            send_sms(num, "PAY ME")

    print(f"[{dt.datetime.now()}] sent from {sender}")

if __name__ == "__main__":
    main()
