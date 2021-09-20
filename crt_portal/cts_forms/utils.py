from .models import Report


def update_email_count(email):
    print('update_email_count')
    print('email => ', email)
    if email is not None:
        reports = Report.objects.filter(contact_email__iexact=email)
        print("report.email => ", [report.contact_email for report in reports])
        email_count = len(reports)
        print("email_count => ", email_count)
        reports.update(email_count=email_count)
        return email_count
