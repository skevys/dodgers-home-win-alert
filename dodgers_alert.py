import os
import smtplib
import requests
from datetime import datetime, timedelta
from email.message import EmailMessage
from zoneinfo import ZoneInfo

DODGERS_ID = 119
        
def load_subscribers():
    with open("subscribers.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def send_email(subject, body):
    recipients = load_subscribers()

    msg = EmailMessage()
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_FROM"], os.environ["EMAIL_PASSWORD"])
        smtp.send_message(msg)
        
def main():
    la_time = datetime.now(ZoneInfo("America/Los_Angeles"))
    check_date = "2026-06-02" #check_date = (la_time - timedelta(days=1)).strftime("%Y-%m-%d")

    url = (
        "https://statsapi.mlb.com/api/v1/schedule"
        f"?sportId=1&teamId={DODGERS_ID}&date={check_date}&hydrate=linescore"
    )

    data = requests.get(url, timeout=30).json()

    for date in data.get("dates", []):
        for game in date.get("games", []):
            home = game["teams"]["home"]
            away = game["teams"]["away"]

            is_home = home["team"]["id"] == DODGERS_ID
            is_final = game["status"]["detailedState"] == "Final"
            dodgers_won = home.get("score", 0) > away.get("score", 0)

            if is_home and is_final and dodgers_won:
                opponent = away["team"]["name"]
                home_score = home["score"]
                away_score = away["score"]

                send_email(
                    f"Dodgers won at home! {home_score}-{away_score}",
                    f"The Dodgers beat the {opponent} at home.\n\n"
                    f"Final score:\n"
                    f"Dodgers {home_score}\n"
                    f"{opponent} {away_score}\n\n"
                    f"Game date: {check_date}"
                )

if __name__ == "__main__":
    main()
