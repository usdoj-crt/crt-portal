#!/bin/bash

# This script assumes that cf is available and that the caller is already logged in.

CF_APP="$1"

function cf_get_env() {
  local name
  name="$1"
  cf env "$CF_APP" | grep "^$name: " | sed "s/^$name: //"
  return 0
}

# Increments a variable, returning the prior value.
# If the value gets too high, we loop back to zero to avoid overflow.
function cf_increment_env() {
  local current
  local next
  local name

  name="$1"

  current="$(cf_get_env "$name")"
  printf "${current:-0}"
  if ! [[ $current =~ ^[0-9]+$ ]] ; then
    printf "Value '$current' is not a number - setting to zero.\n" 1>&2
    next=0
  elif [ $current -ge 65535 ]; then
    next=0
  else
    next="$((current + 1))"
  fi

  cf set-env "$CF_APP" "$name" "$next" 1>/dev/null
  return $?
}

function cf_wait_for_lock() {
  local ticket
  local serving
  local ticket_var
  local serving_var

  ticket_var="$1"
  serving_var="$2"
  ticket="$(cf_increment_env "$ticket_var")"
  serving="$(cf_get_env "$serving_var")"
  while [ ${ticket:-0} -ne ${serving:-0} ]
  do
    printf "Waiting for lock: I am ticket $ticket, and they are currently serving $serving...\n"
    sleep 30
    serving="$(cf_get_env "$serving_var")"
  done
  printf "Acquired lock with ticket $ticket! Continuing...\n"
  return 0
}
