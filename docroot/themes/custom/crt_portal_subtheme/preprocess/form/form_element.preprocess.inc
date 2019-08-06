<?php

/**
 * Implements hook_preprocess_form_element().
 */

function crt_portal_subtheme_preprocess_form_element(&$variables) {

  // Some inputs require a wrapping USWDS class, they are applied below.
  switch ($variables['type']) {

    case 'radio':
      // These work and apply the correct classes!
      $variables['attributes']['class'][] = 'usa-radio';
      $variables['label']['#attributes']['class'][] = 'usa-radio__label';

      // However, we still need to apply a `usa-radio__input` class to the input itself.
      // Looked at the docs but couldn't find a clear reference/example for this:
      //   + https://api.drupal.org/api/drupal/core%21includes%21form.inc/function/template_preprocess_form_element/8.2.x
      //   + https://api.drupal.org/api/drupal/core%21modules%21system%21templates%21form-element.html.twig/8.2.x

      // Tried all of the following, no luck so far:
      // $variables['input']['#attributes']['class'][] = 'usa-radio__input';
      // $variables['element']['#attributes']['class'][] = 'usa-radio__input';
      // $variables['element']['input']['#attributes']['class'][] = 'usa-radio__input';
      break;

    case 'checkbox':
      // These work and apply the correct classes!
      $variables['attributes']['class'][] = 'usa-checkbox';
      $variables['label']['#attributes']['class'][] = 'usa-checkbox__label';

      // However, we still need to apply a `usa-checkbox__input` class to the input itself.
      // Same as above.
      break;
  }

  // USWDS suggests the description should appear before the input.
  $variables['description_display'] = 'before';
}
