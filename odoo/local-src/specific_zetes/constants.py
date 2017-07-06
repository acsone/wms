# Request structure
HEADER_LABELS = ('serNum', 'verNum', 'appNum', 'msgType', 'operId', 'langId',
                 'msgDate', 'msgTime', 'packageId')
METHOD_INDEX = 3
USER_INDEX = 4

RESPONSE_CODE_OK = 0
RESPONSE_CODE_ERROR = 10

# Actions
ZETES_ACTIONS = [('requ', 'Request'),
                 ('resp', 'Response'),
                 ('resu', 'Action')]

# Domains
ZETES_DOMAINS = [('assignment', 'Assignment'),
                 ('catchweight', 'Catchweight'),
                 ('itempick', 'Itempick'),
                 ('location', 'Location'),
                 ('print', 'Print'),
                 ('refdata', 'Refdata'),
                 ('usercontext', 'Usercontext'),
                 ]

# Zetes values for assignment (stock.picking) state
AS_DEFAULT = '00'
AS_START = '01'
AS_ACTIVE = '02'
AS_STAGING = '03'
AS_DONE = '04'
AS_CANCELED = '05'
AS_FINISHED = '08'

# Zetes values for picking (stock.pack.operation) state
OP_DEFAULT = '00'
OP_PICKED = '01'
OP_SHORTPICKED = '02'
OP_SKIPPED = '03'
OP_CUT = '04'
OP_CANCELED = '05'

# Print
PRINT_PASSPORT = '03'
PRINT_LABELS = '04'
