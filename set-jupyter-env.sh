# Run this locally to set jupyter environment variables on Cloud Foundry.

if ! command -v jq &> /dev/null; then
  echo 'Please install jq to continue (https://github.com/jqlang/jq)'
  exit 1
fi

function run_on_cf() {
  local command="$1"
  cf ssh crt-portal-django -t -c "\
    export LD_LIBRARY_PATH="$HOME/deps/1/lib:$HOME/deps/0/lib" && \
    export PATH="$PATH:$HOME/deps/1/python/bin/" && \
    cd /home/vcap/app/ && \
    exec $command \
  "
}

function check_cf_target() {
  echo "Double checking the current cf target:"
  echo ""
  cf target
  if [ $? -ne 0 ]; then
    echo 'Failed to check cf target'
    echo ''
    echo "Please make sure you're logged in to cloud.gov"
    exit 1
  fi
  read -p 'Given the above target, do you want to continue?'
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo 'Okay - canceled! Run cf target -s dev to target dev.'
    exit 1
  fi
}

function setup_oauth() {
  read -p 'Configure OAuth [y/N]? '
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo 'Okay - skipping OAuth setup'
    return
  fi
  run_on_cf 'python /code/crt_portal/manage.py create_jupyter_oauth --cf-set-env --redirect_uris "https://crt-portal-jupyter-dev.app.cloud.gov/hub/oauth_callback"'
}

function setup_database() {
  local username
  local password

  read -p 'Configure database username and password?'
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo 'Okay - skipping database configuration'
    return
  fi

  printf 'Enter a suitably random VCAP-like username (< 100 characters, lowercase letters and numbers):'
  read_secret username
  printf 'Enter a suitably random VCAP-like password (< 100 characters, lowercase letters and numbers):'
  read_secret password

  cf set-env crt-portal-jupyter DATABASE_USER "$username"
  cf set-env crt-portal-jupyter DATABASE_PASSWORD "$password"
}

read_secret() {
    stty -echo
    trap 'stty echo' EXIT
    read "$@"
    stty echo
    trap - EXIT
    echo
}

check_cf_target
setup_oauth
setup_database
