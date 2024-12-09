# from kubernetes import client, config
# import os

# def initialize_k8s():
#     """Load Kubernetes configuration from the default kubeconfig file."""
#     kubeconfig_path = os.path.join(os.environ["USERPROFILE"], ".kube", "config")
#     if not os.path.exists(kubeconfig_path):
#         raise FileNotFoundError(f"Kubeconfig file not found at {kubeconfig_path}")
#     config.load_kube_config(config_file=kubeconfig_path)

# def get_pods_in_namespace(namespace="default"):
#     """Fetch the list of pods in the specified namespace."""
#     v1 = client.CoreV1Api()
#     pods = v1.list_namespaced_pod(namespace)
#     return [pod.metadata.name for pod in pods.items]



# from kubernetes import client, config
# import os

# def initialize_k8s():
#     """Load Kubernetes configuration from the default kubeconfig file."""
#     kubeconfig_path = os.path.join(os.environ["USERPROFILE"], ".kube", "config")
#     if not os.path.exists(kubeconfig_path):
#         raise FileNotFoundError(f"Kubeconfig file not found at {kubeconfig_path}")
#     config.load_kube_config(config_file=kubeconfig_path)

# def get_pods_in_namespace(namespace="default"):
#     """
#     Fetch the list of pods in the specified namespace along with details.
#     Returns:
#         List of dicts with pod details: name, status, restart count.
#     """
#     v1 = client.CoreV1Api()
#     pods = v1.list_namespaced_pod(namespace)
#     return [
#         {
#             "name": pod.metadata.name,
#             "status": pod.status.phase,
#             "restarts": sum(container.restart_count for container in pod.status.container_statuses or [])
#         }
#         for pod in pods.items
#     ]

# from kubernetes import client, config
# import os

# def initialize_k8s():
#     """Load Kubernetes configuration from the default kubeconfig file."""
#     kubeconfig_path = os.path.join(os.environ["USERPROFILE"], ".kube", "config")
#     if not os.path.exists(kubeconfig_path):
#         raise FileNotFoundError(f"Kubeconfig file not found at {kubeconfig_path}")
#     config.load_kube_config(config_file=kubeconfig_path)

# def get_pods_in_namespace(namespace="default"):
#     """
#     Fetch the list of pods in the specified namespace along with details.
#     Returns:
#         List of dicts with pod details: name, status, restart count.
#     """
#     v1 = client.CoreV1Api()
#     pods = v1.list_namespaced_pod(namespace)
#     return [
#         {
#             "name": pod.metadata.name,
#             "status": pod.status.phase,
#             "restarts": sum(container.restart_count for container in pod.status.container_statuses or []),
#         }
#         for pod in pods.items
#     ]

# def get_pods_by_deployment(deployment_name, namespace="default"):
#     """
#     Get pods spawned by a specific deployment in a namespace.
#     Args:
#         deployment_name (str): The name of the deployment.
#         namespace (str): The namespace of the deployment.
#     Returns:
#         List of dicts containing pod details: name and status.
#     """
#     v1 = client.CoreV1Api()
#     apps_v1 = client.AppsV1Api()

#     try:
#         # Get the Deployment
#         deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
#         selector = deployment.spec.selector.match_labels  # Labels used by the deployment

#         # Convert labels to a Kubernetes-compatible label selector
#         label_selector = ",".join([f"{key}={value}" for key, value in selector.items()])

#         # Get Pods matching the label selector
#         pods = v1.list_namespaced_pod(namespace, label_selector=label_selector)
#         return [
#             {"name": trim_identifier(pod.metadata.name), "status": pod.status.phase}
#             for pod in pods.items
#         ]
#     except client.exceptions.ApiException as e:
#         if e.status == 404:
#             return []  # Deployment not found
#         raise RuntimeError(f"Error fetching pods for deployment '{deployment_name}': {e}")

# def trim_identifier(name):
#     return "-".join(name.split("-")[:-2]) if "-" in name else name


# from kubernetes import client, config
# import os

# def initialize_k8s():
#     """Load Kubernetes configuration from the default kubeconfig file."""
#     kubeconfig_path = os.path.join(os.environ["USERPROFILE"], ".kube", "config")
#     if not os.path.exists(kubeconfig_path):
#         raise FileNotFoundError(f"Kubeconfig file not found at {kubeconfig_path}")
#     config.load_kube_config(config_file=kubeconfig_path)

# def get_pods_in_namespace(namespace="default"):
#     """Fetch all pods in a given namespace."""
#     v1 = client.CoreV1Api()
#     pod_list = v1.list_namespaced_pod(namespace=namespace)
#     return [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pod_list.items]

