<?php

/**
 * Implements hook_preprocess_form_element().
 */

function crt_portal_subtheme_preprocess_form_element(&$variables) {

  // Some inputs require a wrapping USWDS class, they are applied below.
  switch ($variables['type']) {

    case 'radio':
      $variables['attributes']['class'][] = 'usa-radio';
      $variables['label']['#attributes']['class'][] = 'usa-radio__label';
      break;

    case 'checkbox':
      $variables['attributes']['class'][] = 'usa-checkbox';
      $variables['label']['#attributes']['class'][] = 'usa-checkbox__label';
      break;
  }

  // USWDS suggests the description should appear before the input.
  $variables['description_display'] = 'before';
}
