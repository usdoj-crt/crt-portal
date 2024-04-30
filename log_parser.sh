#!/bin/bash
echo -n "{}" > filter_logs.json
declare -a filters=("status" "retention_schedule" "litigation_hold" "contact_phone" "language" "referred" "hate_crime" "servicemember" "intake_format" "location_state" "primary_complaint" "contact_first_name" "contact_last_name" "contact_email" "violation_summary" "location_name" "location_name_1" "location_name_2" "location_city_town" "create_date_start" "create_date_end" "summary" "origination_utm_campaign" "assigned_to" "dj_number" "tags" "public_id" "primary_statute" "district" "reported_reason" "commercial_or_public_place")
jq -r '.[].link' exportedLogRecords.json | while read link ; do
    linkparams=( $(echo ${link} | tr "?" "\n") )
    for j in $(echo ${linkparams[2]} | tr "&" "\n"); do
        for k in $(echo $j | tr "=" "\n"); do
            inarray=$(echo ${filters[@]} | grep -w "${k}" | wc -w)
            if [ "${inarray}" -gt "0" ]; then
                originalval=$(jq -r ."${k}" filter_logs.json)
                newval=$((originalval + 1))
                tmp=$(mktemp)
                jq --arg v $newval '.'${k}' = $v' filter_logs.json > "$tmp" && mv "$tmp" filter_logs.json
            fi
        done
    done
done