# def get_pods_by_deployment(deployment_name, namespace="default"):
#     """Fetch pods associated with a deployment."""
#     v1 = client.CoreV1Api()
#     pod_list = v1.list_namespaced_pod(namespace)
    
#     # Filter pods based on owner references
#     pods = []
#     for pod in pod_list.items:
#         for owner in pod.metadata.owner_references or []:
#             if owner.kind == "ReplicaSet" and deployment_name in owner.name:
#                 pods.append({"name": pod.metadata.name, "status": pod.status.phase})
#     return pods
# def get_pods_by_deployment(deployment_name, namespace="default"):
#     """Fetch pods associated with a deployment."""
#     v1 = client.CoreV1Api()
#     pod_list = v1.list_namespaced_pod(namespace)

#     # Filter pods based on owner references
#     pods = []
#     for pod in pod_list.items:
#         for owner in pod.metadata.owner_references or []:
#             # Match ReplicaSet names containing the deployment name
#             if owner.kind == "ReplicaSet" and deployment_name in owner.name:
#                 pods.append({"name": pod.metadata.name, "status": pod.status.phase})
#     return pods


# def trim_identifier(name):
#     """
#     Trim unique suffixes from Kubernetes resource names.
#     Args:
#         name (str): The full name of the resource (e.g., 'sample-python-deployment-56c598c8fc').
#     Returns:
#         str: The trimmed name (e.g., 'sample-python-deployment').
#     """
#     return "-".join(name.split("-")[:-2]) if "-" in name else name


from kubernetes import client, config
import os
import logging

def initialize_k8s():
    """
    Load Kubernetes configuration from the default kubeconfig file.
    """
    kubeconfig_path = os.path.join(os.environ["USERPROFILE"], ".kube", "config")
    if not os.path.exists(kubeconfig_path):
        raise FileNotFoundError(f"Kubeconfig file not found at {kubeconfig_path}")
    config.load_kube_config(config_file=kubeconfig_path)

def get_pods_in_namespace(namespace="default"):
    """
    Fetch the list of pods in the specified namespace along with details.
    Returns:
        List[dict]: Pod details, including name, status, and restart count.
    """
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)
    return [
        {
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "restarts": sum(container.restart_count for container in pod.status.container_statuses or []),
        }
        for pod in pod_list.items
    ]

def get_pods_with_nodes(namespace="default"):
    """
    Fetch all pods in a given namespace and their associated nodes.
    Returns:
        List[dict]: Pod details, including name, status, and node.
    """
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)
    return [
        {
            "name": pod.metadata.name,
            "node": pod.spec.node_name,
            "status": pod.status.phase,
        }
        for pod in pod_list.items
    ]

def get_pod_restarts(pod_name, namespace="default"):
    """
    Get the restart count for a specific pod.
    Args:
        pod_name (str): Name of the pod.
        namespace (str): Namespace of the pod.
    Returns:
        int: Number of restarts.
    """
    logging.info(f"Fetching restart count for pod: {pod_name} in namespace: {namespace}")
    pods = get_pods_in_namespace(namespace)
    for pod in pods:
        if pod["name"] == pod_name:
            logging.info(f"'{pod_name}' restarts: {pod['restarts']}")
            return pod["restarts"]
    logging.warning(f"Pod '{pod_name}' not found in namespace '{namespace}'.")
    return None

def get_pods_by_deployment(deployment_name, namespace="default"):
    """
    Get pods spawned by a specific deployment in a namespace.
    Args:
        deployment_name (str): The name of the deployment.
        namespace (str): The namespace of the deployment.
    Returns:
        List[dict]: Pod details, including name and status.
    """
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    try:
        deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
        selector = deployment.spec.selector.match_labels
        label_selector = ",".join([f"{key}={value}" for key, value in selector.items()])
        logging.info(f"Label selector for deployment '{deployment_name}': {label_selector}")

        pod_list = v1.list_namespaced_pod(namespace, label_selector=label_selector)
        pods = [
            {"name": pod.metadata.name, "status": pod.status.phase}
            for pod in pod_list.items
        ]
        logging.info(f"Pods found for deployment '{deployment_name}': {[pod['name'] for pod in pods]}")
        return pods
    except client.exceptions.ApiException as e:
        if e.status == 404:
            logging.warning(f"Deployment '{deployment_name}' not found in namespace '{namespace}'.")
            return []  # Deployment not found
        raise RuntimeError(f"Error fetching pods for deployment '{deployment_name}': {e}")

def trim_identifier(name):
    """
    Trim unique suffixes from Kubernetes resource names.
    Args:
        name (str): The full name of the resource (e.g., 'sample-python-deployment-56c598c8fc').
    Returns:
        str: The trimmed name (e.g., 'sample-python-deployment').
    """
    return "-".join(name.split("-")[:-2]) if "-" in name else name

