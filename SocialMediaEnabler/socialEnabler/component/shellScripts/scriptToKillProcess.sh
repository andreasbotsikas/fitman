#!/usr/bin/env bash

PIDFILE="/tmp/twitterTest2.pid"

if [ -e "${PIDFILE}" ] && (ps -u $USER -f | grep "[ ]$(cat ${PIDFILE})[ ]"); then
  echo "Already running."
  value=`cat $PIDFILE`

  kill $value
  echo $value
  exit 99
fi

echo "not running"
