# This is a helper script for updating turnstile settings on Cloudflare.
#
# Many of these settings (e.g., "mode", can be set in the Cloudflare dashboard,
# but some settings (e.g., "offlabel") cannot.
#
# Follows the format at:
# https://developers.cloudflare.com/api/operations/accounts-turnstile-widget-update
#
# Set the following environment variables:
# - TURNSTILE_ACCOUNTID
#  - This can be found on https://dash.cloudflare.com/
# - TURNSTILE_TOKEN
#   - Create a token at https://dash.cloudflare.com/profile/api-tokens
#   - The token should have the 'Account.Turnstile:Edit' permission
# - TURNSTILE_SITEKEY
#   - This can be found by running the "Configuration before" command below.
#   - (You'll need your TURNSTILE_ACCOUNTID and TURNSTILE_TOKEN set to run this command)

TURNSTILE_ACCOUNTID='DO NOT COMMIT THIS'
TURNSTILE_TOKEN='DO NOT COMMIT THIS'
TURNSTILE_SITEKEY='DO NOT COMMIT THIS'

echo "Verifying token:"
curl -s --request GET \
  --url "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  --header "Authorization: Bearer $TURNSTILE_TOKEN" \
  --header 'Content-Type: application/json' \
  | jq

echo "Configuration before:"
curl -s --request GET \
  --url "https://api.cloudflare.com/client/v4/accounts/$TURNSTILE_ACCOUNTID/challenges/widgets" \
  --header "Authorization: Bearer $TURNSTILE_TOKEN" \
  --header 'Content-Type: application/json' \
  | jq

echo "Updating..."
curl --request PUT \
  --url "https://api.cloudflare.com/client/v4/accounts/$TURNSTILE_ACCOUNTID/challenges/widgets/$TURNSTILE_SITEKEY" \
  --header "Authorization: Bearer $TURNSTILE_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
  "mode": "invisible",
  "domains": [],
  "name": "STAGING Civil Rights Reporting Portal",
  "bot_fight_mode": false,
  "offlabel": true,
  "clearance_level": "no_clearance"
}'

echo "Configuration after:"
curl -s --request GET \
  --url "https://api.cloudflare.com/client/v4/accounts/$TURNSTILE_ACCOUNTID/challenges/widgets" \
  --header "Authorization: Bearer $TURNSTILE_TOKEN" \
  --header 'Content-Type: application/json' \
  | jq

