# nagbot.py  –  hourly JOSHBOT using only Resend (+ optional Textbelt SMS)
import os, random, string, datetime as dt, schedule, time, requests
from dotenv import load_dotenv
from resend import Resend

load_dotenv()

SUBDOMAIN = "pay.alexschupak.com"      # your verified sub-domain
resend   = Resend(api_key=os.getenv("RESEND_API_KEY"))

FRIEND_EMAIL      = os.getenv("FRIEND_EMAIL")
FRIEND_PHONE_SMTP = os.getenv("FRIEND_PHONE_SMTP")   # e.g. 2025550123@vtext.com
FRIEND_PHONE_NUM  = os.getenv("FRIEND_PHONE_NUM")    # plain digits for Textbelt fallback

def random_from():
    local = "nag" + "".join(random.choices(string.ascii_lowercase, k=6))
    return f"{local}@{SUBDOMAIN}"

def send_email(from_addr, html):
    data = {
        "from": f"JOSHBOT <{from_addr}>",
        "to":   [FRIEND_EMAIL] + ([FRIEND_PHONE_SMTP] if FRIEND_PHONE_SMTP else []),
        "subject": "Hourly mission: ask her out!",
        "html": html,
    }
    resend.emails.send(data=data)

def send_sms(text):
    requests.post("https://textbelt.com/text", {
        "phone": FRIEND_PHONE_NUM,
        "message": text,
        "key": "textbelt"
    })

def job():
    frm  = random_from()
    html = "<p>Hey Josh—time’s ticking ⏰. Go ask her out!</p>"
    send_email(frm, html)
    if not FRIEND_PHONE_SMTP and FRIEND_PHONE_NUM:
        send_sms("Another gentle nudge from JOSHBOT — go ask her out!")
    print(f"[{dt.datetime.now()}] sent from {frm}")

# run once an hour, on the hour
schedule.every().hour.at(":00").do(job)

if __name__ == "__main__":
    job()                    # immediate smoke-test
    while True:
        schedule.run_pending()
        time.sleep(30)
