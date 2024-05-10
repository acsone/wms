/* eslint no-use-before-define: 0 */  // --> OFF

var DEMO_SINGLE_PUTAWAY_1 = {
    'fetch' : {
        "data": {
            "id": 1,
            "name": "A nice pack 1",
            "location_src": {
                "id": 1,
                "name":  'Location SRC 1',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location SRC 2',
            },
            "product": [{"id": 1, "name": 'Product 1', "qty": 5}, {"id": 2, "name": 'Product 2', "qty": 2}],
            "picking": {"id": 1, "name": 'Picking 1'},
        },
        "state": "scan_location",
        "message": undefined
    },
    'validate' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {
            'body': 'Pack validated',
            'message_type': 'info',
        }
    },
    'cancel' : {
        "data": {
            "id": 1,
            "location_src": {
                "id": 1,
                "name":  'Location SRC 1 cancel',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location DST 1 cancel',
            },
            "product": {"id": 1, "name": 'Product 1'},
            "picking": {"id": 1, "name": 'Picking 1'},
        },
        "state": "scan_location",
        "message": undefined
    }
}

var DEMO_SINGLE_PUTAWAY_2 = {
    'fetch' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {"message_type": "error", "body": "You cannot do that!"}
    },
}
var DEMO_SINGLE_PUTAWAY_3 = {
    'fetch' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {"message_type": "error", "body": "No pkg found"}
    },
}
var DEMO_SINGLE_PUTAWAY_4 = {
    'fetch' : {
        "data": {
            "id": 1,
            "name": "A nice pack 4",
            "location_src": {
                "id": 1,
                "name":  'Location SRC 4',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location DST 4',
            },
            "product": {"id": 1, "name": 'Product 4'},
            "picking": {"id": 1, "name": 'Picking 4'},
        },
        "state": "takeover",
        "message": {"message_type": "info", "body": "Benoit is at the toilette: do you take over?"}
    },
    'validate' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {
            'body': 'Pack validated',
            'message_type': 'info',
        }
    },
}
var DEMO_SINGLE_PUTAWAY_5 = {
    'fetch' : {
        "data": {
            "id": 1,
            "name": "A nice pack 5",
            "location_src": {
                "id": 1,
                "name":  'Location SRC 5',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location DST 5',
            },
            "product": {"id": 1, "name": 'Product 5'},
            "picking": {"id": 1, "name": 'Picking 5'},
        },
        "state": "scan_location",
        "message": undefined
    },
    'cancel' : {
        "data": undefined,
        "state": "scan_pack",
        "message": undefined,
    },
    'validate' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {
            'body': 'Pack validated',
            'message_type': 'info',
        }
    },
}
var DEMO_SINGLE_PUTAWAY_6 = {
    'fetch' : {
        "data": {
            "id": 1,
            "name": "A nice pack 6",
            "location_src": {
                "id": 1,
                "name":  'Location SRC 6',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location DST 6',
            },
            "product": {"id": 1, "name": 'Product 6'},
            "picking": {"id": 1, "name": 'Picking 6'},
        },
        "state": "scan_location",
        "message": undefined
    },
    'validate' : {
        "data": undefined,
        "state": "confirm_location",
        "message": {"message_type": "warning", "body": "Are you sure of this location?"}
    },
    'LOC6' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {
            'body': 'Pack validated',
            'message_type': 'info',
        }
    },
}
var DEMO_SINGLE_PUTAWAY_7 = {
    'fetch' : {
        "data": {
            "id": 1,
            "name": "A nice pack 7",
            "location_src": {
                "id": 1,
                "name":  'Location SRC 7',
            },
            "location_dst": {
                "id": 2,
                "name": 'Location DST 7',
            },
            "product": {"id": 1, "name": 'Product 7'},
            "picking": {"id": 1, "name": 'Picking 7'},
        },
        "state": "scan_location",
        "message": undefined
    },
    'validate' : {
        "data": undefined,
        "state": "scan_location",
        "message": {"message_type": "error", "body": "You cannot move to this location"}
    },
    'LOC7' : {
        "data": undefined,
        "state": "scan_pack",
        "message": {
            'body': 'Pack validated',
            'message_type': 'info',
        }
    },
}

var DEMO_SCAN_ANYTHING_PACK = {
    'fetch' : {
        "data": {
            "type": "pack",
            "id": 192834,
            "name": "PA92834",
            "location_src": {
                "id": 1923,
                "name":  'B1S08A34',
            },
            "location_dst": {
                "id": 224,
                "name": 'B1S00A01',
            },
            "product": [{"id": 1, "name": 'Ski Thermo Sock', "qty": 36, "lot": "19102403"}, {"id": 123, "name": 'Hiking shoes', "qty": 32, "lot": "1910239"}],
            "picking": {"id": 1, "name": 'Picking 7'},
        },
        "message": undefined
    },
}
var DEMO_SCAN_ANYTHING_PRODUCT = {
    'fetch' : {
        "data": {
            "type": "product",
            "id": 1,
            "name": "Super Product",
            "location_src": {
                "id": 1,
                "name":  'Location DSGF',
            },
        },
        "message": undefined
    },
}


window.DEMO_SINGLE_PUTAWAY = {
    "1": DEMO_SINGLE_PUTAWAY_1,
    "2": DEMO_SINGLE_PUTAWAY_2,
    "3": DEMO_SINGLE_PUTAWAY_3,
    "4": DEMO_SINGLE_PUTAWAY_4,
    "5": DEMO_SINGLE_PUTAWAY_5,
    "6": DEMO_SINGLE_PUTAWAY_6,
    "7": DEMO_SINGLE_PUTAWAY_7,
};
window.DEMO_SCAN_ANYTHING = {
    "pack": DEMO_SCAN_ANYTHING_PACK,
    "prod": DEMO_SCAN_ANYTHING_PRODUCT,
}

window.DEMO_CASES = {
    "single_pack_putaway": window.DEMO_SINGLE_PUTAWAY,
    "scan_anything": window.DEMO_SCAN_ANYTHING,
}
window.DEMO_CASE = {}

/* eslint no-use-before-define: 2 */  // --> ON
