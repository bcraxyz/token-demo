import json
import os

import agentplatform

client = agentplatform.Client(project=os.environ["PROJECT"], location=os.environ["LOCATION"])
name = next(client.runtimes.list(config={"filter": 'display_name="token-demo"'})).api_resource.name

for event in client.runtimes.get(name=name).stream_query(user_id="demo", message="Send a test email."):
    for part in event.get("content", {}).get("parts", []):
        if "function_response" in part:
            print(json.dumps(part["function_response"]["response"]))
    if "error_message" in event:
        print(event.get("error_code"), event["error_message"])
