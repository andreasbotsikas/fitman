#!/usr/bin/env bash

while true; do
  change=$(inotifywait -e close_write,moved_to,create .)
  change=${change#./ * }
  if [ "$change" = "lalala.txt" ]; then ./scriptToKillProcess.sh; fi
done
echo "123"
