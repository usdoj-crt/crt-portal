. env-helpers.sh foo_app

# Mock "cf", as we don't want to actually interact with cloudfoundry.
function cf() {
  if [[ "$1" == "env" ]] && [[ $# -eq 2 ]]; then
    # Use local env instead of cloudfoundry env.
    # Cloudfoundry env outputs colon separated instead of equals.
    env | sed 's/=/: /'
    return 0
  fi

  if [[ "$1" == "set-env" ]] && [[ "$2" == "foo_app" ]] && [[ $# -eq 4 ]]; then
    name="$3"
    value="$4"
    export "$name=$value"
    return 0
  fi

  echo "cf called with unexpected arguments: $@" >&2
  return 1
}

function test_get_env() {
  export FOO=BAR

  actual="$(cf_get_env FOO)"

  if [[ "$actual" != "BAR" ]]; then
    echo "Failed to get env variable: $actual" >&2
    exit 1
  fi
}
test_get_env

function test_increment_env() {
  cf_increment_env TEST_COUNTER >/dev/null
  actual="$(cf_get_env TEST_COUNTER)"
  if [[ "$actual" -ne 0 ]]; then
    echo "Counter ($actual) should initially be zero" >&2
    exit 1
  fi

  cf_increment_env TEST_COUNTER >/dev/null
  cf_increment_env TEST_COUNTER >/dev/null
  actual="$(cf_get_env TEST_COUNTER)"
  if [[ "$actual" -ne 2 ]]; then
    echo "Counter ($actual) should increment, but didn't" >&2
    exit 1
  fi

  TEST_COUNTER=65535
  cf_increment_env TEST_COUNTER >/dev/null

  actual="$(cf_get_env TEST_COUNTER)"
  if [[ "$actual" -ne 0 ]]; then
    echo "Counter ($actual) should loop around to 1" >&2
    exit 1
  fi
}
test_increment_env


sleeps=0
function sleep() {
  sleeps="$((sleeps + 1))"
  TEST_SERVING="$((TEST_SERVING + 1))"
}

function test_wait_for_lock_when_unlocked() {
  sleeps=0
  cf_wait_for_lock TEST_NEXT TEST_SERVING
  if [[ "$sleeps" -ne 0 ]]; then
    echo "Wait for lock should not sleep when no lock is held" >&2
    exit 1
  fi

}
test_wait_for_lock_when_unlocked

function test_wait_for_lock_when_locked() {
  sleeps=0
  export TEST_NEXT=16
  export TEST_SERVING=4
  cf_wait_for_lock TEST_NEXT TEST_SERVING
  if [[ "$sleeps" -ne 12 ]]; then
    echo "We should have had to wait 12 times, but we waited $sleeps" >&2
    exit 1
  fi
}
test_wait_for_lock_when_locked
