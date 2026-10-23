import argparse
import os
from importlib.metadata import version

import agentplatform
from agentplatform import types
from agentplatform.frameworks import AdkApp

from token_demo.agent import root_agent

parser = argparse.ArgumentParser()
parser.add_argument("--gateway")
args = parser.parse_args()

project, location = os.environ["PROJECT"], os.environ["LOCATION"]
client = agentplatform.Client(project=project, location=location)
config = {
    "display_name": "token-demo",
    "staging_bucket": f"gs://{project}-token-demo",
    "requirements": [
        f"google-cloud-agentplatform[adk,agent_engines]=={version('google-cloud-agentplatform')}",
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

existing = list(client.runtimes.list(config={"filter": 'display_name="token-demo"'}))
if existing:
    runtime = client.runtimes.update(name=existing[0].api_resource.name, agent=AdkApp(agent=root_agent), config=config)
else:
    config["identity_type"] = types.IdentityType.AGENT_IDENTITY
    runtime = client.runtimes.create(agent=AdkApp(agent=root_agent), config=config)
print(runtime.api_resource.spec.effective_identity)
