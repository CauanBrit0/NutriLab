import re
from django.contrib import messages
from django.contrib.messages import constants
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def password_is_valid(request,password, confirm_password):

    if len(password.strip()) <= 6:
        messages.add_message(request,constants.ERROR,'Senha no mínimo 7 digitos.')
        return False
    
    if not password == confirm_password:
        messages.add_message(request,constants.ERROR,'As senhas não coincidem')
        return False
    
    if not re.search('[A-Z]',password):
        messages.add_message(request,constants.ERROR,'Sua senha precisa de uma letra maiuscula')
        return False
    
    if not re.search('[a-z]', password):
        messages.add_message(request,constants.ERROR,'Sua senha precisa de uma letra minúscula.')
        return False
    if not re.search('[1-9]', password):
        messages.add_message(request,constants.ERROR,'Sua senha precisa de um numero')
        return False

    return True





def email_html(path_template: str, assunto: str, para: list, **kwargs) -> dict:
    
    html_content = render_to_string(path_template, kwargs)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(assunto, text_content, settings.EMAIL_HOST_USER, para)

    email.attach_alternative(html_content, "text/html")
    email.send()
    return {'status': 1}