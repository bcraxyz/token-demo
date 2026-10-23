# setup.sh
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${PROJECT:?}" "${LOCATION:?}" "${RESEND_API_KEY:?}"
AUTH_PROVIDER=projects/$PROJECT/locations/$LOCATION/authProviders/resend
GATEWAY=projects/$PROJECT/locations/$LOCATION/agentGateways/token-demo-gw

gcloud config set project "$PROJECT"
gcloud services enable aiplatform.googleapis.com agentidentity.googleapis.com agentregistry.googleapis.com \
  networkservices.googleapis.com networksecurity.googleapis.com iap.googleapis.com
gcloud storage buckets create "gs://$PROJECT-token-demo" --location="$LOCATION"
pip install -q -r requirements.txt

gcloud agent-identity auth-providers create resend --location="$LOCATION" --api-key="$RESEND_API_KEY" \
  || gcloud agent-identity auth-providers undelete resend --location="$LOCATION"
gcloud agent-identity auth-providers add-iam-policy-binding resend --location="$LOCATION" \
  --role=roles/agentidentity.user --member="user:$(gcloud config get-value account)" --quiet > /dev/null

cat > token_demo/.env <<EOF
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$PROJECT
GOOGLE_CLOUD_LOCATION=$LOCATION
AUTH_PROVIDER=$AUTH_PROVIDER
EOF

gcloud network-services agent-gateways import token-demo-gw --location="$LOCATION" <<EOF
name: token-demo-gw
protocols:
  - MCP
googleManaged:
  governedAccessPath: AGENT_TO_ANYWHERE
registries:
  - //agentregistry.googleapis.com/projects/$PROJECT/locations/global
EOF
gcloud beta service-extensions authz-extensions import token-demo-iap --location="$LOCATION" <<EOF
name: token-demo-iap
service: iap.googleapis.com
failOpen: false
timeout: 1s
metadata:
  iapPolicyVersion: "V2"
  iamEnforcementMode: "DRY_RUN"
EOF
gcloud network-security authz-policies import token-demo-authz --location="$LOCATION" <<EOF
name: token-demo-authz
target:
  resources:
    - $GATEWAY
policyProfile: REQUEST_AUTHZ
action: CUSTOM
customProvider:
  authzExtension:
    resources:
      - projects/$PROJECT/locations/$LOCATION/authzExtensions/token-demo-iap
EOF
