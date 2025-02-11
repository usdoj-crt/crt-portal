from django import template
from django.utils.safestring import mark_safe

from ..models import ApplicationContact

register = template.Library()


@register.simple_tag
def application_contact_markup():
    contacts = [
        f'<a href="mailto:{contact.email}">{contact.name} ({contact.email})</a>'
        for contact in ApplicationContact.objects.all()
    ]

    if len(contacts) >= 3:
        return mark_safe("{}, or {}".format(", ".join(contacts[:-1]), contacts[-1]))  # nosec

    if len(contacts) == 2:
        return mark_safe(" or ".join(contacts))  # nosec

    if len(contacts) == 1:
        return mark_safe(contacts[0])  # nosec

    return mark_safe("your application's administrator")  # nosec


@register.simple_tag
def application_contact_email_list():
    contacts = "</br>".join([
        f'<a href="mailto:{contact.email}">{contact.name}</a>'
        for contact in ApplicationContact.objects.all()
    ])

    if len(contacts) > 0:
        return mark_safe(contacts)
    return mark_safe("your application's administrator")  # nosec


@register.simple_tag
def application_contact_mailto_string():
    mailto = ",".join([
        f'{contact.email}'
        for contact in ApplicationContact.objects.all()
    ])

    return mark_safe(mailto)  # nosec
