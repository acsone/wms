# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import logging

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
    client = odoorpc.ODOO(
        config['host'],
        protocol=config['protocol'],
        port=config['port'],
        timeout=None,
    )
    client.login(config['db'], config['erp_user'], config['erp_pwd'])
    return client


def get_done_id():
    file_wr = open('script_odoo.txt', 'r')
    old_id = []
    for line in file_wr.readlines():
        old_id.append(int(line))
        file_wr.close()
    return old_id


def write_done_id(id):
    file_wr = open('script_odoo.txt', 'a')
    file_wr.write(str(id) + '\n')
    file_wr.close()


def write_log(
    so_id, so_name, so_line_id, so_line_name, state, refund_id, reason
):
    file_wr = open('result_odoo.txt', 'a')
    file_wr.write(
        '%s;%s;%s;%s;%s;%s;%s\n'
        % (
            str(so_id),
            so_name,
            str(so_line_id),
            so_line_name,
            str(state),
            str(refund_id),
            reason,
        )
    )
    file_wr.close()


def create_new_refund(client, partner_id, refund_account_id, order_name):
    invoice_obj = client.env['account.invoice']
    in_id = invoice_obj.create(
        {
            'reference_type': "none",
            'partner_id': partner_id,
            'account_id': refund_account_id,
            'type': 'out_refund',
            'name': '%s-%s'
            % (order_name, 'Correction Cde Magento du 30/11/2018'),
        }
    )
    return in_id


def recompute_taxes(client, refund_id):
    invoice_obj = client.env['account.invoice']
    refund = invoice_obj.browse(refund_id)
    refund.compute_taxes()


def contruct_esb_ref_range():
    esb_ref = []
    # Range FR
    for ref in range(100261412, 100261631):
        esb_ref.append(str(ref))
    # Range FR
    for ref in range(200005263, 200005265):
        esb_ref.append(str(ref))
    return esb_ref


def create_new_refund_line(
    client, invoice_id, account_id, product_id, name, amount, tax_ids
):
    invoice_line_obj = client.env['account.invoice.line']
    invoice_line_obj.create(
        {
            'name': name,
            'invoice_id': invoice_id,
            'product_id': product_id,
            'price_unit': amount,
            'account_id': account_id,
            'invoice_line_tax_ids': [[6, False, tax_ids]],
            'quantity': 1,
        }
    )


