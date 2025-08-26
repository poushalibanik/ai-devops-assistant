from mcp.server.fastmcp import FastMCP
import os, requests
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("Slack MCP Server")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
CHANNEL = os.getenv("SLACK_CHANNEL", "#general")

@mcp.tool()
def slack_notify(text: str) -> str:
    resp = requests.post("https://slack.com/api/chat.postMessage",
                         headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
                         json={"channel": CHANNEL, "text": text})
    return "Message sent!" if resp.json().get("ok") else f"Error: {resp.text}"

if __name__ == "__main__":
    print("Starting Slack MCP Server...")
    mcp.run(transport="stdio")
