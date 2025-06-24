# nagbot.py  –  send one email + SMS each morning with a fresh alias
import os, random, string, datetime as dt, schedule, time, requests
from dotenv import load_dotenv
from simplelogin import SimpleLogin
from resend import Resend

load_dotenv()

# ---------- CONFIG ----------
SUBDOMAIN  = "pay.alexschupak.com"
DOMAIN_ID  = 255557            # ← your SimpleLogin domain ID
TXT_KEY    = "textbelt"        # free daily SMS quota
# -----------------------------

sl      = SimpleLogin(os.getenv("SL_TOKEN"))
resend  = Resend(api_key=os.getenv("RESEND_API_KEY"))

FRIEND_EMAIL      = os.getenv("FRIEND_EMAIL")
FRIEND_PHONE_SMTP = os.getenv("FRIEND_PHONE_SMTP")       # carrier gateway
FRIEND_PHONE_NUM  = os.getenv("FRIEND_PHONE_NUM")        # plain digits

def fresh_alias():
    # delete yesterday's 'nagbot' alias
    for a in sl.alias.list():
        if a.get("note") == "nagbot":
            sl.alias.delete(a["id"])
    local = "nag" + "".join(random.choices(string.ascii_lowercase, k=6))
    alias = sl.alias.create(
        email_prefix=local,
        domain_id=DOMAIN_ID,
        note="nagbot",
        enabled=True,
    )
    return alias["email"]

def send_email(alias_addr, html):
    data = {
        "from": f"NudgeBot <{alias_addr}>",
        "to":   [FRIEND_EMAIL] + ([FRIEND_PHONE_SMTP] if FRIEND_PHONE_SMTP else []),
        "subject": "Daily mission: ask her out!",
        "html": html,
    }
    resend.emails.send(data=data)

def send_sms_fallback(text):
    r = requests.post("https://textbelt.com/text", {
        "phone": FRIEND_PHONE_NUM,
        "message": text,
        "key": TXT_KEY
    })
    print("Textbelt:", r.json())

def job():
    alias = fresh_alias()
    body  = "<p>Reminder: today's the day — go talk to her 🚀</p>"
    send_email(alias, body)
    if not FRIEND_PHONE_SMTP:
        send_sms_fallback("Ask her out today! – your accountability bot")
    print(f"[{dt.datetime.now()}] sent from {alias}")

# run at 09:00 America/New_York (13:00 UTC)
schedule.every().day.at("09:00").do(job)

if __name__ == "__main__":
    # immediate smoke-test when script starts
    job()
    while True:
        schedule.run_pending()
        time.sleep(30)
