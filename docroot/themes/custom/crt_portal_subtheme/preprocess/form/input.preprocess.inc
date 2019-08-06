<?php

/**
 * Implements hook_preprocess_form_element().
 */

function crt_portal_subtheme_preprocess_input(&$variables) {

  switch ($variables['element']['#type']) {

    case 'date':
      $class = 'usa-input';
      $variables['attributes']['class'][] = 'usa-input--inline';
      break;

    case 'checkbox':
      $class = 'usa-checkbox__input';
      $variables['title_attributes']['class'][] = 'usa-checkbox__label';
      break;

    case 'radio':
      $class = 'usa-radio__input';
      $variables['title_attributes']['class'][] = 'usa-radio__label';
      break;

    case 'button':
      // Base theme does not yet apply this class to non-Submit buttons.
      $class = 'usa-button';
      break;

    default:
      // If no matches above, we blanket add this class to all inputs.
      $class = 'usa-input';
      break;
  }

  $variables['attributes']['class'][] = $class;

  if (isset($variables['element']['#errors']) && !empty($variables['element']['#errors'])) {
    $variables['attributes']['class'][] = 'usa-input--error';
  }

}
