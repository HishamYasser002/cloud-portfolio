"""Visitor counter logic, kept separate from Azure Functions so it can be unit tested."""
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
)
from azure.data.tables import UpdateMode

PARTITION = "site"
ROW = "counter"
MAX_RETRIES = 5


def increment(table) -> int:
    """Add 1 to the stored count and return the new value.

    Uses optimistic concurrency (ETags): if two visitors arrive at the same
    moment, one update is rejected and retried instead of a visit being lost.
    """
    for _ in range(MAX_RETRIES):
        try:
            entity = table.get_entity(PARTITION, ROW)
        except ResourceNotFoundError:
            try:
                table.create_entity({"PartitionKey": PARTITION, "RowKey": ROW, "count": 1})
                return 1
            except ResourceExistsError:
                continue  # someone else created it first, so read it again

        entity["count"] = int(entity["count"]) + 1
        try:
            table.update_entity(
                entity,
                mode=UpdateMode.REPLACE,
                etag=entity.metadata["etag"],
                match_condition=MatchConditions.IfNotModified,
            )
            return entity["count"]
        except ResourceModifiedError:
            continue  # changed since we read it, so try again

    raise RuntimeError("Could not update the counter after several retries")
