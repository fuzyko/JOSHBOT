import os, random, string, json, datetime as dt, schedule, time, requests
from dotenv import load_dotenv

load_dotenv()

# ------------ CONFIG -------------
SUBDOMAIN        = "pay.alexschupak.com"
RESEND_API_KEY   = os.getenv("RESEND_API_KEY")

FRIEND_EMAIL       = os.getenv("FRIEND_EMAIL")
FRIEND_PHONE_SMTP  = os.getenv("FRIEND_PHONE_SMTP")   # 2025550123@vtext.com
FRIEND_PHONE_NUM   = os.getenv("FRIEND_PHONE_NUM")    # plain digits (Textbelt)
# -------- frequency --------------
schedule.every(30).minutes.do(lambda: job())          # ← change 30 to whatever
# ---------------------------------

def random_from() -> str:
    local = "nag" + "".join(random.choices(string.ascii_lowercase, k=6))
    return f"{local}@{SUBDOMAIN}"

def send_email(from_addr: str, html: str) -> None:
    payload = {
        "from": f"JOSHBOT <{from_addr}>",
        "to":   [FRIEND_EMAIL] + ([FRIEND_PHONE_SMTP] if FRIEND_PHONE_SMTP else []),
        "subject": "Time’s ticking – ask her out!",
        "html": html,
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json"
        },
        data=json.dumps(payload),
        timeout=15
    )
    r.raise_for_status()

def send_sms(text: str) -> None:
    requests.post(
        "https://textbelt.com/text",
        data={"phone": FRIEND_PHONE_NUM, "message": text, "key": "textbelt"},
        timeout=10
    )

def job() -> None:
    frm  = random_from()
    html = "<p>Hey Josh — another friendly nudge ⏰.<br>Go ask her out!</p>"
    send_email(frm, html)
    if not FRIEND_PHONE_SMTP and FRIEND_PHONE_NUM:
        send_sms("JOSHBOT: reminder – go ask her out!")
    print(f"[{dt.datetime.now()}] sent from {frm}")

if __name__ == "__main__":
    job()                       # one immediate send
    while True:
        schedule.run_pending()
        time.sleep(30)
