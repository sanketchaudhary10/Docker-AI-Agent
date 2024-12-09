# from fastapi import FastAPI, HTTPException
# from models import QueryRequest, QueryResponse
# from kube_utils import initialize_k8s, get_pods_in_namespace
# from nlp_utils import parse_query
# import logging

# # Initialize FastAPI app and logging
# app = FastAPI()
# logging.basicConfig(filename="agent.log", level=logging.INFO)

# @app.on_event("startup")
# def setup():
#     """Initialize Kubernetes configuration on startup."""
#     try:
#         initialize_k8s()
#         logging.info("Kubernetes configuration initialized successfully.")
#     except Exception as e:
#         logging.error(f"Failed to initialize Kubernetes configuration: {e}")
#         raise RuntimeError("Failed to initialize Kubernetes configuration.")

# @app.post("/query", response_model=QueryResponse)
# def handle_query(request: QueryRequest):
#     """
#     Handle incoming queries and provide responses.

#     Payload format:
#     {
#         "query": "How many pods are in the default namespace?"
#     }

#     Response format:
#     {
#         "query": "How many pods are in the default namespace?",
#         "answer": "There are 3 pods in the default namespace."
#     }
#     """
#     logging.info(f"Received query: {request.query}")

#     try:
#         # Parse the query to determine intent
#         intents, keywords = parse_query(request.query)
#         logging.info(f"Parsed intents: {intents}, keywords: {keywords}")

#         # Respond based on intents
#         if intents["pods"] and intents["namespace"]:
#             pods = get_pods_in_namespace()
#             answer = f"There are {len(pods)} pods in the default namespace."
#         elif intents["deployments"]:
#             # Example logic for deployments
#             answer = "Currently deployed applications are xyz."
#         elif intents["logs"]:
#             # Example logic for logs
#             answer = "Here are the logs for the requested resource."
#         else:
#             # Default fallback response
#             answer = "I'm sorry, I couldn't understand your query. Please try rephrasing."

#         logging.info(f"Response: {answer}")
#         return QueryResponse(query=request.query, answer=answer)

#     except Exception as e:
#         logging.error(f"Error processing query: {e}")
#         raise HTTPException(status_code=500, detail="An error occurred while processing the query.")



# from fastapi import FastAPI, HTTPException
# from contextlib import asynccontextmanager
# from kubernetes import client, config
# from models import QueryRequest, QueryResponse
# from nlp_utils import parse_query
# import logging
# from kube_utils import get_pods_in_namespace, get_pods_by_deployment, trim_identifier

# # Initialize FastAPI app and logging
# logging.basicConfig(filename="agent.log", level=logging.INFO)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Lifespan event handler for the app."""
#     try:
#         config.load_kube_config()  # Initialize Kubernetes config
#         logging.info("Kubernetes configuration initialized successfully.")
#         yield  # This allows the app to start up
#     except Exception as e:
#         logging.error(f"Failed to initialize Kubernetes configuration: {e}")
#         raise RuntimeError("Failed to initialize Kubernetes configuration.")
#     finally:
#         logging.info("Application shutdown complete.")

# app = FastAPI(lifespan=lifespan)

# #Kubernetes utility functions
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


# @app.post("/query", response_model=QueryResponse)
# def handle_query(request: QueryRequest):
#     logging.info(f"Received query: {request.query}")

#     try:
#         # Parse the query
#         intents, keywords = parse_query(request.query)
#         logging.info(f"Parsed intents: {intents}, keywords: {keywords}")

#         if intents["deployments"] and intents["pods"]:
#             deployment_name = next((kw for kw in keywords if "deployment" in kw.lower()), None)
#             logging.info(f"Identified deployment name: {deployment_name}")

#             if deployment_name:
#                 pods = get_pods_by_deployment(deployment_name)
#                 if pods:
#                     answer = trim_identifier(deployment_name)
#                 else:
#                     answer = "No pods found for the specified deployment."
#             else:
#                 answer = "No deployment name found in the query."

#         elif intents["pods"] and intents.get("status", False):
#             # Handle pod status queries
#             pods = get_pods_in_namespace()
#             logging.info(f"Pods in namespace: {pods}")

