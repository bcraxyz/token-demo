# token_demo/agent.py
import os

import google.auth
import requests
from google.adk.agents import Agent
from google.auth.transport.requests import Request


def send_test_email() -> dict:
    """Fetches the Resend key from Auth Manager, sends a test email, and reports what the agent held."""
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    resp = requests.post(
        f"https://agentidentitycredentials.googleapis.com/v1/{os.environ['AUTH_PROVIDER']}/credentials:retrieve",
        headers={"Authorization": f"Bearer {creds.token}"},
        json={"user_id": "demo"},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json()["success"]["token"]
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
    model="gemini-2.5-flash",
    instruction="When asked to send a test email, call send_test_email and return its result as-is.",
    tools=[send_test_email],
)
