# Template Writing Help

This page explains what's available when writing custom response templates.

The link to this page is [/api/preview-response](/api/preview-response).

Here's what's on this page:

[TOC]

## Variables

### What's available?

All of our templates support a few special variables. They are:

| Name                          | Example                                            | Description                                                                                 |
|-------------------------------|----------------------------------------------------|---------------------------------------------------------------------------------------------|
| `addressee`                   | Dear John Doe                                      | The salutation "Dear FirstName LastName" (sans comma)                                       |
| `contact_address_line_1`      | 1 Demo Street                                      | The recipient's first address line                                                          |
| `contact_address_line_2`      | Apt 5                                              | The recipient's second address line                                                         |
| `contact_city`                | Springfield                                        | The recipient's city                                                                        |
| `contact_state`               | Ohio                                               | The recipient's state                                                                       |
| `contact_zip`                 | 12345                                              | The recipient's zipcode                                                                     |
| `complainant_name`            | John Doe                                           | The complainant's first and last name                                                       |
| `contact_email`               | john@civilrights.justice.gov                       | The recipient's email address                                                               |
| `contact_phone`               | 555-555-5555                                       | The recipient's phone number                                                                |
| `date_of_intake`              | February 29, 1988                                  | The day the report was submitted                                                            |
| `eeoc_office_name`            | Atlanta District Office                            | The name of the EEOC Office associated with the report                                      |
| `eeoc_office_url`             | https://www.eeoc.gov/field-office/atlanta/location | The link to the contact information for the EEOC Office that is associated with the report  |
| `eeoc_charge_number`          | 555-5555-55555                                     | The EEOC charge number associated with this report                                          |
| `mediation_number`            | 2TX3000                                            | The mediation number associated with this report, if applicable                             |
| `organization_name`           | Santa's Workshop                                   | The name of the organization or location that is subject to the complaint                   |
| `organization_phone`          | 555-555-5555                                       | The organization or location that is subject to the complaint's phone number                |
| `organization_address_line_1` | 123 Icy Dr                                         | The organization or location that is subject to the complaint's first address line          |
| `organization_address_line_2` | Apt 1225                                           | The organization or location that is subject to the complaint's second address line         |
| `organization_city`           | Seattle                                            | The organization or location that is subject to the complaint's city                        |
| `organization_state`          | Washington                                         | The organization or location that is subject to the complaint's state                       |
| `organization_zip`            | 54321                                              | The organization or location that is subject to the complaint's zipcode                     |
| `outgoing_date`               | February 31, 1988                                  | The day this reply is being sent (today)                                                    |
| `record_locator`              | 12345-XYZ                                          | The identifier (record locator) of the report                                               |
| `referral_text`               | Ministry of Magic                                  | The referral_variable set on the ReferralContact                                            |
| `section_name`                | Voting                                             | The section of the user sending the reply                                                   |

### How do I use them?

%%verbatim_start
To use a variable, you need to surround it with `{{ }}`.

For instance, considering the above examples, to show:

```
Dear John Doe who lives at 1 Demo Street
```

you'd write:

```
{{ addressee }} who lives at {{ contact_address_line_1 }}
```

%%verbatim_end

### How do I know they're working?

In the template preview, we don't have any real recipient info, so we just show its name, but underlined.

If you don't see the following (for example, if you see `{ addressee }` instead of {{addressee}}) then the variable isn't working!

| Name                     | Shows As                     |
| ------------------------ | ---------------------------- |
| `addressee`              | {{ addressee }}              |
| `contact_address_line_1` | {{ contact_address_line_1 }} |
| `contact_address_line_2` | {{ contact_address_line_2 }} |
| `contact_email`          | {{ contact_email }}          |
| `date_of_intake`         | {{ date_of_intake }}         |
| `outgoing_date`          | {{ outgoing_date }}          |
| `record_locator`         | {{ record_locator }}         |
| `section_name`           | {{ section_name }}           |
| `referral_text`          | {{ referral_text }}          |

### What about translation/localization?

Some variables have translated/localized forms. To use them, add the lanugage code to the start of the variable name, separated with a period. For example:

| Name                     | Shows As                     |
| ------------------------ | ---------------------------- |
| `es.addressee`           | {{ es.addressee }}           |
| `ko.addressee`           | {{ ko.addressee }}           |
| `tl.addressee`           | {{ tl.addressee }}           |
| `vi.section_name`        | {{ vi.section_name }}        |
| `zh_hans.date_of_intake` | {{ zh_hans.date_of_intake }} |
| `zh_hant.outgoing_date`  | {{ zh_hant.outgoing_date }}  |

