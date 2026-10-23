#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
: "${PROJECT:?}" "${LOCATION:?}"
API=https://$LOCATION-aiplatform.googleapis.com/v1
TOKEN=$(gcloud auth print-access-token)

if ENGINE=$(curl -s -H "Authorization: Bearer $TOKEN" \
     "$API/projects/$PROJECT/locations/$LOCATION/reasoningEngines?filter=display_name=%22token-demo%22" \
     | python3 -c "import json, sys; print(json.load(sys.stdin)['reasoningEngines'][0]['name'])") \
   && OP=$(curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "$API/$ENGINE?force=true" \
     | python3 -c "import json, sys; print(json.load(sys.stdin)['name'])"); then
  echo "Deleting $ENGINE..."
  until curl -s -H "Authorization: Bearer $TOKEN" "$API/$OP" | grep -q '"done": true'; do sleep 10; done
  echo "Deleted."
fi
