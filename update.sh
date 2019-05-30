#!/bin/bash
# Routine to connect to cron
# triggers update script on remote server

echo "loading environment variables"
set -a
. .env
set +a
echo "querying database"
curl -X PUT "https://rfr.herokuapp.com/$RFR_APP_UPDATE_URI"
