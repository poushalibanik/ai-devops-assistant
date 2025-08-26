import os
from kubernetes import client, config
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Kubernetes MCP Server")

# Load Kubernetes config (local ~/.kube/config OR in-cluster)
if os.getenv("KUBERNETES_SERVICE_HOST"):
    config.load_incluster_config()
else:
    config.load_kube_config()

apps_v1 = client.AppsV1Api()

@mcp.tool()
def get_pods(name: str) -> str:
    """
    Get pod status for a deployment.
    """
    core_v1 = client.CoreV1Api()
    pods = core_v1.list_namespaced_pod(namespace="default", label_selector=f"app={name}")
    statuses = [f"{p.metadata.name}: {p.status.phase}" for p in pods.items]
    return "\n".join(statuses) if statuses else f"No pods found for {name}"

@mcp.tool()
def deploy_app(name: str, image: str, replicas: int = 1) -> str:
    """
    Deploy an application to Kubernetes.
    Args:
        name: Name of the deployment
        image: Container image (e.g., nginx:latest)
        replicas: Number of replicas (default = 1)
    """
    try:
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector={"matchLabels": {"app": name}},
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": name}),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(name=name, image=image)]
                    ),
                ),
            ),
        )

        apps_v1.create_namespaced_deployment(namespace="default", body=deployment)
        return f"Deployed '{name}' with {replicas} replicas of {image}"
    except Exception as e:
        return f"Deployment failed: {str(e)}"


@mcp.tool()
def get_status(name: str) -> str:
    """
    Get status of a Kubernetes deployment.
    Args:
        name: Deployment name
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace="default")
        available = deployment.status.available_replicas or 0
        replicas = deployment.spec.replicas
        return f"Deployment '{name}': {available}/{replicas} replicas available"
    except Exception as e:
        return f"Error fetching status for '{name}': {str(e)}"


if __name__ == "__main__":
    print("Starting Kubernetes MCP Server...")
    mcp.run(transport="stdio")
