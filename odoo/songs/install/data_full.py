# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import logging
import os
import anthem
from datetime import datetime
from anthem.lyrics.loaders import load_csv_stream, read_csv, load_rows
from anthem.lyrics.records import create_or_update
from anthem.exceptions import AnthemError
from ..common import req

_logger = logging.getLogger(__name__)


def get_files(req, default_file=None):
    """ Check if there is a DATA_DIR in environment else open default_file.

    DATA_DIR is passed by importer.sh when importing splitted file in parallel

    Returns a generator of file to import as DATA_DIR can contain a split of
    csv file
    """
    try:
        dir_path = os.environ['DATA_DIR']
    except KeyError:
        yield resource_stream(req, default_file)
    else:
        file_list = os.listdir(dir_path)
        for file_name in file_list:
            file_path = os.path.join(dir_path, file_name)
            yield open(file_path)


@anthem.log
def import_partner(ctx):
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    for content in get_files(req):
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_partner_link(ctx):
    """Redefine some parent_id on partners affiliates.

    Plus adapt names and types to fit this change.
    """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    with ctx.log(u"Create main customers"):
        content = resource_stream(req, 'data/install/0-partner.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')
    with ctx.log(u"Define invoice type on main partners"):
        content = resource_stream(req, 'data/install/1-invoice.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')
    with ctx.log(u"Define delivery, contact and other type on main partners"):
        content = resource_stream(req, 'data/install/2-delivery.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')
    with ctx.log(u"Rename main partners"):
        content = resource_stream(req, 'data/install/3-rename.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')
    with ctx.log(u"Change parent_id on partner to group them"):
        content = resource_stream(req, 'data/install/4-parent.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')
    with ctx.log(u"Small change on supplier which is also a customer"):
        content = resource_stream(req, 'data/install/5-supplier-client.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_partner_block_delivery(ctx):
    """Load flag on customer that are bad payers and must pay SO at order. This
    was managed by T28 in DB2
    """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    with ctx.log(u"Define bad payers customers (default_delivery_block)"):
        content = resource_stream(req, 'data/install/res_partner_T28.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def post_import_partner(ctx):
    import_partner_link(ctx)
    import_partner_block_delivery(ctx)


@anthem.log
def create_product_other(ctx):
    """ Create product 'Other' used when importing sale orders """
    values = {
        'name': "Divers",
        'default_code': "DIVERS",
        'list_price': 0.0
    }
    create_or_update(ctx, 'product.product',
                     '__setup__.product_other', values)


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({
        'tracking_disable': True,
        'no_connector_export': True,
        'force_archive_orderpoint': True,
        'disable_constrains_orderpoint': True})

    Product = ctx.env['product.product'].with_context(load_ctx)
    file_csv = 'data/install/product.csv'
    for content in get_files(req, file_csv):
        try:
            load_csv_stream(ctx, Product, content, delimiter=',')
        except anthem.exceptions.AnthemError as e:
            # Append filename in exception message
            message = ('File %s\n' % content.name) + e.message
            raise anthem.exceptions.AnthemError(message)


def product_copy_on_unactive(ctx):
    # Computed fields on product.template are not set for archived product
    # copy the values from product.product
    ctx.env.cr.execute("""
        UPDATE product_template as tmpl
        SET active=prod.active, default_code=prod.default_code
        FROM product_product as prod
        WHERE tmpl.id = prod.product_tmpl_id AND prod.active=False
    """)


def product_template_set_create_date(ctx):
    # Update create_date on all products
    # The hack in db2_import on create_date
    # doesn't work with parent objects of inherits
    ctx.env.cr.execute("""
        UPDATE product_template as tmpl
        SET create_date=prod.create_date
        FROM product_product as prod
        WHERE tmpl.id = prod.product_tmpl_id
    """)


@anthem.log
def post_import_products(ctx):
    product_copy_on_unactive(ctx)
    product_template_set_create_date(ctx)


@anthem.log
def import_product_supplierinfo(ctx):
    """ Importing product supplier infos from csv"""
    for content in get_files(req, 'data/install/supplierinfo.csv'):
        load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')


@anthem.log
def import_pricelist_items(ctx):
    """ Importing pricelists from csv"""
    for content in get_files(req, 'data/install/pricelist_items.csv'):
        load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def import_wh_family_locations(ctx):
    """ Importing family locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/location_family.csv')
    load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def import_wh_locations(ctx):
    """ Importing warehouse locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    for content in get_files(req, 'data/install/location.csv'):
        load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def import_other_locations(ctx):
    """ Importing other locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    with ctx.log(u"Importing reserve locations"):
        content = resource_stream(req, 'data/install/locators_reserve.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing parking locations"):
        content = resource_stream(req, 'data/install/locators_parking.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def location_compute_parents(ctx):
    """Compute parent_left, parent_right"""
    ctx.env['stock.location']._parent_store_compute()


@anthem.log
def import_delivery_round_config(ctx):
    """ Importing delivery round config from csv"""
    content = \
        resource_stream(req, 'data/install/round.template.version.csv')
    load_csv_stream(ctx, 'round.template.version', content, delimiter=',')

    content = resource_stream(req, 'data/install/delivery_template.csv')
    load_csv_stream(ctx, 'round.template', content, delimiter=',')
    content = resource_stream(
        req, 'data/install/delivery.carrier.template.csv')
    load_csv_stream(ctx, 'round.template', content, delimiter=',')

    content = resource_stream(req, 'data/install/delivery_tags.csv')
    load_csv_stream(ctx, 'round.tag', content, delimiter=',')
    content = resource_stream(req, 'data/install/delivery_itinerary.csv')
    load_csv_stream(ctx, 'round.itinerary', content, delimiter=',')
    content = resource_stream(req, 'data/install/delivery_clients.csv')
    load_csv_stream(ctx, 'round.itinerary.position', content, delimiter=',')


@anthem.log
def import_delivery_carriers_round(ctx):
    """ Importing carriers - delivery round mapping from csv """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Carrier = ctx.env['delivery.carrier'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/delivery.carrier.round.csv')
    load_csv_stream(ctx, Carrier, content, delimiter=',')


@anthem.log
def import_lots(ctx):
    """ Importing lots from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Lot = ctx.env['stock.production.lot'].with_context(load_ctx)
    for content in get_files(req, 'data/install/stock_production_lot.csv'):
        load_csv_stream(ctx, Lot, content, delimiter=',')


@anthem.log
def purge_inventory(ctx):
    """ Remove all inventory lines.

    Not removing lines would mean we have the risk that
    some lots have dupplicates (ALCN-1309)

    """
    inv1 = ctx.env.ref('__setup__.initial_inventory')
    inv2 = ctx.env.ref('__setup__.initial_inventory_no_lot')
    domain = [('inventory_id', 'in', (inv1.id, inv2.id))]
    ctx.env['stock.inventory.line'].search(domain).unlink()


@anthem.log
def import_inventory(ctx):
    """ Importing inventory from csv"""
    values = {
        'name': 'Initial',
        }
    inventory = create_or_update(ctx, 'stock.inventory',
                                 '__setup__.initial_inventory', values)

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(req, 'data/install/stock_inventory_line.csv')
    header, rows = read_csv(content)
    header.append('inventory_id/.id')
    new_rows = []
    for row in rows:
        row.append(inventory.id)
        new_rows.append(row)
    load_rows(ctx, model, header, list(new_rows))


@anthem.log
def import_inventory_without_lot(ctx):
    """ Importing second inventory without lots from csv"""
    values = {
        'name': 'Initial (products without lot)',
    }
    inventory = create_or_update(ctx, 'stock.inventory',
                                 '__setup__.initial_inventory_no_lot', values)

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(
        req, 'data/install/stock_inventory_line_without_lot.csv')
    header, rows = read_csv(content)
    header.append('inventory_id/.id')
    new_rows = []
    for row in rows:
        row.append(inventory.id)
        new_rows.append(row)
    load_rows(ctx, model, header, list(new_rows))


@anthem.log
def import_banks(ctx):
    """ Importing banks """
    content_supplier = \
        resource_stream(req, 'data/install/res_bank_supplier.csv')
    load_csv_stream(ctx, 'res.bank', content_supplier, delimiter=',')


@anthem.log
def import_bank_accounts(ctx):
    """ Import banks accounts """

    # By default, Odoo add a constraint on res_partner_bank to have only one
    # bank account by company. However Alcyon uses the same bank account
    # for one or several customers. We need to remove this constrains
    # before importing bank accounts
    drop_constraint_query = """
    ALTER TABLE res_partner_bank
    DROP CONSTRAINT IF EXISTS res_partner_bank_unique_number;
    """
    ctx.env.cr.execute(drop_constraint_query)

    content_supplier = resource_stream(
        req, 'data/install/res_partner_bank_supplier.csv')
    load_csv_stream(ctx, 'res.partner.bank', content_supplier, delimiter=',')


@anthem.log
def import_customer_banks_and_mandats(ctx):
    """
    Import customer banks and customers mandat from a file manually generated
    :param ctx:
    :return:
    """

    # By default, Odoo add a constraint on res_partner_bank to have only one
    # bank account by company. However Alcyon uses the same bank account
    # for one or several customers. We need to remove this constrains
    # before importing bank accounts
    drop_constraint_query = """
    ALTER TABLE account_banking_mandate
    DROP CONSTRAINT IF EXISTS account_banking_mandate_mandate_ref_company_uniq;
    """
    ctx.env.cr.execute(drop_constraint_query)

    # Delete the constraint on res_partner_bank (see comment above)
    drop_constraint_query = """
        ALTER TABLE res_partner_bank
        DROP CONSTRAINT IF EXISTS res_partner_bank_unique_number;
        """
    ctx.env.cr.execute(drop_constraint_query)

    content = resource_stream(req, 'data/source/mandats.csv')
    header, rows = read_csv(content)

    # Check the header of the file
    try:
        index_ref_customer = header.index('X0014')
        index_ref_mandat = header.index('Ref_Mandat')
        index_signature_date = header.index('Date_Signature')
        index_sequence = header.index('Sequence')
        index_prefix_bank = header.index('Cle_IBAN')
        index_bank_account = header.index('Compte_Bancaire')
        index_bic = header.index('BIC')
        index_date_last_run = header.index('Last_Run')
    except Exception:
        _logger.error(
            'Invalid mandat file. The header must be: X0015,X0011,X0014,'
            'Ref_Mandat,Date_Signature,Siecle,Sequence,Cle_IBAN,'
            'Compte_Bancaire,BIC,Last_Run')
        return

    check_customer_query = "SELECT id FROM res_partner WHERE ref = %s;"
    check_bank_query = "SELECT id FROM res_bank WHERE bic = %s;"
    check_bank_account_query = \
        "SELECT id FROM res_partner_bank WHERE " + \
        "sanitized_acc_number = %s AND partner_id = %s;"

    mandats = ctx.env['account.banking.mandate']

    index = 1
    for row in rows:
        try:
            # Verify the customer
            ref_customer = str(int(row[index_ref_customer]))
            ctx.env.cr.execute(check_customer_query, (ref_customer,))
            result = ctx.env.cr.fetchone()

            if not result:
                _logger.error('Customer not found with ref %s' % ref_customer)
                continue
            partner_id = result[0]

            # Check and create the Bank if needed
            bic = row[index_bic]
            ctx.env.cr.execute(check_bank_query, (bic,))
            result = ctx.env.cr.fetchone()

            if not result:
                xmlid = '__import__.bank_%s' % bic
                bank_value = {
                    'name': bic,
                    'bic': bic,
                }
                bank = create_or_update(ctx, 'res.bank', xmlid, bank_value)
                bank_id = bank.id
            else:
                bank_id = result[0]

            # Check and create the bank account if needed
            iban = row[index_prefix_bank] + row[index_bank_account]
            ctx.env.cr.execute(check_bank_account_query, (iban, partner_id))
            result = ctx.env.cr.fetchone()

            if not result:
                xmlid = '__import__.bank_account_%s_%s' % (ref_customer, iban)
                bank_account_value = {
                    'acc_number': iban,
                    'partner_id': partner_id,
                    'bank_id': bank_id,
                }
                bank_account = create_or_update(ctx, 'res.partner.bank',
                                                xmlid, bank_account_value)
                bank_account_id = bank_account.id
            else:
                bank_account_id = result[0]

            ref_mandat = row[index_ref_mandat]

            # Create the mandat
            if row[index_sequence] == 'F':
                recurrent_sequence_type = 'first'
            else:
                recurrent_sequence_type = 'recurring'

            xmlid = '__import__.mandate_%s_%s' % (ref_customer, ref_mandat)

            signature_date_str = row[index_signature_date]
            signature_date = datetime.strptime(signature_date_str, '%d/%m/%Y')
            signature_date_str = signature_date.strftime('%Y-%m-%d')

            mandat_value = {
                'unique_mandate_reference': ref_mandat,
                'format': 'sepa',
                'partner_bank_id': bank_account_id,
                'partner_id': partner_id,
                'type': 'recurrent',
                'recurrent_sequence_type': recurrent_sequence_type,
                'signature_date': signature_date_str,
            }

            if row[index_date_last_run]:
                last_run_str = row[index_date_last_run]
                last_run = datetime.strptime(last_run_str, '%d/%m/%Y')

                # In some case (for old customer), the last action date
                # is less than the signature date.
                # In this case, we set the last action like the signature
                # date
                if last_run < signature_date:
                    last_run = signature_date

                last_run_str = last_run.strftime('%Y-%m-%d')
                mandat_value['last_debit_date'] = last_run_str

            mandat = create_or_update(ctx, 'account.banking.mandate',
                                      xmlid, mandat_value)
            mandats |= mandat

            index += 1
        except Exception as e:
            _logger.error('Cannot import the line %s: %s' %
                          (index, ', '.join(row)))
            _logger.error(str(e))
            pass

        # Validate all created mandats
    mandats.write({'state': 'valid'})


@anthem.log
def import_stock_bins(ctx):
    """ Importing Stock Bins"""
    for content in get_files(req, 'data/install/product_stock_bin.csv'):
        load_csv_stream(ctx, 'product.stock.bin', content, delimiter=',')


@anthem.log
def post_import_stock_bins(ctx):
    """ Add route on product stocked depending on locators.

    This is a post correction of the csv file product_stock_bin.csv
    for both demo and full data modes.

    Plus add "Nouveauté" route if the former locator has only one letter
    and has route purchase.route_warehouse0_buy.
    As locator with 1 letter is not imported we take and clean this information
    from description_picking field on the product.

    """
    StockBin = ctx.env['product.stock.bin']

    food_route = ctx.env.ref('__setup__.stock_location_route_pick_ali')
    fridge_route = ctx.env.ref('__setup__.stock_location_route_pick_froid')
    mat_route = ctx.env.ref('__setup__.stock_location_route_pick_materiel')
    med_route = ctx.env.ref('__setup__.stock_location_route_pick_medoc')
    new_route = ctx.env.ref('__setup__.stock_location_route_new')

    family_map = [
        ('A', food_route),
        ('Q', fridge_route),
        ('E', mat_route),
        ('P', mat_route),
        ('G', med_route),
    ]

    cr = ctx.env.cr

    for family_letter, route in family_map:
        family = ctx.env.ref('__import__.location_family_%s' % family_letter)
        domain = [('bin_location_id', 'child_of', family.id)]
        product_bins = StockBin.search(domain)
        if not product_bins:
            continue
        products = product_bins.mapped('product_id')

        cr.execute(
            "INSERT INTO stock_route_product (product_id, route_id)"
            "  SELECT id, %s FROM product_template"
            "  WHERE id in %s"
            "    AND id NOT IN ("
            "      SELECT product_id FROM stock_route_product"
            "      WHERE route_id = %s)",
            (route.id, tuple(products.ids), route.id))

    def sql_create_routes(letter, route):
        cr.execute(
            "INSERT INTO stock_route_product (product_id, route_id)"
            "  SELECT id, %s FROM product_template"
            "  WHERE description_picking = %s"
            "    AND id NOT IN ("
            "      SELECT product_id FROM stock_route_product"
            "      WHERE route_id = %s)",
            (route.id, family_letter, route.id))

    for family_letter, route in family_map:
        sql_create_routes(family_letter, route)
        sql_create_routes(family_letter, new_route)


@anthem.log
def create_journals(ctx):
    """ Create the balance' journals """
    journal = ctx.env['account.journal'].search([
        ('code', '=', 'MISC')
    ], limit=1)
    if not journal:
        _logger.error('MISC journal not found')
        return

    supplier_xml_id = '__setup__.account_move_balance_supplier'
    create_or_update(ctx, 'account.move', supplier_xml_id, {
        'name': 'Balance fournisseur',
        'journal_id': journal.id,
    })

    customer_xml_id = '__setup__.account_move_balance_customer'
    create_or_update(ctx, 'account.move', customer_xml_id, {
        'name': 'Balance clients',  # In french for Catherine
        'journal_id': journal.id,
    })


@anthem.log
def import_customer_journal_items(ctx):
    """ Import customer journal items """
    import_journal_items(ctx, customer=True)


@anthem.log
def import_supplier_journal_items(ctx):
    """ Import supplier journal items """
    import_journal_items(ctx, supplier=True)


@anthem.log
def import_journal_items(ctx, customer=False, supplier=False):
    """ Import Journal Items """

    if customer:
        file_path = 'data/source/BALclients.csv'
        move = ctx.env.ref('__setup__.account_move_balance_customer')
    elif supplier:
        file_path = 'data/source/BALfournisseurs.csv'
        move = ctx.env.ref('__setup__.account_move_balance_supplier')
    else:
        raise Exception('You cannot start this method without specifying '
                        'the type of import')

    # This import cannot be executed twice. In this case we skip this import
    # without raise an error
    if move.line_ids:
        _logger.error('This import can only be executed once.'
                      'Lines are not empty')
        return

    ctx.env.cr.execute("SELECT code, id FROM account_account")
    accounts = dict(ctx.env.cr.fetchall())

    check_customer_ref_query = "SELECT id FROM res_partner WHERE ref = %s"

    AccountMoveLine = ctx.env['account.move.line']

    new_header = [
        'name',
        'partner_id/.id',
        'date_maturity',
        'account_id/.id',
        'debit',
        'credit',
        'move_id/.id'
    ]

    for content in get_files(req, file_path):
        header, rows = read_csv(content)

        index_account = header.index('Cpt gen.')
        index_customer_ref = header.index('Auxiliaire')
        index_deadline = header.index('Echeance')
        index_credit = header.index('Credit')
        index_debit = header.index('Debit')
        index_num_piece = header.index('n[piece')
        index_journal = header.index('Jrn')

        new_rows = []
        for row in rows:
            customer_ref = row[index_customer_ref]
            ctx.env.cr.execute(check_customer_ref_query, (customer_ref,))
            result = ctx.env.cr.fetchone()

            if not result:
                _logger.error('Customer not found with ref %s' % customer_ref)
                continue
            partner_id = result[0]

            # Account
            account = row[index_account]
            account_id = accounts[account]

            try:
                # Deadline
                deadline_str = row[index_deadline]
                deadline = datetime.strptime(deadline_str, '%d/%m/%Y')
                deadline_str = deadline.strftime('%Y-%m-%d')
            except Exception:
                deadline_str = datetime.now().strftime('%Y-%m-%d')

            # Debit
            debit_str = row[index_debit].replace(',', '.')
            debit = debit_str and float(debit_str) or 0

            # Credit
            credit_str = row[index_credit].replace(',', '.')
            credit = credit_str and float(credit_str) or 0

            if (credit * debit != 0) or (credit + debit < 0):
                _logger.error('Invalid value for credit (%s) and debit (%s)' %
                              (credit, debit))
                continue

            num_piece = row[index_num_piece]
            original_journal = row[index_journal]
            name = "%s - %s" % (original_journal, num_piece)

            new_rows.append(
                [name,
                 partner_id,
                 deadline_str,
                 account_id,
                 debit,
                 credit,
                 move.id])

        # Load rows without the method load_rows (we want to set the context)
        result = AccountMoveLine\
            .with_context(check_move_validity=False,
                          tracking_disable=True,
                          active_test=False,
                          import_initial_balance=True)\
            .load(new_header, new_rows)
        ids = result['ids']
        if not ids:
            messages = u'\n'.join(
                u'- %s' % msg for msg in result['messages']
            )
            ctx.log_line(u"Failed to load CSV "
                         u"in '%s'. Details:\n%s" %
                         (AccountMoveLine._name, messages))
            raise AnthemError(u'Could not import CSV. See the logs')
        else:
            ctx.log_line(u"Imported %d records in '%s'" %
                         (len(ids), AccountMoveLine._name))

        # Recompute matched percentage and amount
        move._compute_matched_percentage()
        move._amount_compute()


@anthem.log
def main(ctx):
    """ Loading full data (But in this function only small files,
    other files will be import by importer.sh)
    """
    create_product_other(ctx)
    # Putting some demo data in full mode because we don't have yet real data
    import_delivery_round_config(ctx)
    import_delivery_carriers_round(ctx)
    import_banks(ctx)
    import_bank_accounts(ctx)
    import_customer_banks_and_mandats(ctx)
