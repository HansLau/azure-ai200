import azure.functions as func
import json
import os
import uuid
from datetime import datetime, timezone
from classifier import classify_ticket

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
MOCK_DB = []  # Standalone fallback when Cosmos DB isn't connected yet

def get_cosmos_container():
    # Read the exact variable names we set up in the Azure Portal settings
    cosmos_uri = os.getenv("COSMOS_DB_URI")
    cosmos_key = os.getenv("COSMOS_DB_KEY")
    
    if not cosmos_uri or not cosmos_key:
        return None
    try:
        from azure.cosmos import CosmosClient
        db_name = os.getenv("COSMOS_DB_NAME", "TicketDB")
        container_name = os.getenv("COSMOS_CONTAINER_NAME", "Tickets")
        
        # Connects using the separate URI and Key fields
        client = CosmosClient(cosmos_uri, credential=cosmos_key)
        return client.get_database_client(db_name).get_container_client(container_name)
    except Exception:
        return None

# 1. Ticket Submission
@app.route(route="tickets", methods=["POST"])
def submit_ticket(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        name = body.get("name")
        email = body.get("email")
        title = body.get("title")
        description = body.get("description", "")
        priority = body.get("priority", "Medium")

        if not name or not email or not title:
            return func.HttpResponse(
                json.dumps({"error": "name, email, and title are required"}),
                status_code=400,
                mimetype="application/json"
            )

        category = body.get("category") or classify_ticket(title, description)
        ticket = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "title": title,
            "description": description,
            "suggestedCategory": category,
            "priority": priority,
            "status": "New",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        container = get_cosmos_container()
        if container:
            container.create_item(body=ticket)
        else:
            MOCK_DB.append(ticket)

        return func.HttpResponse(json.dumps(ticket), status_code=201, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

# 2. Ticket Retrieval & Admin Filter
@app.route(route="tickets", methods=["GET"])
def get_tickets(req: func.HttpRequest) -> func.HttpResponse:
    try:
        category = req.params.get("category")
        status = req.params.get("status")
        email = req.params.get("email")

        container = get_cosmos_container()
        if container:
            query = "SELECT * FROM c WHERE 1=1"
            params = []
            if category:
                query += " AND c.suggestedCategory = @cat"
                params.append({"name": "@cat", "value": category})
            if status:
                query += " AND c.status = @stat"
                params.append({"name": "@stat", "value": status})
            if email:
                query += " AND c.email = @em"
                params.append({"name": "@em", "value": email})
            query += " ORDER BY c.createdAt DESC"
            items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        else:
            items = MOCK_DB
            if category:
                items = [t for t in items if t.get("suggestedCategory") == category]
            if status:
                items = [t for t in items if t.get("status") == status]
            if email:
                items = [t for t in items if t.get("email") == email]
            items = sorted(items, key=lambda x: x.get("createdAt", ""), reverse=True)

        return func.HttpResponse(json.dumps(items), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

# 3. Status Updates
@app.route(route="tickets/{id}", methods=["PATCH"])
def update_ticket_status(req: func.HttpRequest) -> func.HttpResponse:
    try:
        ticket_id = req.route_params.get("id")
        body = req.get_json()
        new_status = body.get("status")

        if not new_status:
            return func.HttpResponse(json.dumps({"error": "status is required"}), status_code=400, mimetype="application/json")

        container = get_cosmos_container()
        if container:
            item = container.read_item(item=ticket_id, partition_key=ticket_id)
            item["status"] = new_status
            container.replace_item(item=ticket_id, body=item)
            updated = item
        else:
            item = next((t for t in MOCK_DB if t["id"] == ticket_id), None)
            if not item:
                return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404, mimetype="application/json")
            item["status"] = new_status
            updated = item

        return func.HttpResponse(json.dumps(updated), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
