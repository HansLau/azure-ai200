import azure.functions as func
import json
import os
import uuid
import re
import logging
from datetime import datetime, timezone

from classifier import suggest_category

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
MOCK_DB = []

def get_cosmos_container():
    endpoint = os.getenv("COSMOS_DB_URI")
    key = os.getenv("COSMOS_DB_KEY")
    db_name = os.getenv("COSMOS_DB_NAME", "tickets")
    container_name = os.getenv("COSMOS_CONTAINER_NAME", "tickets")

    if not endpoint or not key:
        logging.warning("Cosmos DB URI or Key missing from environment settings.")
        return None

    try:
        from azure.cosmos import CosmosClient
        client = CosmosClient(endpoint, credential=key)
        return client.get_database_client(db_name).get_container_client(container_name)
    except Exception as e:
        logging.error(f"Cosmos connection error: {e}")
        return None


def generate_next_ticket_id(container):
    if not container:
        existing_ids = [t.get("id", "") for t in MOCK_DB if str(t.get("id", "")).startswith("T")]
        nums = []
        for i in existing_ids:
            m = re.match(r"^T(\d+)$", str(i))
            if m:
                nums.append(int(m.group(1)))
        next_num = max(nums, default=0) + 1
        return f"T{next_num:03d}"

    try:
        # Fetch all IDs safely across partitions
        query = "SELECT c.id FROM c"
        results = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        nums = []
        for item in results:
            item_id = item.get("id") if isinstance(item, dict) else item
            match = re.match(r"^T(\d+)$", str(item_id))
            if match:
                nums.append(int(match.group(1)))

        next_num = max(nums, default=0) + 1
        return f"T{next_num:03d}"
    except Exception as e:
        logging.error(f"Error generating sequential ID: {e}")
        # Default safely to incrementing based on item count rather than random hex
        try:
            count_query = "SELECT VALUE COUNT(1) FROM c"
            cnt = list(container.query_items(query=count_query, enable_cross_partition_query=True))[0]
            return f"T{int(cnt) + 1:03d}"
        except Exception:
            return "T074"

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

        if body.get("category"):
            category = body.get("category")
        else:
            cat_result = suggest_category(title, description)
            category = cat_result.get("category", "General Enquiry")

        now_ts = datetime.now(timezone.utc).isoformat()
        container = get_cosmos_container()

        # Generate sequential ID (e.g., T073) if not explicitly provided
        ticket_id = body.get("id") or generate_next_ticket_id(container)

        ticket = {
            "id": ticket_id,
            "name": name,
            "email": email,
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "New",
            "createdAt": now_ts,
            "updatedAt": now_ts
        }

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
                query += " AND c.category = @cat"
                params.append({"name": "@cat", "value": category})
            if status:
                query += " AND c.status = @stat"
                params.append({"name": "@stat", "value": status})
            if email:
                query += " AND c.email = @em"
                params.append({"name": "@em", "value": email})

            # Fetch items and sort safely in Python
            items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
            items = sorted(items, key=lambda x: x.get("createdAt", ""), reverse=True)
        else:
            items = MOCK_DB
            if category:
                items = [t for t in items if t.get("category") == category]
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

        now_ts = datetime.now(timezone.utc).isoformat()
        container = get_cosmos_container()
        if container:
            item = container.read_item(item=ticket_id, partition_key=ticket_id)
            item["status"] = new_status
            item["updatedAt"] = now_ts
            container.replace_item(item=ticket_id, body=item)
            updated = item
        else:
            item = next((t for t in MOCK_DB if t["id"] == ticket_id), None)
            if not item:
                return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404, mimetype="application/json")
            item["status"] = new_status
            item["updatedAt"] = now_ts
            updated = item

        return func.HttpResponse(json.dumps(updated), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")