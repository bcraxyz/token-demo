import os

import requests
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.cloud.agentidentitycredentials_v1 import AuthProviderCredentialsServiceClient


def send_test_email() -> dict:
    """Fetches the Resend key from Auth Manager, sends a test email, and reports what the agent held."""
    token = AuthProviderCredentialsServiceClient(transport="rest").retrieve_credentials(
        auth_provider=os.environ["AUTH_PROVIDER"], user_id="demo"
    ).success.token
    sent = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {token}"},
        json={"from": "onboarding@resend.dev", "to": "delivered@resend.dev", "subject": "token-demo", "text": "Sent by agent."},
        timeout=10,
    )
    return {
        "agent_sees": token[:12] if token.startswith("goog-") else token[:7],
        "length": len(token),
        "resend_status": sent.status_code,
    }


root_agent = Agent(
    name="token_demo",
    model=Gemini(model="gemini-3.5-flash", client_kwargs={"enterprise": True, "location": "global"}),
    instruction="When asked to send a test email, call send_test_email and return its result as-is.",
    tools=[send_test_email],
)
