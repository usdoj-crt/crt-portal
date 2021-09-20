from .models import Report


def update_email_count(email):
    if email is not None:
        reports = Report.objects.filter(contact_email__iexact=email)
        email_count = len(reports)
        reports.update(email_count=email_count)
        return email_count
