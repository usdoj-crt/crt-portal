"""The blue-green deploy plug-in that works with build packs is deprecated,
So this script reproduces the steps in a shell script. From: https://github.com/concourse/cf-resource/issues/62
"""
# expects blue-green-deploy.sh USERNAME PASSWORD SPACE
APP_NAME=crt-portal-django;
CRT_USERNAME=$1
CRT_PASSWORD=$2
SPACE=$3


# login to the right place
cf auth $CRT_USERNAME $CRT_PASSWORD;
cf target -o doj-crtportal-prototyping -s $SPACE;


# Deploy a new app called crt-portal-django-venerable, if that builds correctly, delete the old app and rename crt-portal-django-venerable to crt-portal-django
app_state() {
  cf app "$1" | grep 'requested state:' | tr -s ' ' | cut -f3 -d' ' || echo 'missing';
}

VEN_NAME="${APP_NAME}-venerable";
APP_STATE="$(app_state "$APP_NAME")";
MADE_VEN='false';

if [[ "$APP_STATE" != 'missing' ]]; then
  if [[ "$APP_STATE" != 'started' ]]; then
    cf delete "$APP_NAME" -f;
  else
    VEN_STATE="$(app_state "$VEN_NAME")";
    if [[ "$VEN_STATE" != 'missing' ]]; then
      cf delete "$VEN_NAME" -f;
    fi;
    cf rename "$APP_NAME" "$VEN_NAME";
    MADE_VEN='true';
  fi;
fi;

if cf push "$APP_NAME" ; then
  if [[ "$MADE_VEN" == 'true' ]]; then
    cf delete "$VEN_NAME" -f;
  fi;
  echo 'SUCCESS!';
else
  if [[ "$MADE_VEN" == 'true' ]]; then
    cf logs "$APP_NAME" --recent;
    cf delete "$APP_NAME" -f;
    cf rename "$VEN_NAME" "$APP_NAME";
  fi;
  echo 'FAILED :(';
  exit 1
fi;