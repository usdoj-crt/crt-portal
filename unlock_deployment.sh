#!/bin/bash

circleci_url='https://app.circleci.com/pipelines/github/usdoj-crt/crt-portal?branch=develop'

read -r -d '' usage <<EOF
Unlocks CircleCI when deployments are stuck because of a failed deployment.

Once unlocked, deployments will need to be restarted by merging a new branch into develop or by re-running the stalled build-and-test from CircleCI at:

$circleci_url

Make sure to log in (by running 'cf login --sso') prior to running this script

Note: This script will change the current 'cf target' to dev.

Usage:

  $0

EOF

if [ "$#" -gt 0 ]; then
  echo "$usage"
  exit 1
fi

echo "Making sure we're in dev: "
echo ""
cf target -o 'doj-crtportal' -s 'dev'
if [ $? -ne 0 ]; then
  echo 'Failed to change cf target to dev.'
  echo ''
  echo "Please make sure you're logged in to cloud.gov"
  exit 1
fi

. env-helpers.sh crt-portal-django

next="$(cf_get_env CCI_NEXT_TICKET)"
serving="$(cf_get_env CCI_SERVING_TICKET)"

# If next or serving are unset, we're in a bad state.
if [ -z "$next" ] || [ -z "$serving" ]; then
  echo 'One or both of the deployment variables are unset.'
  echo ''
  echo "Please make sure you're logged in to cloud.gov"
  exit 1
fi

cat <<EOF

================================================================================
⚠️ WARNING:

This will skip any pending deployments. They will need to be cancelled and re-run.

If you're not sure that you want to do this, please exit now.

The current serving ticket is: $serving
The current pending ticket is: $next

This will set the serving ticket to: $next
================================================================================

EOF

read -p 'Reset the deployment variables [y/N]? '
if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
  echo 'Okay - canceled!'
  exit 1
fi

cf set-env crt-portal-django CCI_SERVING_TICKET "$next" 1>/dev/null
if [ $? -ne 0 ]; then
  echo 'Failed to set CCI_SERVING_TICKET.'
  exit 1
fi

new_next="$(cf_get_env CCI_NEXT_TICKET)"
new_serving="$(cf_get_env CCI_SERVING_TICKET)"
cat <<EOF

================================================================================
🔓 Unlocked!

The new serving ticket is: $new_serving
The new pending ticket is: $new_next

You may now retry the failed / locked deployment. To do this, find the stalled workflow in Circle CI and choose "Rerun" -> "Rerun workflow from start"

$circleci_url
================================================================================

EOF

