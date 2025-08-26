import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Jenkins MCP Server")

JENKINS_URL = os.getenv("JENKINS_URL", "http://hurlza01.hursley.ibm.com:9090")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")

def _crumb():
    # Some Jenkins setups require a crumb for CSRF protection
    r = requests.get(f"{JENKINS_URL}/crumbIssuer/api/json", auth=(JENKINS_USER, JENKINS_TOKEN))
    if r.status_code == 200:
        j = r.json()
        return {j["crumbRequestField"]: j["crumb"]}
    return {}

@mcp.tool()
def trigger_jenkins_job(job_name: str, params: dict = None) -> str:
    """
    Trigger a Jenkins job (freestyle or pipeline). Pass parameters for parameterized jobs.
    """
    params = params or {}
    # # Prefer buildWithParameters; Jenkins will allow plain build if no params are defined.
    # url = f"{JENKINS_URL}/job/{job_name}/buildWithParameters"
    url = f"{JENKINS_URL}/job/{job_name}/build"
    headers = _crumb()
    resp = requests.post(url, auth=(JENKINS_USER, JENKINS_TOKEN), params=params, headers=headers)
    if resp.status_code in (201, 200):
        # Jenkins returns a queue location in the Location header
        q = resp.headers.get("Location", "")
        return f"Triggered job '{job_name}'. Queue: {q or 'unknown'}"
    return f"Failed to trigger job '{job_name}': {resp.status_code} {resp.text}"

if __name__ == "__main__":
    print("Starting Jenkins MCP Server...")
    mcp.run(transport="stdio")

#will add functions to check status of job, delete job etc later