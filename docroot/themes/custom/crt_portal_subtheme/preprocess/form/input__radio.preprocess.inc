<?php

/**
 * @file
 * Alterations for radio buttons.
 */

function crt_portal_subtheme_preprocess_input__radio(&$variables) {
  $variables['attributes']['class'][] = 'usa-radio__input';
}
