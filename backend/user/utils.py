def send_mail(email,otp):
    from smtplib import SMTP,SMTPAuthenticationError,SMTPException
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    host = "smtp.gmail.com"
    port = 587
    username = "soubhagya.developer@gmail.com"
    password = "Thinkonce@000"
    from_email= username
    to_list = email

    try:
        email_conn = SMTP(host, port)
        email_conn.ehlo()
        email_conn.starttls()
        email_conn.login(username,password)

        the_msg = MIMEMultipart("alternative")
        the_msg['subject'] = "movify - User Reset Password !"
        the_msg["from"] = from_email

        plain_txt = "movify - User Reset Password"
        html_text = """\
            <!DOCTYPE html>
            <html lang="en">
            <body>
            <pre style="background:#e6e3e3;padding:5px;color:red;font-weight:bold;font-family:monospace;border-radius:5px;">
            <p>Use {} OTP to reset password</p>
            </pre>
            </body>
            </html>
        """.format(otp)


        part_1 = MIMEText(plain_txt,'plain')
        part_2 = MIMEText(html_text,"html")
        the_msg.attach(part_1)
        the_msg.attach(part_2)
        email_conn.sendmail(from_email,to_list,the_msg.as_string())
        email_conn.quit()
        return True
    except SMTPException:
        print("SMTPException happened")