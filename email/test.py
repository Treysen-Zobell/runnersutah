import smtplib
from email.mime.text import MIMEText

GMAIL_USERNAME = "runnersutah.api@gmail.com"
GMAIL_APP_PASSWORD = "GMCWMXKMIZCZLLBS"

message = MIMEText("Hello there")
message["Subject"] = "Test Message"
message["To"] = "treysenzobell@gmail.com"
message["From"] = f"{GMAIL_USERNAME}@gmail.com"

smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtp_server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
smtp_server.sendmail(message["From"], "treysenzobell@gmail.com", message.as_string())
smtp_server.quit()
