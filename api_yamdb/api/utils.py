import random

from django.core.mail import send_mail


def send_code_to_email(serializer):
    code = int(''.join([str(random.randint(0, 10)) for _ in range(5)]))
    subject = 'Verification code from yabdb'
    message = f'Your verification code:\n{code}\nThanks for using yabdb.'
    created_object = serializer.save(confirmation_code=code)
    send_mail(
        subject,
        message,
        'from@example.com',
        [created_object.email],
        fail_silently=False,
    )
