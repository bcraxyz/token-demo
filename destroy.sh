# destroy.sh
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
  until curl -s -H "Authorization: Bearer $TOKEN" "$API/$OP" | grep -q '"done": true'; do sleep 10; done
fi

gcloud network-security authz-policies delete token-demo-authz --location="$LOCATION" --quiet
gcloud beta service-extensions authz-extensions delete token-demo-iap --location="$LOCATION" --quiet
gcloud network-services agent-gateways delete token-demo-gw --location="$LOCATION" --quiet
gcloud agent-identity auth-providers delete resend --location="$LOCATION" --quiet
gcloud storage rm -r "gs://$PROJECT-token-demo" --quiet
rm -f token_demo/.env