## Markdown (Text Formatting)

### What is it?

Our response templates are stored in a file format called Markdown. Markdown is a popular way to use plain text to express lists, headings, etc. You've probably seen it before to some extent in chat applications, Github, etc.

As a quick example of what markdown looks like, here is how you'd write a list in markdown:

```
- Fruit
    - Apples
    - Bananas
- Vegetables
    - Tomato*
    - Potato*

_*Dependent on economic or taxonomic policy_
```

Which will show as:

- Fruit
    - Apples
    - Bananas
- Vegetables
    - Tomato\*
    - Potato\*

_\*Dependent on economic or taxonomic policy_

### Something's not working...

Some common situations where things might not work as expected:

---

#### Not leaving blank lines

Between paragraphs, or between different fancy formatting, leave a blank line.

```
Lists, for instance, won't work if they're directly on the next line after text:
- See?
- Not working.

You need to leave some space:

- That's
- Better.
```

Becomes:

Lists, for instance, won't work if they're directly on the next line after text:
- See?
- Not working.

You need to leave some space:

- That's
- Better.

---

#### Not indenting by four spaces

With this markdown, you have to use four spaces to indent:

```
- This is a list
  - This is not quite a sublist yet

versus:

- This is another list
    - And this is a correct sublist!
```

which becomes:

- This is a list
  - This is not quite a sublist yet

versus:

- This is another list
    - And this is a correct sublist!

---

### What can I do with it?

This page is rendered using our email markdown and styles - so what you see here is what you get!

Here's all of the markdown things we support:

#### Line Breaks

This is going to look confusing with the rest of the page, but:

```
---
```

which becomes:

---

#### Links

```
[this is a link](http://www.google.com)
```

which becomes:

[this is a link](http://www.google.com)

---

#### Text Styles

```
_This is italicized_
__This is bold__
```

which becomes

_This is italicized_
**This is bold**

---

#### Lists

```
- Unordered
    - Sublist
    - Here
- List
- Here

And for ordered:

1. Ordered
    1. Sublist
    1. Here
1. List
1. Here
```

Which shows as (make sure to use four spaces to indent):

- Unordered
  - Sublist
  - Here
- List
- Here

And for ordered:

1. Ordered
   1. Sublist
   1. Here
1. List
1. Here

---

#### Tables

```
| Header     | Header     | Header     |
| ---------- | ---------- | ---------- |
| Cell Value | Cell Value | Cell Value |
| Cell Value | Cell Value | Cell Value |
| Cell Value | Cell Value | Cell Value |
```

which becomes:

| Header     | Header     | Header     |
| ---------- | ---------- | ---------- |
| Cell Value | Cell Value | Cell Value |
| Cell Value | Cell Value | Cell Value |
| Cell Value | Cell Value | Cell Value |

---

#### Block Quotes

```
> I wrote a haiku
> It is in this block quote now
> Wow block quotes are great
```

which becomes:

> I wrote a haiku
> It is in this block quote now
> Wow block quotes are great

---

#### Admonitions

Admonitions are boxes with some text in them. We don't have styles for them now, but the HTML will be produced all the same:

```
!!! note
    Make sure to indent these by four spaces

!!! danger
    Oh no danger!
```

which becomes:

!!! note
    Make sure to indent these by four spaces

!!! danger
    Oh no danger!

The following types are standard, but we can invent our own:

- attention
- caution
- danger
- error
- hint
- important
- note
- tip
- warning

---

#### Optional sections

Optional sections are a custom extension for working with response templates that have paragraphs that might or might not be included in the final response. They look like this:

```
This content is not optional

[%optional group="The checkbox group" name="The individual checkbox name"]

This content is optional

[%endoptional]

More not optional content
```

which becomes:

This content is not optional

[%optional group="The checkbox group" name="The individual checkbox name"]

This content is optional

[%endoptional]

More not optional content

Note that the dropdown is just for previewing that this works - in the Contact Complaianant page, these will be checkboxes. Unchecking the boxes will hide the section completely.

#### Footnotes

```
Footnotes[^1], which have a label[^@#$%] and some content:

[^1]: This is a footnote content.
[^@#$%]: A footnote on the label: "@#$%".
```

which becomes:

Footnotes[^1], which have a label[^@#$%] and some content:

(These will show up at the bottom of the page, after all of the rest of the content)

[^1]: This is a footnote content.
[^@#$%]: A footnote on the label: "@#$%".

---

#### Headers

```
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6
```

Which show as:

# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6

---

And that's it (well, except the footnotes)!