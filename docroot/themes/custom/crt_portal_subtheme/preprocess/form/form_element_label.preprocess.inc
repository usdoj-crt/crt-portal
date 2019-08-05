<?php

/**
 * @file
 * Alterations for form labels.
 */

function crt_portal_subtheme_preprocess_form_element_label(&$variables) {
  $variables['attributes']['class'][] = 'usa-radio__label';
}
