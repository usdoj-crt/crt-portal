---
title: assigned_to_bulk
subject: "Assigned: {{reports|length}} Reports"
language: en
is_html: true
is_notification: true
---

Hello,

You have been assigned to take a look at {{reports|length}} Reports:

 {% for r in reports %}
     - [Report {{r.id}}](/form/view/{{r.id}})
 {% endfor %}

Please take a look at the links above or, if you think this was in error, please add a comment and reassign the reports as appropriate.

Sincerely,

Portal Team

_please do not reply to this message_