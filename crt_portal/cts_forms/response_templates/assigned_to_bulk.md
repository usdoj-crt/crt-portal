---
title: assigned_to_bulk
subject: "Assigned: {{reports|length}} Reports"
language: en
is_html: true
is_notification: true
---

Hello,

You have been assigned {{reports|length}} reports in the CRT Reporting Portal, which takes in reports from the public at civilrights.justice.gov:

 {% for r in reports %}
     - [Report {{r.id}}](/form/view/{{r.id}})
 {% endfor %}

After reviewing the links above, you can:

1. Respond to the public through the Portal User Interface

2. Change the status of the reports (close the reports)

3. Assign the reports to another user and more

If you need training on how to process these reports, please reach out to [Bill.Laughman@usdoj.gov](mailto:bill.laughman@usdoj.gov).

Sincerely,

Portal Team

_please do not reply to this message_
