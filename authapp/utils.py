import base64
from django.core.mail import EmailMessage
from django.conf import settings

GENDER = (
    ('Male','Male'),
    ('Female','Female'),
    ('Other','Other')
)

class ResponseInfo(object):
    def __init__(self, user=None, **args):
        self.response = {
            "status": args.get('status', 200),
            "error": args.get('error', []),
            "data": args.get('data', []),
            "message": args.get('message', [])
        }

class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.code = 400


def activation_email(email, otp):
    mail_subject = 'Active Account '
    email_byte = email.encode("ascii")
    email_string = base64.b64encode(email_byte)
    enc_email = email_string.decode("ascii")
    link = f"{settings.DOMAIN}active/{enc_email}/{otp}"
    message = ( f'Hi, your activation link is (Note:-This link work only one time!) {link} ' )
    email = EmailMessage(mail_subject, message, to=[email])  
    email.send()
    
def forgot_password_email(email, otp):
    mail_subject = 'OTP for Forgot Password.'
    message = ( f'Hi, your OTP for forgot password :- {otp} ' )
    email = EmailMessage(mail_subject, message, to=[email])  
    email.send()
