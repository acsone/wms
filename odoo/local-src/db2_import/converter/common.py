# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def convert_date(prefix, db2_row):
    dd = db2_row[prefix + 'jj']
    if dd == 0:
        return False
    mm = db2_row[prefix + 'mm']
    Y = "%s%02i" % (db2_row[prefix + 'ss'], db2_row[prefix + 'aa'])
    return "%s-%02i-%02i" % (Y, mm, dd)


def convert_int_date(idate):
    str_date = str(idate)
    Y = str_date[:4]
    mm = str_date[4:6]
    dd = str_date[6:]
    return "%s-%02i-%02i" % (Y, mm, dd)


def convert_customer(ref):
    return '__import__.customer_%s' % (ref)


def convert_supplier(ref):
    return '__import__.supplier_%s' % (ref)


def add_xmlid(record, xmlid, noupdate=False):
    """ Add a XMLID on an existing record """
    try:
        ref_id, __, __ = record.env['ir.model.data'].xmlid_lookup(xmlid)
    except ValueError:
        pass  # does not exist, we'll create a new one
    else:
        return record.env['ir.model.data'].browse(ref_id)
    if '.' in xmlid:
        module, name = xmlid.split('.')
    else:
        module = ''
        name = xmlid
    return record.env['ir.model.data'].create({
        'name': name,
        'module': module,
        'model': record._name,
        'res_id': record.id,
        'noupdate': noupdate,
    })


def create_or_update(model, xmlid, values):
    """ Create or update a record matching xmlid with values """
    record = model.env.ref(xmlid, raise_if_not_found=False)
    if record:
        record.update(values)
    else:
        record = model.create(values)
        add_xmlid(record, xmlid)
    return record


def convert_product_id(product_code):
    if product_code:
        xmlid = '__import__.product_%s' % product_code
    else:
        xmlid = '__setup__.product_other'
    return xmlid


def convert_user(resp_num):
    """ return user xmlid from a responsible number """
    if resp_num in (8, 9, 10):
        return False
    xmlid = '__setup__.res_user_%s' % resp_num
    return xmlid


def convert_coding(value):
    """Convert to utf8 and strip all DB2 messy strings"""
    if isinstance(value, basestring):
        value = value.decode('latin1').encode('utf8').strip()
    return value


def do_picking(pick, lines):
    """ Do a partial picking using delivered qty from DB2 """
    pick.action_confirm()
    pick.force_assign()
    pick.do_prepare_partial()
    for line in lines:
        product_xmlid = convert_product_id(line['product'])
        product = pick.env.ref(product_xmlid)
        move = pick.move_lines.filtered(
            lambda p: p.product_id == product)
        move_update_vals = {}
        if line.get('date'):
            move_update_vals['date'] = line['date']
        if line.get('date_expected'):
            move_update_vals['date_expected'] = line['date_expected']

        if move_update_vals:
            move.write(move_update_vals)

        ope = pick.pack_operation_ids.filtered(
            lambda p: p.product_id == product)

        if not ope:
            continue
        # += to make sure than we process all qty if there are
        # more than one line with same product
        ope.qty_done += line['qty_done']

    # in our case 0 on each operation means we don't want to transfer
    # as oposited to odoo process
    if any([op.qty_done for op in pick.pack_operation_ids]):
        pick = pick.with_context(
            __skip_check_tracking=True,
            __no_job_create_draft_invoice=True,
        )
        mig_location = None
        if pick.picking_type_code == 'incoming':
            # disable check on receive note for receptions
            # and skip backorder creation
            pick = pick.with_context(
                __no_pick_receive_note_check=True,
                __no_specific_stock_backorder=True,
                __no_job_create_draft_invoice=True,
                __no_backorder_choice=True)
            # set destination to location dedicated for migration
            # in order to not mess with the parking inventory
            mig_location = pick.env.ref('__setup__.mig_purchase_reception')
            for ope in pick.pack_operation_ids:
                if op.qty_done:
                    ope.location_dest_id = mig_location
        # for internal picks from stock to output location
        elif pick.picking_type_code == 'internal':
            # set source to location dedicated for migration
            # in order to create stock moves that won't affect the stock
            mig_location = pick.env.ref('__setup__.mig_sale_pick')
            for ope in pick.pack_operation_ids:
                if op.qty_done:
                    ope.location_id = mig_location

        result = pick.do_new_transfer()
        if result and result['res_model'] == 'stock.backorder.confirmation':
            # Accept backorder creation
            operations_to_delete = pick.pack_operation_ids.filtered(
                lambda o: o.qty_done <= 0)
            for pack in pick.pack_operation_ids - operations_to_delete:
                pack.product_qty = pack.qty_done
                if pick.picking_type_code in 'incoming':
                    if pack.qty_done:
                        pack.location_dest_id = mig_location
                elif pick.picking_type_code == 'internal':
                        pack.location_id = mig_location
            operations_to_delete.unlink()
            pick.do_transfer()
    # unreserve picking for which no qty has been delivered
    if pick.state != 'done':
        pick.do_unreserve()


def do_shipping(pick, lines):
    """ Transfert the last picking (Shipping)

    operations are mostly ok

    this does set the quantities

    Remainings goes in a backorder
    """
    pick.action_confirm()
    pick.do_prepare_partial()
    for line in lines:
        product_xmlid = convert_product_id(line['product'])
        product = pick.env.ref(product_xmlid)
        ope = pick.pack_operation_ids.filtered(
            lambda p: p.product_id == product)
        if not ope:
            continue
        # += to make sure than we process all qty if there are
        # more than one line with same product
        ope.qty_done += line['qty_done']

    # in our case 0 on each operation means we don't want to transfer
    # as oposited to odoo process
    if any([op.qty_done for op in pick.pack_operation_ids]):
        pick = pick.with_context(
            __skip_check_tracking=True,
            __no_job_create_draft_invoice=True)
        result = pick.do_new_transfer()
        if result and result['res_model'] == 'stock.backorder.confirmation':
            # Accept backorder creation
            operations_to_delete = pick.pack_operation_ids.filtered(
                lambda o: o.qty_done <= 0)
            for pack in pick.pack_operation_ids - operations_to_delete:
                pack.product_qty = pack.qty_done
            operations_to_delete.unlink()
            pick.do_transfer()
    # unreserve picking for which no qty has been delivered
    if pick.state != 'done':
        pick.do_unreserve()
