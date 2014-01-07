#!/usr/bin/env bash

PIDFILE="/tmp/twitterTest2.pid"

if [ -e "${PIDFILE}" ] && (ps -u $USER -f | grep "[ ]$(cat ${PIDFILE})[ ]"); then
  echo "Already running."
  exit 99
fi

python /home/user/Downloads/testFile/cronTest_v2.py  > /tmp/cronTesttwitter2.log &

echo $! > "${PIDFILE}"
chmod 644 "${PIDFILE}"
