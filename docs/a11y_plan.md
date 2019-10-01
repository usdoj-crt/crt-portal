# Accessibility testing plan

Our [accessibility testing plan](https://docs.google.com/document/d/15ondXXQytfmSNAgboZP-CajXLVbQvFBRhPDnawEPiZU/edit#) is stored in Google Docs; please see the linked plan for the latest.

Below is a copy of the plan as of October 1, 2019 for ease of reference within GitHub when testing front-end features!

## When we test accessibility

**Each Story**:  We aim to test the accessibility of each Story that we develop. Developers should aim to complete as much testing as feasible before they push to the development site. Other teammates (design, product) can help out by completing additional tests using the dev site.

**Biweekly Review**:  We have bi-weekly review sessions scheduled for every other Thursday with Terri Youngblood, Section 508 Subject Matter Expert for the Department of Justice. This will be a chance for us to do more in-depth review and use Terri’s expertise to improve our work.

## How we'll test accessibility

We currently have pa11y configured to test proposed code changes for accessibility. Note that pa11y is currently configured to check the first page of the form only; a future improvement will extend pa11y checks to all pages.

For each Story, we will manually test the corresponding page in these ways:

1. Test the site by zooming the page to 200%.
  + This is an important and easy-to-do check that shows how the site will appear for someone with low vision who zooms in. More from the Bureau of Internet Accessibility.
2. View website on mobile phone.
  + Check text size and navigation.
3. Test the page in black-and-white (find contrast) + color inverse (find issues).
  + This is another important and easy-to perform check. It shows how users with low or no color contrast vision will experience the site. If a tester knows how to update CSS styles manually in the browser, they can see how the site would look in black-and-white by adding this CSS to the `<html>` tag:

  ```
      -moz-filter: grayscale(100%);
      -webkit-filter: grayscale(100%);
      filter: gray; /* IE6-9 */
      filter: grayscale(100%);
  ```
  + Chrome extensions like Accessibility Insights can also help you see pages in grayscale.
  + Chrome’s built-in inspector includes a tool for checking contrast ratios. This is a quick way to make sure text has the right contrast against a background of the right size.
  + Other tools: WCAG 2.0 Contrast checker, ANDI.

4. Test that the page is accessible via the keyboard; check images, forms, and multimedia for accessibility.
  + All new features developed should be accessible via the keyboard only, without using the mouse. The Accessibility Insights Chrome Extension tool provides guidance and thorough checklists to assist with manual keyboard accessibility testing.
  + Use the 18F Accessibility Checklist to help you check: https://accessibility.18f.gov/checklist/

5. Test using VoiceOver (or another screen reader).

  + Testing with a screen reader is an important step and one that will require some training. VoiceOver comes with a built-in tutorial: you can start the tutorial by opening VoiceOver and pressing fn+ctrl+opt+cmd+f8 on a Mac.
    + Recommended to use Safari with VoiceOver
  + Do keyboard shortcuts work in a table to navigate
  + All fields have explicit labels

## Collaborating with the Accessibility Guild

Additionally, the 18F Accessibility Guild is developing a Manual User Testing Guide — this could be a source of training and expertise for our project. We hope to collaborate with them and pull in their expertise as needed.