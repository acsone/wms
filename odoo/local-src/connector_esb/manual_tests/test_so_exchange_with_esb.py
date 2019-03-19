# -*- coding: utf-8 -*-

"""
This script work with sale order to make a full test exchange
with the ESB.
"""

import argparse
import time

import odoorpc

# Default arguments
hostname = 'localhost'
port = 80
user = 'admin'
password = 'admin'
db_name = 'odoodb'

# Parsing command line arguments
parser = argparse.ArgumentParser(description='Test ESB sale order exchange.')
parser.add_argument('--hostname', default=hostname)
parser.add_argument('--port', default=port)
parser.add_argument('--user', default=user)
parser.add_argument('--password', default=password)
parser.add_argument('--db_name', default=db_name)
args = parser.parse_args()


def login(args):
    # print 'Connecting to {}:{}'.format(args.hostname, args.port)
    odoo = odoorpc.ODOO(args.hostname, port=args.port)
    odoo.login(args.db_name, args.user, args.password)
    return odoo
    # uid = odoo.env.user


odoo = login(args)
# Search for a specific customer
customer = odoo.execute('res.partner', 'search', [('name', 'like', 'HOGGE')])
product_1 = odoo.env.ref('__import__.product_2761427_product_template')[0]
# product_1 = odoo.env['product.product'].browse(product_1_id)

# Create a new sale order and confirm sale
so_data = {
    'partner_id': customer[0],
    'date_order': '2018-08-24',
    'sale_channel': 'fax',
    'carrier_id': 2,
    'client_order_ref': 'customer ref',
    'delivery_price': 23.5,
    'suite_name': '0123434234',
    'order_line': [
        (
            0,
            0,
            {
                'sequence': 1,
                # 'name': '345', #self.prod1.name,
                'product_id': product_1.id,
                'product_uom_qty': 7,
            },
        )
    ],
}
new_so_id = odoo.execute('sale.order', 'create', so_data)
print('New sale order with id {}'.format(new_so_id))
so = odoo.env['sale.order'].browse(new_so_id)
so.action_confirm_background()
# Wait till it has been sent to the ESB
while True:
    odoo.logout()
    time.sleep(10)
    odoo = login(args)
    so = odoo.env['sale.order'].browse(new_so_id)
    if not so:
        print('The sale order could not be found.')
        exit(0)
    elif so['esb_ref']:
        print(
            u'Sale order has been sent to the'
            u' ESB with esb_id {}'.format(so['esb_ref'])
        )
        break
    else:
        print(u'Sale order {} is in state {}'.format(so['id'], so['state']))

# Update the sale order, changes should be sent to the ESB
so['order_line'][0].product_uom_qty = 12
print('Updated the quantity on the sale order to 12')
odoo.logout()
