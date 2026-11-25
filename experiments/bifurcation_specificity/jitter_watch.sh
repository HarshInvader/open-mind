#!/bin/sh
# Independent watcher in its own session: logs when the chain or python pid disappears (catches SIGKILL, which cannot be trapped).
cd "$(dirname "$0")"
sleep 5
C=$1; P=$(cat jitter_run.pid)
echo "WATCH start $(date -u +%FT%TZ) chain $C py $P watcher $$" >> jitter_watch.log
while :; do
  kill -0 "$C" 2>/dev/null || { echo "WATCH chain $C gone $(date -u +%FT%TZ)" >> jitter_watch.log; break; }
  kill -0 "$P" 2>/dev/null || { echo "WATCH py $P gone $(date -u +%FT%TZ)" >> jitter_watch.log; }
  sleep 20
done
