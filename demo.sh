# demo.sh
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${PROJECT:?}" "${LOCATION:?}" "${RESEND_API_KEY:?}"
export STAGING_BUCKET=gs://$PROJECT-token-demo
export AUTH_PROVIDER=projects/$PROJECT/locations/$LOCATION/authProviders/resend
GATEWAY=projects/$PROJECT/locations/$LOCATION/agentGateways/token-demo-gw

echo "Real key:        ${RESEND_API_KEY:0:7}"

IDENTITY=$(python3 deploy.py)
gcloud agent-identity auth-providers add-iam-policy-binding resend --location="$LOCATION" \
  --role=roles/agentidentity.user --member="principal://$IDENTITY" --quiet > /dev/null
sleep 60
echo "Without gateway: $(python3 invoke.py)"

read -rp "Press Enter to attach Agent Gateway..."
python3 deploy.py --gateway "$GATEWAY" > /dev/null
echo "With gateway:    $(python3 invoke.py)"
