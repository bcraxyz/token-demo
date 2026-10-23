import argparse
import os
from importlib.metadata import version

import vertexai
from vertexai import types
from vertexai.agent_engines import AdkApp

from token_demo.agent import root_agent

parser = argparse.ArgumentParser()
parser.add_argument("--gateway")
args = parser.parse_args()

project, location = os.environ["PROJECT"], os.environ["LOCATION"]
client = vertexai.Client(project=project, location=location)
config = {
    "display_name": "token-demo",
    "staging_bucket": f"gs://{project}-token-demo",
    "requirements": [
        f"google-cloud-aiplatform[adk,agent_engines]=={version('google-cloud-aiplatform')}",
        f"google-adk=={version('google-adk')}",
        "google-cloud-agentidentitycredentials",
        "cloudpickle",
        "pydantic",
        "requests",
    ],
    "extra_packages": ["token_demo"],
    "env_vars": {"AUTH_PROVIDER": f"projects/{project}/locations/{location}/authProviders/resend"},
}
if args.gateway:
    config["agent_gateway_config"] = {"agent_to_anywhere_config": {"agent_gateway": args.gateway}}
    config["env_vars"]["GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES"] = "false"
    config["env_vars"]["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

existing = list(client.agent_engines.list(config={"filter": 'display_name="token-demo"'}))
if existing:
    engine = client.agent_engines.update(name=existing[0].api_resource.name, agent=AdkApp(agent=root_agent), config=config)
else:
    config["identity_type"] = types.IdentityType.AGENT_IDENTITY
    engine = client.agent_engines.create(agent=AdkApp(agent=root_agent), config=config)
print(engine.api_resource.spec.effective_identity)
