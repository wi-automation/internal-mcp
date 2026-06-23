from literals import DatabaseInstance
from literals.operation import Operation

PERMITTED_TABLE_OPERATIONS: dict[DatabaseInstance, dict[str, set[Operation]]] = {
    "gestionale": {
        "userCustomer": {"select"},
    },
}
