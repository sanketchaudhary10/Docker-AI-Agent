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
    try:
        initialize_k8s()  
        logging.info("Kubernetes configuration initialized successfully.")
        yield  
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
        intents, keywords, deployment_name = parse_query(request.query)
        logging.info(f"Parsed intents: {intents}, keywords: {keywords}, deployment name: {deployment_name}")

        if "node" in request.query.lower() and "pod" in request.query.lower():
            pods = get_pods_with_nodes()
            answer = ", ".join([f"'{pod['name']}' belongs to node '{pod['node']}'" for pod in pods])

        elif "restarts" in request.query.lower() and "pod" in request.query.lower():
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
            pods = get_pods_in_namespace()
            pod_statuses = [f"{pod['name']} is {pod['status']}" for pod in pods]
            answer = f"Status: {', '.join(pod_statuses)}"

        elif intents["deployments"] and intents["pods"]:
            
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

