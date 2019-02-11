# -*- coding: utf-8 -*-
import time
import datetime
import logging
import argparse
import ConfigParser
import odoorpc


def get_config(path, env):
    """Returns a config dict for a given env"""
    config = ConfigParser.ConfigParser()
    with open(path) as config_file:
        config.readfp(config_file)
        if config.has_section(env):
            return dict(config.items(env))
        else:
            raise ValueError('Unknown env {}'.format(env))


def rpc_client(config):
    """Return a rpc client based on config dict"""
    client = odoorpc.ODOO(config['host'],
                          protocol=config['protocol'],
                          port=config['port'],
                          timeout=None)
    client.login(config['db'],
                 config['erp_user'],
                 config['erp_pwd'])
    return client


def get_done_id():
    file = open('script_odoo.txt', 'r')
    old_id = []
    for line in file.readlines():
        old_id.append(int(line))
    file.close()
    print str(old_id)
    return old_id


def write_done_id(id):
    file = open('script_odoo.txt', 'a')
    file.write(str(id) + '\n')
    file.close()

def create_new_refund(client, partner_id):
    invoice_obj = client.env['account.invoice']
    in_id = invoice_obj.create(
        {'reference_type': "none",
         'partner_id': partner_id,
         'account_id': 154,
         'type': 'out_refund',
        })
    return in_id

def create_new_refund_line(client,invoice_id, account_id, product_id,name,
                           amount):
    invoice_line_obj = client.env['account.invoice.line']
    invoice_line_obj.create({'name': name,
                        'invoice_id': invoice_id,
                        'product_id': product_id,
                        'price_unit': amount,
                        'account_id': account_id,
                        'quantity': 1,
                        })


def get_sale_order_to_correct(config=False):
    logging.debug('---------START------------')
    client = rpc_client(config)
    sale_order_obj = client.env['sale.order']
    sale_order_line_obj = client.env['sale.order.line']
    old_id = get_done_id()
    all_sale_order = sale_order_obj.search([('name', 'ilike', 'SO'),
                                            ('date_order', '<=', '2018-12-04'),
                                            ('id', '=', 536572),
                                            ('id', 'not in', old_id)])
    for cpt, order_id in enumerate(all_sale_order, 1):
        new_refund_id = False
        print str("Order: %s %s %s" % (cpt, len(all_sale_order), order_id))
        order = sale_order_obj.browse(order_id)
        new_order_id_tmp = order.copy()
        new_order_tmp = sale_order_obj.browse(new_order_id_tmp)
        new_order_date = datetime.datetime(2018, 11, 30, 0, 0)
        new_order_tmp.date_order = new_order_date
        order_line_ids = sale_order_line_obj.search([('order_id', '=',
                                                      order_id),
                                                     (
                                                     'price_total', '!=', 0.0)])
        order_line = sale_order_line_obj.browse(order_line_ids)
        for pos, line in enumerate(order_line, 0):
            print str("Line: %s %s" % (pos, len(order_line)))
            dup_line = new_order_tmp.order_line[pos]
            # In order to force the onchange
            if dup_line.product_uom_qty != 0:
                result = dup_line.onchange(
                    {u'qty_to_invoice': dup_line.qty_to_invoice,
                     u'price_unit': dup_line.price_unit,
                     u'product_uom_qty': dup_line.product_uom_qty,
                     u'qty_invoiced': dup_line.qty_invoiced,
                     u'currency_id': dup_line.currency_id.id,
                     u'id': dup_line.id,
                     u'procurement_ids': [],
                     u'qty_delivered': dup_line.qty_delivered,
                     u'product_uom': dup_line.product_uom.id,
                     u'route_id': False,
                     u'customer_lead': 0,
                     u'analytic_tag_ids': [],
                     u'order_id': {u'date_order': '2018-11-30',
                                   u'partner_id': new_order_tmp.partner_id.id,
                                   u'pricelist_id':
                                       new_order_tmp.pricelist_id.id,
                                   u'discount_pricelist_id':
                                       new_order_tmp.discount_pricelist_id.id,
                                   u'picking_ids': [],
                                   u'fiscal_position_id': new_order_tmp.fiscal_position_id.id,
                                   u'supplier_promotion_allowed': True,
                                   },
                     u'tax_id': [[6, False, dup_line.tax_id.ids]],
                     u'discounting_type': u'multiplicative',
                     u'price_total': dup_line.price_total,
                     u'invoice_status':  u'no',
                     u'price_unit': 0,
                     u'price_subtotal': 0,
                     u'product_id': dup_line.product_id.id,
                     u'product_qty_unavailable': 0,
                     u'discount2': 0,
                     u'discount3': 0},
                    u'product_uom_qty',
                    {u'qty_to_invoice': u'1', u'sequence': u'',
                     u'price_unit': u'1', u'product_uom_qty': u'1',
                     u'price_subtotal': u'1', u'currency_id': u'',
                     u'procurement_ids.origin': u'',
                     u'procurement_ids.product_qty': u'',
                     u'procurement_ids': u'', u'qty_delivered': u'1',
                     u'product_uom': u'1', u'route_id': u'1',
                     u'customer_lead': u'', u'analytic_tag_ids': u'',
                     u'procurement_ids.product_uom': u'', u'name': u'',
                     u'state': u'1', u'older_lot_life_date': u'',
                     u'procurement_ids.date_planned': u'',
                     u'procurement_ids.product_id': u'1',
                     u'procurement_ids.state': u'', u'qty_invoiced': u'1',
                     u'exception': u'', u'discount': u'1',
                     u'product_qty_remains_to_deliver': u'',
                     u'layout_category_id': u'', u'product_qty_canceled': u'1',
                     u'tax_id': u'1', u'discounting_type': u'1',
                     u'price_total': u'1', u'invoice_status': u'1',
                     u'product_id': u'1', u'product_qty_unavailable': u'',
                     u'qty_delivered_updateable': u'',
                     u'procurement_ids.location_id': u'', u'discount2': u'1',
                     u'discount3': u'1'})
                to_write = result['value']
                if abs(line.price_total - to_write['price_subtotal']) > 1.0:
                    if not new_refund_id:
                        new_refund_id = create_new_refund(client,
                                                          new_order_tmp.partner_id.id)
                    create_new_refund_line(client,new_refund_id,
                                           154,
                                           dup_line.product_id.id,
                                           'Refund discount :%s' % (
                                               dup_line.name),
                                           abs(line.price_total - to_write['price_subtotal']))




        sale_order_obj.unlink(new_order_id_tmp)
        print str(new_order_id_tmp)
        print str("New refund %s" % new_refund_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
    choices = ['dev', 'integration', 'prod'], required = True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    get_sale_order_to_correct(config)
