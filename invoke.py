# invoke.py
import json
import os

import vertexai

client = vertexai.Client(project=os.environ["PROJECT"], location=os.environ["LOCATION"])
name = next(client.agent_engines.list(config={"filter": 'display_name="token-demo"'})).api_resource.name

for event in client.agent_engines.get(name=name).stream_query(user_id="demo", message="Send a test email."):
    for part in event.get("content", {}).get("parts", []):
        if "function_response" in part:
            print(json.dumps(part["function_response"]["response"]))
