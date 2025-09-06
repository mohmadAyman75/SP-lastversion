import smtplib
import random
from email.message import EmailMessage
import re

class gmail():
    # Generate random code
    def __init__(self):
        self.random_var= random.randint(100000, 999999)  # 6-digit code


    def send_message_random_code(self,email):
        fromaddr = 'projectsp881@gmail.com'

        password = 'fupl gium vqrp hudv'  # Replace with actual app password

            # Create email message
        msg = EmailMessage()
        msg['From'] = fromaddr
        msg['To'] = email
        msg['Subject'] = 'Verification Code'
        msg.set_content(f"Welcome to the library application!\nYour verification code is: {self.random_var}\ndon`t send this code for any one")

            # Send email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.login(fromaddr, password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def get_random_var(self):
        print(self.random_var)
        return self.random_var

    def is_valid_gmail(self,email):
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if re.match(pattern, email):
            return 1
        else:
            return 0
        
    def send_new_update(self,email):
        fromaddr = 'projectsp881@gmail.com'

        password = 'fupl gium vqrp hudv'  # Replace with actual app password

            # Create email message
        msg = EmailMessage()
        msg['From'] = fromaddr
        msg['To'] = email
        msg['Subject'] = 'نور المعرفه'
        msg.set_content(f"""Dear [User],

    Thank you for subscribing to our newsletter! 🎉 You’ll now receive the latest updates, exclusive content, and special offers directly to your inbox.

    If you ever change your mind, you can unsubscribe at any time using the link below.

    Happy reading!
    The [نور المعرفه] Team""")

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.login(fromaddr, password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