def get_sale_order_to_correct(config=False):
    logging.debug('---------START------------')
    client = rpc_client(config)
    sale_order_obj = client.env['sale.order']
    sale_order_line_obj = client.env['sale.order.line']
    old_id = get_done_id()
    esb_ref = contruct_esb_ref_range()
    all_sale_order = sale_order_obj.search(
        [
            ('esb_ref', 'in', esb_ref),
            ('sale_channel', '=', 'web'),
            ('id', 'not in', old_id),
        ]
    )
    for cpt, order_id in enumerate(all_sale_order, 1):
        new_refund_id = False
        print str("Order: %s/%s ID:%s" % (cpt, len(all_sale_order), order_id))
        order = sale_order_obj.browse(order_id)
        order_line_ids = sale_order_line_obj.search(
            [('order_id', '=', order_id), ('price_subtotal', '!=', 0.0)]
        )
        order_line = sale_order_line_obj.browse(order_line_ids)
        for pos, line in enumerate(order_line, 1):
            print str("Line: %s/%s" % (pos, len(order_line)))
            if line.product_uom_qty == 0:
                write_log(
                    order.id,
                    order.name,
                    line.id,
                    line.product_id.default_code,
                    False,
                    False,
                    'Free product line skipped',
                )
                continue
            elif line.product_uom_qty != line.qty_delivered:
                write_log(
                    order.id,
                    order.name,
                    line.id,
                    line.product_id.default_code,
                    False,
                    False,
                    'Qty delivered != Qty ordered %s'
                    % (line.product_uom_qty - line.qty_delivered),
                )
            else:
                # In order to force the onchange
                result = line.onchange(
                    {
                        u'qty_to_invoice': line.qty_to_invoice,
                        u'price_unit': line.price_unit,
                        u'product_uom_qty': line.product_uom_qty,
                        u'qty_invoiced': line.qty_invoiced,
                        u'currency_id': line.currency_id.id,
                        u'id': line.id,
                        u'procurement_ids': [],
                        u'qty_delivered': line.qty_delivered,
                        u'product_uom': line.product_uom.id,
                        u'route_id': False,
                        u'customer_lead': 0,
                        u'analytic_tag_ids': [],
                        u'order_id': {
                            u'date_order': '2018-11-30',
                            u'partner_id': order.partner_id.id,
                            u'pricelist_id': order.pricelist_id.id,
                            u'discount_pricelist_id': order.discount_pricelist_id.id,
                            u'picking_ids': [],
                            u'fiscal_position_id': order.fiscal_position_id.id,
                            u'supplier_promotion_allowed': True,
                        },
                        u'tax_id': [[6, False, line.tax_id.ids]],
                        u'discounting_type': u'multiplicative',
                        u'price_total': line.price_total,
                        u'invoice_status': u'no',
                        u'price_subtotal': 0,
                        u'product_id': line.product_id.id,
                        u'product_qty_unavailable': 0,
                        u'discount2': 0,
                        u'discount3': 0,
                    },
                    u'product_uom_qty',
                    {
                        u'qty_to_invoice': u'1',
                        u'sequence': u'',
                        u'price_unit': u'1',
                        u'product_uom_qty': u'1',
                        u'price_subtotal': u'1',
                        u'currency_id': u'',
                        u'procurement_ids.origin': u'',
                        u'procurement_ids.product_qty': u'',
                        u'procurement_ids': u'',
                        u'qty_delivered': u'1',
                        u'product_uom': u'1',
                        u'route_id': u'1',
                        u'customer_lead': u'',
                        u'analytic_tag_ids': u'',
                        u'procurement_ids.product_uom': u'',
                        u'name': u'',
                        u'state': u'1',
                        u'older_lot_life_date': u'',
                        u'procurement_ids.date_planned': u'',
                        u'procurement_ids.product_id': u'1',
                        u'procurement_ids.state': u'',
                        u'qty_invoiced': u'1',
                        u'exception': u'',
                        u'discount': u'1',
                        u'product_qty_remains_to_deliver': u'',
                        u'layout_category_id': u'',
                        u'product_qty_canceled': u'1',
                        u'tax_id': u'1',
                        u'discounting_type': u'1',
                        u'price_total': u'1',
                        u'invoice_status': u'1',
                        u'product_id': u'1',
                        u'product_qty_unavailable': u'',
                        u'qty_delivered_updateable': u'',
                        u'procurement_ids.location_id': u'',
                        u'discount2': u'1',
                        u'discount3': u'1',
                    },
                )
                to_write = result['value']
                if line.price_subtotal - to_write['price_subtotal'] > 1.0:
                    if not new_refund_id:
                        new_refund_id = create_new_refund(
                            client,
                            order.partner_id.id,
                            order.partner_id.property_account_receivable_id.id,
                            order.name,
                        )
                    create_new_refund_line(
                        client,
                        new_refund_id,
                        154,
                        line.product_id.id,
                        '%s: Corr. promo 30/11/2018 :%s'
                        % (order.name, line.name),
                        (line.price_subtotal - to_write['price_subtotal']),
                        line.tax_id.ids,
                    )
                    write_log(
                        order.id,
                        order.name,
                        line.id,
                        line.product_id.default_code,
                        True,
                        new_refund_id,
                        'Done refund for %s'
                        % abs(
                            line.price_subtotal - to_write['price_subtotal']
                        ),
                    )
                else:
                    write_log(
                        order.id,
                        order.name,
                        line.id,
                        line.product_id.default_code,
                        False,
                        False,
                        'Everything is fine',
                    )

        if new_refund_id:
            # We will force recompute Taxes on sale_order
            recompute_taxes(client, new_refund_id)
        write_done_id(order_id)
        print str("New refund %s" % new_refund_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--env', choices=['dev', 'integration', 'prod'], required=True
    )
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    get_sale_order_to_correct(config)
