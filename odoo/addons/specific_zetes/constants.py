# Request structure
HEADER_LABELS = (
    "serNum",
    "verNum",
    "appNum",
    "msgType",
    "operId",
    "langId",
    "msgDate",
    "msgTime",
    "packageId",
)
METHOD_INDEX = 3
USER_INDEX = 4

RESPONSE_CODE_OK = 0
RESPONSE_CODE_ERROR = 10
RESPONSE_CODE_NO_LINES = 11

# Actions
ZETES_ACTIONS = [("requ", "Request"), ("resp", "Response"), ("resu", "Action")]

# Domains
ZETES_DOMAINS = [
    ("assignment", "Assignment"),
    ("catchweight", "Catchweight"),
    ("itempick", "Itempick"),
    ("location", "Location"),
    ("print", "Print"),
    ("refdata", "Refdata"),
    ("usercontext", "Usercontext"),
]

# Zetes values for assignment (stock.picking) state
AS_DEFAULT = "00"
AS_START = "01"
AS_ACTIVE = "02"
AS_STAGING = "03"
AS_DONE = "04"
AS_CANCELED = "05"
AS_FINISHED = "08"

# Zetes values for picking (stock.pack.operation) state
OP_DEFAULT = MOVE_DEFAULT = "00"
OP_PICKED = MOVE_DONE = "01"
OP_SHORTPICKED = MOVE_SHORTPICKED = "02"
OP_SKIPPED = MOVE_SKIPPED = "03"
OP_CUT = MOVE_CUT = "04"
OP_CANCELED = MOVE_FULL = "05"
OP_MISSING = "09"

# Print
PRINT_PASSPORT = "03"
PRINT_LABELS = "04"

# Assignment types
PICKING_ASSIGNMENT = "1"
RANGEMENT_ASSIGNMENT = "2"
REASSORT_ASSIGNMENT = "3"

# Move type (load, put, load & put)
MOVE_TYPE_LOAD = "1"
MOVE_TYPE_PUT = "2"
MOVE_TYPE_LOADPUT = "3"  # not used

# Type of load (load or unload)
MOVE_UNLOAD = "1"
MOVE_LOAD = "2"

# Zero Check Limit
ZERO_CHECK_LIMIT = 0

# Printer
PRINTER_MEDICAMENT = "1"
PRINTER_ALIMENT = "2"
PRINTER_FRIGO = "3"
