import os

import httpx
from google.adk.agents import Agent
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_tool import AuthConfig
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider, GcpAuthProviderScheme
from google.adk.models import Gemini
from google.adk.tools.authenticated_function_tool import AuthenticatedFunctionTool


async def send_test_email(credential: AuthCredential) -> dict:
    """Sends a test email through Resend and reports the credential the agent received."""
    http = credential.http
    token = http.credentials.token if http.credentials and http.credentials.token else next(iter(http.additional_headers.values()))
    async with httpx.AsyncClient() as client:
        sent = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {token}"},
            json={"from": "onboarding@resend.dev", "to": "delivered@resend.dev", "subject": "token-demo", "text": "Sent by agent."},
            timeout=10,
        )
    return {"agent_sees": token[:7], "length": len(token), "resend_status": sent.status_code}


CredentialManager.register_auth_provider(GcpAuthProvider())

root_agent = Agent(
    name="token_demo",
    model=Gemini(model="gemini-3.5-flash", client_kwargs={"enterprise": True, "location": "global"}),
    instruction="When asked to send a test email, call send_test_email and return its result as-is.",
    tools=[
        AuthenticatedFunctionTool(
            func=send_test_email,
            auth_config=AuthConfig(auth_scheme=GcpAuthProviderScheme(name=os.environ["AUTH_PROVIDER"])),
        )
    ],
)
