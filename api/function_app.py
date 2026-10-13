import json
import logging
import os

import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

from counter import increment

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# e.g. https://sthishamportfolio.table.core.windows.net
TABLE_ACCOUNT_URL = os.environ["TABLE_ACCOUNT_URL"]
TABLE_NAME = os.environ.get("TABLE_NAME", "visits")

_table = None


def get_table():
    """Connect once and reuse the connection between requests.

    No connection string or key: DefaultAzureCredential uses your `az login`
    on your laptop and the function's managed identity in Azure.
    """
    global _table
    if _table is None:
        service = TableServiceClient(endpoint=TABLE_ACCOUNT_URL, credential=DefaultAzureCredential())
        _table = service.create_table_if_not_exists(TABLE_NAME)
    return _table


@app.route(route="visits", methods=["GET", "POST"])
def visits(req: func.HttpRequest) -> func.HttpResponse:
    try:
        count = increment(get_table())
    except Exception:
        logging.exception("Visitor counter failed")
        return func.HttpResponse(
            json.dumps({"error": "counter unavailable"}),
            status_code=500,
            mimetype="application/json",
        )
    return func.HttpResponse(json.dumps({"count": count}), mimetype="application/json")
