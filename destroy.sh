#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
: "${PROJECT:?}" "${LOCATION:?}"

./reset.sh
gcloud network-security authz-policies delete token-demo-authz --location="$LOCATION" --quiet
gcloud beta service-extensions authz-extensions delete token-demo-iap --location="$LOCATION" --quiet
gcloud network-services agent-gateways delete token-demo-gw --location="$LOCATION" --quiet
gcloud agent-identity auth-providers delete resend --location="$LOCATION" --quiet
gcloud storage rm -r "gs://$PROJECT-token-demo" --quiet
rm -f token_demo/.env
