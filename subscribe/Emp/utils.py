from django.conf import settings
from django.core.mail import EmailMessage
import random

def gen_user_id(fname, lname):
    user_name = str(fname).lower() + str(lname[0]).lower()
    user_id = str(user_name) + str(random.randrange(1000, 9999))
    print(user_id)
    return user_id


def gen_emp_id(fname):
    number_list = [x for x in range(10)]
    code_items = []
    for i in range(4):
        num = random.choice(number_list)
        code_items.append(num)
    code_string = "".join(str(item) for item in code_items)
    emp_id = str(fname[0]) + str(code_string)
    return emp_id


def send_mail(template_id, email, template_data):
    """
    Sends mail
    """
    msg = EmailMessage(from_email=settings.DEFAULT_FROM_EMAIL, to=email)
    print("hereeeeeee")
    msg.template_id = template_id
    print("jere")
    msg.dynamic_template_data = template_data
    print("hereeeeeeeee123")
    msg.send(fail_silently=False)
    print(msg)