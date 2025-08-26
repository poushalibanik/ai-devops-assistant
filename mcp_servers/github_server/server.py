from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os, requests

load_dotenv()
mcp = FastMCP("GitHub MCP Server")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@mcp.tool()
def create_issue(repo: str, title: str, body: str) -> str:
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = requests.post(url, json={"title": title, "body": body}, headers=headers)
    return f"Issue created: {resp.json().get('html_url', resp.text)}"


@mcp.tool()
def create_pr(repo: str, title: str, head: str, base: str = "main", body: str = "") -> str:
    """
    Create a GitHub Pull Request.
    repo format: owner/repo
    head: branch containing changes (e.g. 'feature-branch')
    base: branch you want to merge into (default: 'main')
    """
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"title": title, "head": head, "base": base, "body": body}
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code == 201:
        return f"Pull Request created: {resp.json().get('html_url')}"
    else:
        return f"Failed to create PR: {resp.status_code} {resp.text}"

if __name__ == "__main__":
    print("Starting GitHub MCP Server...")  
    mcp.run(transport="stdio")
