<?php

/**
 * Implements template_preprocess_checkboxes().
 */

function crt_portal_subtheme_preprocess_checkboxes(&$variables) {
  $variables['attributes']['class'][] = 'usa-checkbox__input';
}
