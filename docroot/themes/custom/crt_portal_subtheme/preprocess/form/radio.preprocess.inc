<?php

/**
 * Implements template_preprocess_radios().
 */

function crt_portal_subtheme_preprocess_input__radio(&$variables) {
  $variables['attributes']['class'][] = 'usa-radio__input';
}
