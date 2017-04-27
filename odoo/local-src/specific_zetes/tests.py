import requests

DOMAIN = 'http://localhost:8069/zetes/'
USER_CODE = '02'
ZONE_CODE = '01'


def identification():
    print '==== Identification ===='
    data = '208030824,2.2.3,3iV_101,REQU_USERCONTEXT,{},1,20170207,072932,' \
           '98427733121320,1,,01,,,,,,,,,,,,,,,,#'.format(USER_CODE)
    result = requests.post(DOMAIN, data=data)
    usercontext = result.content.split(',')
    print 'User name: {}'.format(usercontext[16])


def signoff():
    print '==== Sign Off ===='
    data = '208092662,2.2.3,3iV_101,RESU_USERCONTEXT,{},1,20170207,081534,' \
           '874277334413394,4,70,,1,Monica Checchi,,,,,,,,,,,,#'\
        .format(USER_CODE)
    result = requests.post(DOMAIN, data=data)
    print result.content


def print_zones():
    print '==== Get zones ===='
    data = '208030824,2.2.3,3iV_101,REQU_REFDATA,{},1,20170207,072934,' \
           '98427733121341,,,,,,,,,,,,,,,,,,,,,#'.format(USER_CODE)
    result = requests.post(DOMAIN, data=data)
    content = result.content
    if content.endswith('#\n\n'):
        content = content[:-3]
    for zone in content.split('\n'):
        data = zone.split(',')
        print '{}. {}'.format(data[13], data[14])


def assignment():
    print '==== Assignment ===='
    data = '208030828,2.2.3,3iV_101,REQU_ASSIGNMENT,{},1,20170207,072835,' \
           '30427733115352,1,1,1,{},,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#'\
        .format(USER_CODE, ZONE_CODE)
    result = requests.post(DOMAIN, data=data)
    assignment = result.content.split(',')
    picking_id = assignment[14]

    print assignment

    if not picking_id:
        raise Exception('Cannot find a picking')

    print 'Picking ID: ' + picking_id

    data = '208030828,2.2.3,3iV_101,RESU_ASSIGNMENT,{},1,20170207,072836,' \
           '30427733115363,{},,,,01,123456789,,,,,,,,,,#'\
        .format(USER_CODE, picking_id)
    requests.post(DOMAIN, data=data)

    return picking_id


def get_itempicks(picking_id):
    print '==== Get itempicks ===='
    data = '208030828,2.2.3,3iV_101,REQU_ITEMPICK,{},1,20170207,072904,' \
           '30427733118044,{},,,,1,0,,,,,,,,,,,,,,,,,,,#'\
        .format(USER_CODE, picking_id)
    result = requests.post(DOMAIN, data=data)

    content = result.content
    if content.endswith('#\n\n'):
        content = content[:-3]

    for move_str in content.split('\n'):
        move = move_str.split(',')

        move_id = move[17]
        zone = move[21]
        corridor = move[22]
        shelf = move[23]
        height = move[24]
        box = move[25]

        qty = move[36]

        data = '208030828,2.2.3,3iV_101,REQU_CATCHWEIGHT,{},1,20170207,' \
               '072929,30427733121295,{},,,,1,{},{},{},{},{},{},2520872,' \
               '00709,01,,,,,,,,,{},,{},,,,,,,,,,,#'\
            .format(USER_CODE, picking_id, move_id, zone, corridor, shelf,
                    height, box, qty, move[63])
        result = requests.post(DOMAIN, data=data)
        catchweigh = result.content.split(',')
        lot_number = catchweigh[21]
        print 'Lot number: {}'.format(lot_number)

        data = '208030828,2.2.3,3iV_101,RESU_CATCHWEIGHT,{},1,20170207,' \
               '072930,30427733121306,{},,,,1,{},,,,,,,,,,{},{},,,,,,,,,#'\
            .format(USER_CODE, picking_id, move_id, lot_number, qty)
        requests.post(DOMAIN, data=data)

        data = '208030828,2.2.3,3iV_101,RESU_ITEMPICK,{},1,20170207,072931,' \
               '30427733121317,{},,,,1,{},,{},{},,01,0,,,,,,,,,,,,,,,,,,,,' \
               ',,,,,,,,,,,,,,,,,#'.format(USER_CODE, picking_id,
                                           move_id, {}, {})
        requests.post(DOMAIN, data=data)


def validate_picking(picking_id):
    print 'Print validate picking'

    data = '208030828,2.2.3,3iV_101,RESU_ASSIGNMENT,{},1,20170207,073416,' \
           '304277331541559,{},,,,04,123456789,,,,,,,,,,#'\
        .format(USER_CODE, picking_id)
    requests.post(DOMAIN, data=data)


def print_picking(picking_id):
    data = '6217065353,2.2.3,3iV_101,REQU_PRINT,{},1,20170418,141715,' \
           '024284359531558,{},,,,,03,1,,,,1,,,,,,,,,#'\
        .format(USER_CODE, picking_id)
    requests.post(DOMAIN, data=data)


def reset_picking_action(picking_id, move_id):
    data = '6217065353,2.2.3,3iV_101,RESU_ITEMPICK,01,1,20170425,094959,' \
           '014285040975922,{},,,,1,{},,000005,000001,,05,2,,,,,,,,' \
           ',,,,,,,,,,,,,,,,,,,1,,,,,,,,,,#'.format(picking_id, move_id)
    requests.post(DOMAIN, data=data)


picking_id = None
move_id = None

# identification()
# print_zones()
# picking_id = assignment()
# get_itempicks(picking_id)
# validate_picking(picking_id)
# print_picking(picking_id)
# reset_picking_action(picking_id, move_id)