#             pod_name = next((kw for kw in keywords if kw in [pod["name"] for pod in pods]), None)
#             if pod_name:
#                 answer = trim_identifier(pod_name)
#             else:
#                 answer = "Pod specified in the query was not found in the default namespace."

#         elif intents["pods"]:
#             # Handle general pod-related queries
#             pods = get_pods_in_namespace()
#             logging.info(f"Pods in namespace: {pods}")
#             answer = f"There are {len(pods)} pods in the default namespace."
#         elif intents["logs"]:
#             answer = "Fetching logs for the specified resource..."
#         else:
#             answer = "I'm sorry, I couldn't understand your query. Please try rephrasing."

#         logging.info(f"Response: {answer}")
#         return QueryResponse(query=request.query, answer=answer)

#     except Exception as e:
#         logging.error(f"Error processing query: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail="An error occurred while processing the query.")


from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from kube_utils import (
    initialize_k8s,
    get_pods_in_namespace,
    get_pods_with_nodes,
    get_pod_restarts,
    get_pods_by_deployment,
    trim_identifier,
)
from models import QueryRequest, QueryResponse
from nlp_utils import parse_query
import logging

# Initialize FastAPI app and logging
logging.basicConfig(filename="agent.log", level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the app."""
    try:
        initialize_k8s()  # Initialize Kubernetes config
        logging.info("Kubernetes configuration initialized successfully.")
        yield  # This allows the app to start up
    except Exception as e:
        logging.error(f"Failed to initialize Kubernetes configuration: {e}")
        raise RuntimeError("Failed to initialize Kubernetes configuration.")
    finally:
        logging.info("Application shutdown complete.")

app = FastAPI(lifespan=lifespan)

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    logging.info(f"Received query: {request.query}")

    try:
        # Parse the query
        intents, keywords, deployment_name = parse_query(request.query)
        logging.info(f"Parsed intents: {intents}, keywords: {keywords}, deployment name: {deployment_name}")

        if "node" in request.query.lower() and "pod" in request.query.lower():
            # Query for pods and their nodes
            pods = get_pods_with_nodes()
            answer = ", ".join([f"'{pod['name']}' belongs to node '{pod['node']}'" for pod in pods])

        elif "restarts" in request.query.lower() and "pod" in request.query.lower():
            # Query for pod restart count
            pod_name = next((kw for kw in keywords if kw), None)
            if pod_name:
                restarts = get_pod_restarts(pod_name)
                if restarts is not None:
                    answer = f"The pod '{pod_name}' has restarted {restarts} times."
                else:
                    answer = f"No restarts information found for pod '{pod_name}'."
            else:
                answer = "Pod specified in the query was not found."

        elif "status" in request.query.lower() and "all pods" in request.query.lower():
            # Query for status of all pods
            pods = get_pods_in_namespace()
            pod_statuses = [f"{pod['name']} is {pod['status']}" for pod in pods]
            answer = f"Status: {', '.join(pod_statuses)}"

        elif intents["deployments"] and intents["pods"]:
            # Query for pods spawned by a deployment
            if deployment_name:
                pods = get_pods_by_deployment(deployment_name)
                if pods:
                    pod_names = ", ".join([trim_identifier(pod["name"]) for pod in pods])
                    answer = f"{pod_names}"
                else:
                    answer = f"No pods found for the deployment '{deployment_name}'."
            else:
                answer = "No deployment name found in the query."

        elif intents["pods"] and intents.get("status", False):
            # Query for pod status
            pods = get_pods_in_namespace()
            pod_name = next((kw for kw in keywords if kw in [pod["name"] for pod in pods]), None)
            if pod_name:
                answer = f"'{pod_name}' is 'Running'."
            else:
                answer = "Pod specified in the query was not found in the default namespace."

        else:
            answer = "I'm sorry, I couldn't understand your query. Please try rephrasing."

        logging.info(f"Response: {answer}")
        return QueryResponse(query=request.query, answer=answer)

    except Exception as e:
        logging.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the query.")

