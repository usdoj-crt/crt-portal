---
title: assigned_to
subject: "Assigned: Report {{record_locator}}"
language: en
is_html: true
is_notification: true
---

{% load application_contact %}

Hello,

You have been assigned [Report {{record_locator}}](/form/view/{{report.id}}) in the CRT Reporting Portal, which takes in reports from the public at [civilrights.justice.gov](https://civilrights.justice.gov)

After reviewing the link above, you can:

1. Respond to the public through the Portal User Interface
2. Change the status of the report (close the report)
3. Assign it to another user and more

If you need training on how to process this report, please reach out to {% application_contact_markup %}.
