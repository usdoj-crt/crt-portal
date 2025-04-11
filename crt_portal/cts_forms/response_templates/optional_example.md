---
title: EXAMPLE - Optional Sections
subject: "DEMO: Your Civil Rights Division Report - {{ record_locator }} from the {{ section_name }} Section"
language: en
is_html: true
show_in_dropdown: false
---

{{ addressee }},

You contacted the Department of Justice on {{date_of_intake}}. After careful review of what you submitted, we have decided not to take any further action on your complaint.

[%optional group="Big Headers" name="What we did"]

# What we did:

Team members from the Civil Rights Division reviewed the information you submitted. Based on our review, we have decided not to take any further action on your complaint. We receive several thousand reports of civil rights violations each year. We unfortunately do not have the resources to take direct action for every report.

Your report number was {{record_locator}}.
[%endoptional]

[%optional group="Big Headers" name="What you can do"]

# What you can do:

We are not determining that your report lacks merit. Your issue may still be actionable by others - your state bar association or local legal aid office may be able to help.
[%endoptional]

## To find a local office:

[%optional group="Finding help" name="Texas Bar"]
Texas Bar Association
[https://www.texasbar.com/](https://www.texasbar.com/)
(512) 427-1463
[%endoptional]

[%optional group="Finding help" name="Legal Services"]
Legal Services Corporation (or Legal Aid Offices)
[https://www.lsc.gov/find-legal-aid](https://www.lsc.gov/find-legal-aid)
[%endoptional]

[%optional group="Big Headers" name="How you have helped"]

# How you have helped:

While we don’t have the capacity to take on each individual report, your report can help us find issues affecting multiple people or communities. It also helps us understand emerging trends and topics.

Thank you for taking the time to contact the Department of Justice about your concerns. We regret we are not able to provide more help on this matter.
[%endoptional]

[% optional group="Signature" name="Signature" ]
Sincerely,

U.S. Department of Justice
Civil Rights Division
[% endoptional ]
