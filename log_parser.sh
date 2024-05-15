#!/bin/bash
echo -n "{}" > filter_logs.json
declare -a filters=(\
  "assigned_to"\
  "commercial_or_public_place"\
  "contact_email"\
  "contact_first_name"\
  "contact_last_name"\
  "contact_phone"\
  "create_date_end"\
  "create_date_start"\
  "district"\
  "dj_number"\
  "hate_crime"\
  "intake_format"\
  "language"\
  "litigation_hold"\
  "location_city_town"\
  "location_name"\
  "location_name_1"\
  "location_name_2"\
  "location_state"\
  "origination_utm_campaign"\
  "primary_complaint"\
  "primary_statute"\
  "public_id"\
  "referred"\
  "reported_reason"\
  "retention_schedule"\
  "servicemember"\
  "status"\
  "summary"\
  "tags"\
  "violation_summary"\
)
jq -r '.[] | .message' exportedLogRecords.json | while read link ; do
    linkparams=( $(echo ${link} | tr "?" "\n") )
    for param in $(echo ${linkparams[8]} | tr "&" "\n"); do
        echo "$param"
        for filter in $(echo $param | tr "=" "\n"); do
            inarray=$(echo ${filters[@]} | grep -w "${filter}" | wc -w)
            if [ "${inarray}" -gt "0" ]; then
                originalval="$(jq -r ."${filter}" filter_logs.json)"
                newval="$((originalval + 1))"
                tmp="$(mktemp)"
                jq --arg v $newval '.'${filter}' = $v' filter_logs.json > "$tmp" && mv "$tmp" filter_logs.json
            fi
        done
    done
done
