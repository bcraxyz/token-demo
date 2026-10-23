# deploy.py
import argparse
import os

import vertexai
from vertexai import types
from vertexai.agent_engines import AdkApp
from importlib.metadata import version

from token_demo.agent import root_agent

parser = argparse.ArgumentParser()
parser.add_argument("--gateway")
args = parser.parse_args()

client = vertexai.Client(project=os.environ["PROJECT"], location=os.environ["LOCATION"])
config = {
    "display_name": "token-demo",
    "staging_bucket": os.environ["STAGING_BUCKET"],
    "requirements": [
        f"google-cloud-aiplatform[agent_engines,adk]=={version('google-cloud-aiplatform')}",
        f"google-adk=={version('google-adk')}",
        "cloudpickle",
        "pydantic",
        "requests",
    ],
    "extra_packages": ["token_demo"],
    "env_vars": {"AUTH_PROVIDER": os.environ["AUTH_PROVIDER"]},
}
if args.gateway:
    config["agent_gateway_config"] = {"agent_to_anywhere_config": {"agent_gateway": args.gateway}}

existing = list(client.agent_engines.list(config={"filter": 'display_name="token-demo"'}))
if existing:
    engine = client.agent_engines.update(name=existing[0].api_resource.name, agent=AdkApp(agent=root_agent), config=config)
else:
    config["identity_type"] = types.IdentityType.AGENT_IDENTITY
    engine = client.agent_engines.create(agent=AdkApp(agent=root_agent), config=config)
print(engine.api_resource.spec.effective_identity)
