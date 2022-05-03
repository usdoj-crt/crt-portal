const path = require('path');

module.exports = {
  entry: {
    test: './crt_portal/static/js/components/test.jsx',
    // base: './crt_portal/static/js/base.js',
    // attachments: './crt_portal/static/js/attachments.js',
    // autofill_current_date: './crt_portal/static/js/autofill_current_date.js',
    // banner_language_selection: './crt_portal/static/js/banner_language_selection.js',
    // bulk_actions: './crt_portal/static/js/bulk_actions.js',
    // clear_error_class: './crt_portal/static/js/clear_error_class.js',
    // complaint_actions: './crt_portal/static/js/complaint_actions.js',
    // complaint_quick_view: './crt_portal/static/js/complaint_quick_view.js',
    // complaint_view_filters: './crt_portal/static/js/complaint_view_filters.js',
    // contact_info_confirmation_modal: './crt_portal/static/js/contact_info_confirmation_modal.js',
    // dashboard_quick_view: './crt_portal/static/js/dashboard_quick_view.js',
    // dashboard_view_filters: './crt_portal/static/js/dashboard_view_filters.js',
    // disable_submit_button: './crt_portal/static/js/disable_submit_button.js',
    // dropdown: './crt_portal/static/js/dropdown.js',
    // edit_contact_info: './crt_portal/static/js/edit_contact_info.js',
    // edit_details: './crt_portal/static/js/edit_details.js',
    // focus_alert: './crt_portal/static/js/focus_alert.js',
    // form_letter: './crt_portal/static/js/form_letter.js',
    // highlight_active_header: './crt_portal/static/js/highlight_active_header.js',
    // modal: './crt_portal/static/js/modal.js',
    // other_show_hide: './crt_portal/static/js/other_show_hide.js',
    // primary_complaint: './crt_portal/static/js/primary_complaint.js',
    // print_report: './crt_portal/static/js/print_report.js',
    // pro_form_show_hide: './crt_portal/static/js/pro_form_show_hide.js',
    // progress_bar: './crt_portal/static/js/progress_bar.js',
    // redirect_modal: './crt_portal/static/js/redirect_modal.js',
    // routing_guide: './crt_portal/static/js/routing_guide.js',
    // unsupported_browsers: './crt_portal/static/js/unsupported_browsers.js',
    // url_params_polyfill: './crt_portal/static/js/url_params_polyfill.js',
    // word_count: './crt_portal/static/js/word_count.js'
  },
  output: {
    filename: '[name].min.js',
    path: path.resolve(__dirname, 'crt_portal/static/js')
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules)/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] }
      },
    ]
  },
};
