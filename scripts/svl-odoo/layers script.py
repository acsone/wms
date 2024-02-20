# Part of Odoo. See LICENSE file for full copyright and licensing details.
# AMAZING SCRIPT BY MVW, WAMA, DAFR

# ⢸⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⡷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠢⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠈⠑⢦⡀⠀⠀⠀⠀⠀
# ⢸⠀⠀⠀⠀⢀⠖⠒⠒⠒⢤⠀⠀⠀⠀⡇⠀⠀⠀⠀⠙⢦⡀⠀⠀⠀⠀
# ⢸⠀⠀⣀⢤⣼⣀⡠⠤⠤⠼⠤⡄⠀⠀⡇⠀⠀⠀⠀⠀⠀⠙⢄⠀⠀⠀⠀
# ⢸⠀⠀⠑⡤⠤⡒⠒⠒⡊⠙⡏⠀⢀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⡄⠀
# ⢸⠀⠀⠀⠇⢄⣀⣀⣀⣀⢀⠧⠟⠁⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀
# ⢸⠀⠀⠀⠸⣀⠀⠀⠈⢉⠟⠓⠀⠀ARE YA FIXING VALUATION, SON?!
# ⢸⠀⠀⠀⠀⠈⢱⡖⠋⠁⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⠀⣠⢺⠧⢄⣀⠀⠀⣀⣀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⣠⠃⢸⠀⠀⠈⠉⡽⠿⠯⡆⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⣰⠁⠀⢸⠀⠀⠀⠀⠉⠉⠉⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠣⠀⠀⢸⢄⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⠀⠀⢸⠀⢇⠀⠀⠀⠀⠀⠀⡇⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⠀⠀⡌⠀⠈⡆⠀⠀⠀⠀⠀⡇⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⠀⢠⠃⠀⠀⡇⠀⠀⠀⠀⠀⡇ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
# ⢸⠀⠀⠀⠀⢸⠀⠀⠀⠁⠀⠀⠀⠀⠀⠷                ⢸
#################################################################
#     Everybody gangsta until picking a Valuation Ticket !      #
#################################################################

# server action context
import datetime
import time
import sys
from odoo.exceptions import UserError
from odoo.tools import float_compare, profiler

# START -- conf.py --
# !!! PLEASE READ COMMENTS AND CONFIGURE THE SCRIPT TO MATCH YOUR USE-CASE !!!
# fmt: off

# -- CONFIGURATION -- #
# Context
ticket_ref = ''                 # Ticket ID (for traceability)
trigram    = ''                 # Trigram / Quadrigram (to be able to kick your ass if you screw up something)

# Modes
restore_valuation      = True   # Default Mode, restore your inventory valuation
show_progress_status   = False  # Display a progress status of how many products are yet to be processed.
show_db_products_logs  = False  # Get logs from the temporary table (might be very long to show on screen, use webshell if possible)
force_clean_table      = False  # Clean the custom table and index after you are done with the script

# Run
should_commit       = True      # Wherever the change should be applied to the database or not. Use False if you want to test the result.
redo_done_products  = False     # If False, the script will ignore products already Done. Set to True to recompute Dones products (useful if combined with specific_products)
specific_products   = False     # If you know your targets (list of product ids or refs).
specific_companies  = [1]       # Choose which company you want the script to run on. Set it to `env.companies` to run on all companies. If False, defaults to the currently selected company
clean_when_complete = False     # Should be true in production mode. When True, the script will drop the custom table & index on completion. (Do not use with schedule action)
avoid_archived      = False     # Set to False if you want to also fix archived products. (recommended)
raise_log           = True      # Used for unit tests. We do not want an error raised on completion.
log_report          = False     # Create an ir.logging for each product
display_summary     = True      # Display a summary of the modifications done by the script at the start of the report.

# Valuation
init_start_date   = "2023-09-30 21:59:00"        # If set, the SVLS before this date will be merged in 1 initialisation layer (ex: "2023-12-31 00:00:00")
update_start_date = False        # If set, the IN unit_cost will only be updated after this date (ex: "2023-12-31 00:00:00")
delete_before     = False        # Delete svls before fixing (not recommended)
sync_dates        = False        # Sync dates between stock_moves and stock valuation layers (not recommended)

use_account_move = True         # Use the Account Moves to compute IN unit cost (recommended for more accuracy but could absorb the price differences figures)
use_purchase     = True         # Use the Purchase Order to compute the IN unit cost (recommended)
use_std_price    = True         # (AVCO & FIFO for IN moves): When no data is found to compute the unit_cost: True -> Use standard_price | False -> Use SVL existing UC
use_first_svl_uc = True         # Use first SVL UC as starting price. Useful if first move is an OUT and no account move is present.
# fmt: on
# -- END CONFIGURATION -- #


specific_products = set()
print("collecting products with svl", file=sys.stderr)
env.cr.execute("select distinct product_id from stock_valuation_layer")
specific_products.update(row[0] for row in env.cr.fetchall())
print("collecting products with stock moves in FY 2024", file=sys.stderr)
env.cr.execute("select distinct product_id from stock_move where date>='2023-10-01'")
specific_products.update(row[0] for row in env.cr.fetchall())
print("collecting products with internal stock quants", file=sys.stderr)
env.cr.execute("select distinct product_id from stock_quant sq left join stock_location sl on sl.id = sq.location_id where sl.usage = 'internal'")
specific_products.update(row[0] for row in env.cr.fetchall())
specific_products = list(specific_products)
# specific_products = []

# SEQUENCES AND LANG MODIFIERS
custom_misc_desc = (
    "Productwaarde handmatig gewijzigd"  # "Cost Manually change" in Dutch, you can update it with wanted language.
)
# END SEQUENCES

# __SERVER_ACTION_DEBUG_PARAM_MARKER__ !!! DO NOT REMOVE !!! This marker is used by the server_action_debug module to encapsulate parameters
# __SCRIPT_CONFIG_TEST_MARKER__ !!! DO NOT REMOVE !!! This marker is used by the test module to separate the configuration from the execution

# TODO: Add common translations for misc SVL

if len(list(filter(bool, [restore_valuation, show_progress_status, show_db_products_logs, force_clean_table]))) != 1:
    raise UserError("Incorrect Configuration, 1 mode ONLY must be selected")

odoo_version = float(env["ir.module.module"].search([("name", "=", "base")]).installed_version[-8:-4])

product_reports = {}

StockValuationLayer = env["stock.valuation.layer"].sudo().with_context(active_test=avoid_archived, no_update_price_cache=True)
StockMove = env["stock.move"].sudo().with_context(active_test=avoid_archived, no_update_price_cache=True)
ProductProduct = env["product.product"].sudo().with_context(active_test=avoid_archived, no_update_price_cache=True)

if specific_companies:
    specific_companies = env["res.company"].browse([int(company) for company in specific_companies])
else:
    specific_companies = env.company

# Product default_code to id
if specific_products and isinstance(specific_products[0], str):
    specific_products = ProductProduct.search([("default_code", "in", specific_products)]).ids

any_data = {}  # Used in list comprehension as they can't access variable from outside scope, but can from global scope ('LOAD_DEREF', 'STORE_DEREF', 'LOAD_CLOSURE')
processed_svl_ids = []  # Contain the ids of the processed svls. Every svls in it is considered correct.

precs = {
    "qp": 2,  # UOM Precision (Qty)
    "vp": env.company.currency_id.decimal_places,  # Currency Precision (Value)
    "cp": env["decimal.precision"].precision_get("Product Price"),  # Product Price Precision (Cost)
}

timings = {
    "start": time.time(),
    "last_save": time.time(),
    "after_start": 14 * 60,  # 14 minutes
    "after_save": 20,  # 20 seconds
}

if update_start_date:
    update_start_date = datetime.datetime.strptime(update_start_date, "%Y-%m-%d %H:%M:%S")

if init_start_date:
    init_start_date = datetime.datetime.strptime(init_start_date, "%Y-%m-%d %H:%M:%S")

# END -- conf.py --
# START -- database.py --
# Product States stored in DB
STATE_NEW = 0
STATE_DONE = 1
STATE_IN_PROGRESS = 2


def save_progress(product, stock_move, valuation_total, valuation_initial, last_svl_date, svls_ids):
    # Pre-mature save when remaining run time is getting low. Set Product valuation restoration as 'In Progress'
    if (
        time.time() - timings["start"] >= timings["after_start"]
        and time.time() - timings["last_save"] >= timings["after_save"]
    ):
        write_product_to_db(
            product,
            STATE_IN_PROGRESS,
            product_reports[product.id],
            valuation_total,
            valuation_initial,
            svls_ids,
            stock_move.id,
            last_svl_date,
        )
        commit()
        timings["last_save"] = time.time()


def commit(force_commit=False):
    """
    Simply apply commit on the database if the option are set to avoid the conditional redundancy through the script.
    :return: Null
    """
    if should_commit or force_commit:
        env.cr.commit()


def model_exists(model_name):
    try:
        env[model_name]
        return True
    except Exception:
        return False


def write_product_to_db(product, state, report, tt_val, init_val, processed_svls, sm_id, last_svl_date):
    """
    Insert fixed product data in the script TABLE.
    The data set in the table should be enough to continue the restoration on future script runs.
    """
    params = {
        "product_id": product.id,
        "company_id": env.company.id,
        "state": state,
        "log": report,
        "processed_svls": processed_svls,
        "current_stock_move_id": sm_id,
        "last_svl_date": last_svl_date,
        "initial_quantity": init_val["quantity"],
        "initial_value": init_val["value"],
        "total_quantity": tt_val["quantity"],
        "total_value": tt_val["value"],
        "create_date": datetime.datetime.now(),
    }
    env.cr.execute(
        "SELECT id FROM tech_support_fix_valuation_v2 WHERE product_id = %(product_id)s AND company_id = %(company_id)s",
        params,
    )
    if len(env.cr.fetchall()):
        query = """
            UPDATE tech_support_fix_valuation_v2
            SET
                state = %(state)s,
                log = %(log)s,
                total_quantity = %(total_quantity)s,
                total_value = %(total_value)s,
                current_stock_move_id = %(current_stock_move_id)s,
                processed_svls = %(processed_svls)s,
                last_svl_date = %(last_svl_date)s
            WHERE
                product_id = %(product_id)s
                AND company_id = %(company_id)s;"""
    else:
        query = "INSERT INTO tech_support_fix_valuation_v2({}) VALUES ({});".format(
            ",".join(params.keys()), ",".join(["%(" + key + ")s" for key in params.keys()])
        )
    env.cr.execute(query, params)


def get_product_db_data(product):
    """
    Get product info of previous script runs from the sql table tech_support_fix_valuation_v2
    If there is no info stored on the table, then the product was not processed by the script, and defaults values are returned.
    """

    # Fetch data
    env.cr.execute(
        """
        SELECT *
        FROM tech_support_fix_valuation_v2
        WHERE product_id = %s AND company_id = %s
        """,
        [product.id, env.company.id],
    )
    if res := env.cr.dictfetchone():
        return res

    # Default Values
    return {
        "state": 0,
        "log": "",
        "processed_svls": [],
        "current_stock_move_id": None,
        "last_svl_date": None,
        "total_quantity": 0,
        "total_value": 0,
        "initial_quantity": product.quantity_svl,
        "initial_value": product.value_svl,
    }


def _get_products_where_query_and_params(state=None, states=None):
    if state is not None or not states:
        states = [state]

    wheres, params = [], []

    # State
    wheres.append("state in %s")
    params.append(tuple(states))

    # Companies
    wheres.append("company_id in %s")
    params.append(tuple(specific_companies.ids))

    # Products
    if specific_products:
        wheres.append("product_id in %s")
        params.append(tuple(specific_products))

    return "WHERE " + " AND ".join(wheres), params


def clean_done_products():
    where, params = _get_products_where_query_and_params(states=[STATE_DONE, STATE_IN_PROGRESS])
    env.cr.execute("DELETE FROM tech_support_fix_valuation_v2 " + where, params)


def table_exists(table_name):
    """Check if a table exists in postgres

    :param table_name: the table's name
    :return: True if the table exists
    :rtype: bool
    """
    env.cr.execute("SELECT to_regclass(%s);", [table_name])
    res = env.cr.fetchone()
    return res is not None and res[0] is not None


def table_init():
    """
    Create a POSTGRES TABLE containing Logs and state of each product. Useful for batching, scheduled action, logging.
    Create an INDEX on stock_valuation_layer.stock_valuation_layer_id to improve script performance.
    :return: Null
    """
    env.cr.execute(
        """
        CREATE TABLE IF NOT EXISTS tech_support_fix_valuation_v2 (
            id SERIAL PRIMARY KEY,
            product_id integer,
            company_id integer,
            state integer DEFAULT 0,
            log text,
            create_date timestamp,
            processed_svls integer[],
            total_quantity float8,
            total_value float8,
            initial_quantity float8,
            initial_value float8,
            current_stock_move_id integer,
            last_svl_date timestamp
        );
        CREATE INDEX IF NOT EXISTS stock_valuation_layer_id_support_index ON stock_valuation_layer (stock_valuation_layer_id) WHERE stock_valuation_layer_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS tech_support_fix_valuation_v2_idx ON tech_support_fix_valuation_v2 (product_id, company_id);
        CREATE INDEX IF NOT EXISTS tech_support_fix_valuation_v2_state_idx ON tech_support_fix_valuation_v2 (state);
    """
    )


def table_clean():
    """
    Clean the table tech_support_fix_valuation_v2 and the index stock_valuation_layer_id_support_index when the script is complete.
    The script is considered complete when get_products doesn't return more products.
    """
    if not force_clean_table and (not clean_when_complete or get_products().exists()):
        return

    env.cr.execute(
        """
        DROP TABLE IF EXISTS tech_support_fix_valuation_v2;
        DROP INDEX IF EXISTS stock_valuation_layer_id_support_index;
    """
    )
    commit(force_commit=force_clean_table)


# END -- database.py --
# START -- report.py --
# Ex: "By MVW For 2134514\n\n"
log_context_header = "{}{}{}".format(
    "By " + trigram + " " if trigram else "",
    "For " + ticket_ref if ticket_ref else "",
    "\n\n" if trigram or ticket_ref else "",
)

# REPORT MESSAGES
_STOCK_MOVE_MESSAGE = "{sm.product_uom_qty} {sm.product_uom.name} {direction} (#{sm.id}) - {sm.date}\n"
_SVL_MESSAGE = "SVL #{svl.id}:  qty:{svl.quantity:.{p[qp]}f}  value:{svl.value:.{p[vp]}f}  uc:{svl.unit_cost:.{p[cp]}f}  src:{uc_src}\n"
_VALUATION_MESSAGE = "Valuation =>  Qty: {:.{p[qp]}f}   Value: {:.{p[vp]}f}\n"
_PRODUCT_MESSAGE = (
    "-" * 20 + "\nProduct #{product.id} [Company #{company.id}] {product.default_code} - {product.name}\n"
)
_IN_REM_DATA_MESSAGE = "Rem Data of IN SVL#{svl.id} => qty: {svl.remaining_qty:.{p[qp]}f} | value: {svl.remaining_value:.{p[qp]}f} | uc: {rem_uc:.{p[cp]}f}\n"
_OUT_REM_DATA_MESSAGE = "Rem Qty of OUT SVL#{svl.id} =>  {svl.remaining_qty:.{p[qp]}f}\n"
_REVALUATION_MESSAGE = "Revaluation of SVL# {} for {:.{p[qp]}f} quantity -> value = {:.{p[vp]}f}\n"
_LANDED_COST_MESSAGE = "Landed cost SVL created #{svl.id} - {svl.description}: | value:{svl.value:.{p[vp]}f} | svl_related: {svl.stock_valuation_layer_id.id} | lc: {svl.stock_landed_cost_id.id}\n"
_SUMMARY_MESSAGE = """
Product: #{product.id} {product.display_name} (cid: {cid})
    Quantity: {diff_qty}   Value: {diff_val}"""


def _write_product_report(msg, product, lb_before=0, lb_after=0):
    """
    Write a message to the 'products' report.
    :param msg: String to write in the report.
    :param product: product.product related to your message(if you write in the products index)
    :param lb_before: Integer indicating how much line break you want before your message.
    :param lb_after: Integer indicating how much line break you want after your message.
    """
    if product.id not in product_reports:
        product_reports[product.id] = ""
    product_reports[product.id] += "\n" * lb_before + msg + "\n" * lb_after


def get_logs_from_db():
    """
    Get product logs from the script TABLE
    :return: list[str]
    """
    where, params = _get_products_where_query_and_params(state=STATE_DONE)
    env.cr.execute("SELECT log FROM tech_support_fix_valuation_v2 " + where, params)
    return [p["log"] for p in env.cr.dictfetchall()]


def get_summary():
    if not display_summary:
        return ""

    env.cr.execute(
        """
        SELECT
            company_id,
            product_id,
            total_quantity - initial_quantity as diff_qty,
            total_value - initial_value as diff_val
        FROM tech_support_fix_valuation_v2
        WHERE
            product_id {}
            and (
                round((total_quantity - initial_quantity)::numeric, 2) != 0
                or round((total_value - initial_value)::numeric, 2) != 0
            )
        ORDER BY abs(initial_value - total_value) DESC""".format("in %s" if specific_products else "is not null"),
        [tuple(specific_products)] if specific_products else [],
    )
    summary = []
    for res in env.cr.dictfetchall():
        product = ProductProduct.browse(res["product_id"])
        company = env["res.company"].browse(res["company_id"])
        uom = product.uom_id
        summary.append(
            _SUMMARY_MESSAGE.format(
                product=product,
                cid=company.id,
                diff_qty="{:+.{up}f} {}".format(res["diff_qty"], uom.name, up=rd_to_dgt(uom.rounding)),
                diff_val="{:+.{vp}f}".format(res["diff_val"], vp=precs["vp"]),
            )
        )

    return "DIFFERENCE SUMMARY:\n------------------" + "\n".join(summary) + "\n"


def get_progress_report():
    """Create a report with the number of products processed per company, so you can estimate when the script will end.
    To have a better estimate, we should count the number of stock moves (or move lines), as the main loop
    in this script is iterating over stock moves.
    """
    progress_by_company = {}
    msg = []
    if table_exists("tech_support_fix_valuation_v2"):
        # Count the progress by company
        where, params = _get_products_where_query_and_params(state=STATE_DONE)
        env.cr.execute(
            """
            SELECT company_id, count(product_id)
            FROM tech_support_fix_valuation_v2
        """
            + where
            + "GROUP BY company_id;",
            params,
        )
        for company_id, product_count in env.cr.fetchall():
            progress_by_company[company_id] = {"processed": product_count, "total": product_count}

    # Compute the total number of products by company
    for company in specific_companies:
        total = len(get_products(company))
        progress_by_company.setdefault(company.id, {"processed": 0, "total": 0})["total"] += total

    processed = total = 0
    for company_id, progress in progress_by_company.items():
        processed += progress["processed"]
        total += progress["total"]
        msg.append("Company #{}: processed {processed} out of {total} products".format(company_id, **progress))

    if table_exists("tech_support_fix_valuation_v2"):
        env.cr.execute(
            """
            SELECT product_id, company_id
            FROM tech_support_fix_valuation_v2
            WHERE state = %s LIMIT 1;
        """,
            [STATE_IN_PROGRESS],
        )
        if (res := env.cr.fetchone()) is not None:
            msg.append("\nCurrently working on product #{} (company #{})".format(*res))

    msg.append("\nTotal Progression: {:.2%}".format(processed / total))
    return "\n".join(msg)


# END -- report.py --
# START -- utils.py --
def raise_error(msg, should_raise=True):
    # Raise a Warning or a UserError based on the version if should_raise allows it
    if not should_raise:
        return
    if odoo_version < 15:
        raise Warning(msg)
    else:
        raise UserError(msg)


def is_zero(float_nb, rounding=None, digits=None):
    if not rounding and not digits:
        digits = 2
    return float_compare(0, float_nb, precision_rounding=rounding, precision_digits=digits) == 0


def rd_to_dgt(rounding):  # rounding to digits (decimal_places)
    return str("{:.10f}".format(rounding)).split("1")[0][::-1].find(".") + 1


float_round = StockValuationLayer._fields["quantity"].round


# END -- utils.py --
# START -- standard_price.py --
def update_standard_price(product, new_std_price):
    product.with_context(disable_auto_svl=True).write({"standard_price": float_round(new_std_price, precs["cp"])})


def compute_standard_price(product, svl):
    """
    Recompute the standard price.
    Should only be called after an IN move. This method still handle OUT moves, but should only be used for specific scenarios.
    :return: message mentioning the recomputation for report purpose
    """
    if svl.stock_move_id._is_dropshipped() or svl.stock_move_id._is_dropshipped_returned():
        _write_product_report("\tCompute Standard Price not available for DROPSHIPPED moves: Skip.", product)
        return
    if svl.stock_move_id._is_out():
        _write_product_report(
            "\tCompute Standard Price should not be called for OUT moves. If not done intentionally, please investigate.",
            product,
        )

    svl_domain = [
        ("company_id", "=", env.company.id),
        ("product_id", "=", product.id),
        ("id", "in", processed_svl_ids),
    ]
    current_valuation = get_current_valuation(product)
    quantity_svl = current_valuation["quantity"]
    value_svl = current_valuation["value"]

    new_std_price = None

    if product.cost_method == "average":
        if quantity_svl > 0:
            new_std_price = value_svl / quantity_svl
        elif quantity_svl == 0 and svl.stock_move_id._is_in():
            new_std_price = svl.unit_cost
        elif quantity_svl < 0 or quantity_svl == 0 and svl.stock_move_id._is_out():
            oldest_out_svl = StockValuationLayer.search(
                svl_domain + [("remaining_qty", "<", 0)], order="create_date asc, id asc", limit=1
            )
            new_std_price = oldest_out_svl.unit_cost

    elif product.cost_method == "fifo":
        if quantity_svl > 0:
            # Get uc from oldest IN svl with rem qty
            oldest_in_svl = StockValuationLayer.search(
                svl_domain + [("remaining_qty", ">", 0)], order="create_date asc, id asc", limit=1
            )
            new_std_price = oldest_in_svl.remaining_value / oldest_in_svl.remaining_qty
        elif quantity_svl == 0 and svl.stock_move_id._is_out():
            # Get uc from last IN svl
            last_in_svl = StockValuationLayer.search(
                svl_domain + [("quantity", ">", 0)], order="create_date desc, id desc", limit=1
            )
            last_in_value = sum((last_in_svl | last_in_svl.stock_valuation_layer_ids).mapped("value"))
            last_in_quantity = sum((last_in_svl | last_in_svl.stock_valuation_layer_ids).mapped("quantity"))
            new_std_price = (
                last_in_value / last_in_quantity
            )  # Because remaining_qty is 0, we recompute the unit_cost using the revaluation svls linked to the last_in svl
        elif quantity_svl < 0 or quantity_svl == 0 and svl.stock_move_id._is_in():
            # Get uc from the oldest OUT svl with neg rem qty
            oldest_out_svl = StockValuationLayer.search(
                svl_domain + [("remaining_qty", "<", 0)], order="create_date asc, id asc", limit=1
            )
            new_std_price = oldest_out_svl.unit_cost  # Rem qty is negative, hence we can't recompute using the rem data

    if new_std_price is not None:
        update_standard_price(product, new_std_price)
        _write_product_report("\t** New standard price computed : {} \n".format(product.standard_price), product)


# END -- standard_price.py --
# START -- unit_cost.py --
def _compute_out_standard_uc_and_value(svl):  # OUT standard
    unit_cost = svl.product_id.standard_price
    value = unit_cost * svl.quantity
    return unit_cost, value, ["std_price"]


def _compute_out_avco_uc_and_value(svl):  # OUT average
    unit_cost = svl.product_id.standard_price
    value = svl.currency_id.round(unit_cost * svl.quantity)
    uc_src = ["avg"]

    # Compute & Adjust Rounding Error (based on odoo standard code)
    current_valuation = get_current_valuation(svl.product_id)
    currency = svl.currency_id
    quantity_svl = current_valuation["quantity"]
    if float_compare(quantity_svl, 0, precision_digits=precs["qp"]) == 1:
        rounding_error = abs(value) - currency.round(abs(svl.quantity) * current_valuation["value"] / quantity_svl)
        max_allowed_rounding_error = currency.round(
            currency.rounding * abs(svl.quantity) / 2 + currency.rounding * 2
        )  # Check more lenient than standard
        if rounding_error and abs(rounding_error) <= max_allowed_rounding_error:
            value += rounding_error
            uc_src.append("rd_error:{}".format(rounding_error))
        elif rounding_error:  # Rounding Error is too big, should not happen, hence there is a valuation error
            _write_product_report(
                "/!\\ Rounding Error detected and not adjusted: {} > max {}\n".format(
                    rounding_error, max_allowed_rounding_error
                ),
                svl.product_id,
            )

    return unit_cost, value, uc_src


def _compute_out_fifo_uc_and_value(svl):  # OUT fifo
    uc_src = ["fifo"]

    unit_cost = svl.product_id.standard_price
    value = 0
    qty_to_valuate = abs(svl.quantity)

    previous_in_svls = StockValuationLayer.search(
        [
            ("company_id", "=", env.company.id),
            ("product_id", "=", svl.product_id.id),
            ("id", "in", processed_svl_ids),
            ("remaining_qty", ">", 0),
        ],
        order="create_date asc, id asc",
    )
    for svl_in in previous_in_svls:
        if is_zero(qty_to_valuate, rounding=svl.uom_id.rounding):
            break

        qty_removable = min(qty_to_valuate, svl_in.remaining_qty)
        qty_to_valuate -= qty_removable
        unit_cost = get_remaining_unit_cost(svl_in)
        value += qty_removable * unit_cost
        uc_src.append("SVL({}, q:{}, v:{})".format(svl_in.id, qty_removable, qty_removable * unit_cost))

    if not is_zero(qty_to_valuate, rounding=svl.uom_id.rounding):
        # If qty_to_valuate != 0, it means that the current svl make the stock go in negative,
        #   or that it was negative from the start, and that we need to valuate this quantity.
        # In the first scenario, unit_cost is equal to the last IN svl unit_cost (computed from rem data).
        # In the other scenario, unit_cost is equal to the product standard_price.
        value += qty_to_valuate * unit_cost
    else:
        unit_cost = value / abs(svl.quantity)

    return unit_cost, -value, uc_src


def _compute_in_standard_uc_and_value(svl):  # IN standard
    unit_cost = svl.product_id.standard_price
    return unit_cost, unit_cost * svl.quantity, ["std_price"]


_compute_in_methods = {}


def _compute_in_avco_uc_and_value(svl):  # IN average/fifo
    """
    Bunch of methods to compute an IN unit_cost.
    The priority of each method is defined in the list uc_getters_order_by_priority.
    The methods must return None if they are not able to get the unit_cost
    """

    def can_use(*conditions: bool, bypass_date=False):
        """Add a method to compute in cost.
        Ordered by priority, the first method returning a value will be used.

        :param list[bool] conditions: Should this method be available in the current context. All values are AND'ed.
        :param bool bypass_date: when True, the condition will be applied even if the the unit cost cannot be updated.
            (c.f. `_compute_in_avco_uc_and_value`)
        """
        any_data["can_use"] = (all(conditions), bypass_date)

        def wrapper(func):
            _compute_in_methods[func] = any_data["can_use"]
            return func

        return wrapper

    @can_use(use_purchase)
    def _get_from_purchase_line_id(stock_move):
        line = stock_move.purchase_line_id or stock_move.move_dest_ids.purchase_line_id[:1]
        if not line or is_zero(line.price_unit) or line.product_id.id != stock_move.product_id.id:
            return None

        # SBI: use price_subtotal instead of price_unit to take care of discounts
        price_unit = abs(
            line.currency_id._convert(
                line.price_subtotal, env.company.currency_id, env.company, stock_move.date, round=False
            )
        ) / line.product_qty
        uc = line.product_uom._compute_price(price_unit, stock_move.product_id.uom_id)
        return uc, ["PO({})".format(price_unit)]

    @can_use(use_purchase, odoo_version >= 16)
    def _get_from_purchase_kit(stock_move):
        line = stock_move.purchase_line_id or stock_move.move_dest_ids.purchase_line_id[:1]
        if (
            not line
            or is_zero(line.price_unit)
            or stock_move.product_id == line.product_id
            or not stock_move.bom_line_id
        ):
            return None

        # Copy/paste from _get_from_purchase_line_id()
        kit_price_unit = abs(
            line.currency_id._convert(
                line.price_unit, env.company.currency_id, env.company, stock_move.date, round=False
            )
        )
        kit_price_unit = line.product_uom._compute_price(kit_price_unit, stock_move.product_id.uom_id)

        cost_share = stock_move.bom_line_id._get_cost_share()  # Limitation: If the BoM changed, the cost will also
        uc = float_round(
            kit_price_unit * cost_share * line.product_qty / stock_move.product_qty, precision_digits=precs["cp"]
        )

        return uc, ["PO-Kit({})".format(uc)]

    @can_use(use_purchase, use_account_move)
    def _get_from_vendor_bill(stock_move):
        purchase_line_id = stock_move.purchase_line_id or stock_move.move_dest_ids.purchase_line_id[:1]
        if not purchase_line_id:
            return None

        for aml in stock_move.purchase_line_id.invoice_lines:
            aml_uom_qty = aml.product_uom_id._compute_quantity(
                aml.quantity, stock_move.product_id.uom_id, rounding_method="HALF-UP"
            )
            if aml.balance != 0 and is_zero(
                aml_uom_qty - stock_move.product_uom_qty, rounding=stock_move.product_id.uom_id.rounding
            ):
                return abs(aml.balance / stock_move.product_uom_qty), ["BILL"]
        return None

    @can_use(bypass_date=True)
    def _get_from_origin(stock_move):
        if stock_move.origin_returned_move_id and stock_move.origin_returned_move_id.stock_valuation_layer_ids:
            layers = stock_move.origin_returned_move_id.sudo().stock_valuation_layer_ids
            if (
                stock_move.origin_returned_move_id._is_dropshipped()
                or stock_move.origin_returned_move_id._is_dropshipped_returned()
            ):
                layers = layers.filtered(
                    lambda lay: float_compare(lay.value, 0, precision_rounding=lay.product_id.uom_id.rounding) <= 0
                )
            layers |= layers.stock_valuation_layer_ids
            quantity = sum(layers.mapped("quantity"))
            uc = 0
            if not is_zero(quantity, digits=precs["qp"]):
                uc = sum(layers.mapped("value")) / quantity
            return uc, ["origin_svl_uc"]
        return None

    @can_use(use_account_move)
    def _get_from_account_move(stock_move):
        if len(stock_move.account_move_ids) == 1 and (
            stock_move.location_id.usage in ["inventory", "production", "supplier"]
            or stock_move.location_dest_id.usage == "inventory"
        ):
            am = stock_move.account_move_ids
            uc = abs(am.amount_total) / abs(stock_move.product_qty)
            return uc, ["AM({}, {}, {})".format(am.id, am.amount_total, stock_move.product_qty)]
        return None

    @can_use(use_std_price)
    def _get_from_standard_price(stock_move):
        return abs(stock_move.product_id.standard_price), ["standard_price"]

    @can_use(bypass_date=True)
    def _get_from_svl(stock_move):
        # filter needed for dropship moves
        in_svls = stock_move.stock_valuation_layer_ids.filtered(lambda s: s.quantity > 0)
        if len(in_svls) >= 1:
            in_svls |= in_svls.stock_valuation_layer_ids
            # quantity can't be 0 due to previous condition
            uc = abs(sum(in_svls.mapped("value")) / sum(in_svls.mapped("quantity")))
            uc = float_round(uc, precision_digits=precs["cp"])
            return uc, ["svl"]
        return None

    can_update_uc = not update_start_date or svl.create_date >= update_start_date
    # Ordered by priority, the first value returned will be used.
    uc_getters_order_by_priority = [
        _get_from_origin,
        _get_from_vendor_bill,
        _get_from_purchase_line_id,
        _get_from_purchase_kit,
        _get_from_account_move,
        _get_from_standard_price,
        _get_from_svl,
    ]
    for uc_getter in uc_getters_order_by_priority:
        can_use, bypass_date = _compute_in_methods[uc_getter]
        if not bypass_date and not (can_use and can_update_uc):
            continue
        getter_ret_val = uc_getter(svl.stock_move_id)
        if getter_ret_val is not None:
            unit_cost, uc_src = getter_ret_val
            return unit_cost, unit_cost * svl.quantity, uc_src
    return 0, 0, []


def get_remaining_unit_cost(svl):
    # Return the unit cost recomputed from the remaining_value & remaining_qty.
    if svl.remaining_qty > 0:
        return svl.remaining_value / svl.remaining_qty
    return svl.unit_cost


def compute_unit_cost_and_value(svl):
    """
    Call the relevant compute method based on the move direction (in/out) and the costing method.
    """
    if use_first_svl_uc and len(processed_svl_ids) == 0:
        update_standard_price(svl.product_id, svl.unit_cost)

    compute_methods = {
        ("in_standard", "dropship_standard", "dropship_return_standard"): _compute_in_standard_uc_and_value,
        (
            "in_average",
            "in_fifo",
            "dropship_average",
            "dropship_fifo",
            "dropship_return_average",
            "dropship_return_fifo",
        ): _compute_in_avco_uc_and_value,
        ("out_standard"): _compute_out_standard_uc_and_value,
        ("out_average"): _compute_out_avco_uc_and_value,
        ("out_fifo"): _compute_out_fifo_uc_and_value,
    }
    method_key = "{}_{}".format(get_move_type(svl.stock_move_id), svl.product_id.cost_method)
    for keys, compute_method in compute_methods.items():
        if method_key in keys:
            return compute_method(svl)
    raise UserError("No compute method found for {}".format(method_key))


# END -- unit_cost.py --
# START -- misc_valuation.py --
def update_with_misc_valuation(valuation_total, product, date_start=None, date_end=None):
    """
    Find the global revaluation layers between the given dates, and will either:
        - Update them if it's a handled case (ex: Manual Price change)
        - Delete them if not
    :return: valuation_total updated with the values from misc_svls
    """
    handled_price_changes = {  # key: description to match, value: get new_unit_cost function
        "Product value manually modified": lambda description: float(
            description.split()[-1][:-1]
        ),  # format: 'Product value manually modified (from <old_uc> to <new_uc>)'
        "Product cost updated": lambda description: float(
            description.split()[-1][:-1]
        ),  # format: 'Manual Stock Valuation: <custom_comment>. Product cost updated from <old_uc> to <new_uc>.'
        "Change cost to": lambda description: float(description.split()[-1]),  # format: ?
        custom_misc_desc: lambda description: float(description.split()[-1][:-1]),  # format: ?
    }

    misc_domain = [
        ("product_id", "=", product.id),
        ("company_id", "=", env.company.id),
        ("stock_valuation_layer_id", "=", False),
        ("stock_move_id", "=", False),
        ("quantity", "=", 0),
    ]
    if date_start:
        misc_domain.append(("create_date", ">=", date_start))
    if date_end:
        misc_domain.append(("create_date", "<", date_end))

    misc_value_total = 0
    for m_svl in StockValuationLayer.search(misc_domain):
        new_unit_cost = None  # Next is not available in Server Action.
        for desc_key, to_float in handled_price_changes.items():
            if m_svl.description is not None and desc_key in m_svl.description:
                new_unit_cost = to_float(m_svl.description)
                break

        if product.cost_method == "fifo" or new_unit_cost is None:
            # Every misc svl not handled should be deleted
            _write_product_report("Misc SVL #{} deleted : {}\n".format(m_svl.id, m_svl.description), m_svl.product_id)
            m_svl.sudo().unlink()
            continue

        if product.cost_method == "standard":
            # Standard can't handle rounding errors like AVCO does
            new_unit_cost = float_round(new_unit_cost, precision_digits=precs["cp"])

        # Manual price change
        _write_product_report("Misc SVL #{} found : {}\n".format(m_svl.id, m_svl.description), m_svl.product_id)

        current_value = valuation_total["value"]
        target_value = valuation_total["quantity"] * new_unit_cost
        value_delta = m_svl.currency_id.round(target_value - current_value)  # Correct logic

        if float_compare(value_delta, m_svl.value, precision_rounding=m_svl.currency_id.rounding) != 0:
            new_description = "Product value manually modified (from {} to {})".format(
                product.standard_price, new_unit_cost
            )
            _write_product_report(
                "\t - Misc SVL value updated : from {:.2f} to {} -> {}\n".format(
                    m_svl.value, value_delta, new_description
                ),
                m_svl.product_id,
            )
            m_svl.write({"value": value_delta, "description": new_description})
            # As strange as it may seem, a price update doesn't impact the remaining values.

        update_standard_price(product, new_unit_cost)
        misc_value_total += value_delta
        processed_svl_ids.append(m_svl.id)
        valuation_total.update({"value": valuation_total["value"] + value_delta})

    if misc_value_total != 0:
        _write_product_report(
            "\tNew Current "
            + _VALUATION_MESSAGE.format(valuation_total["quantity"], valuation_total["value"], p=precs),
            product,
        )
    return valuation_total


def clean_svl(product):
    """
    Removes some layers from the database.
    They will be correctly regenerated by the script during the script execution.
    """
    svls = StockValuationLayer.search(
        [("company_id", "=", env.company.id), ("product_id", "=", product.id), ("id", "not in", processed_svl_ids)]
    )
    if delete_before:
        _write_product_report("Existing valuation Deleted\n", product)
        svls.sudo().unlink()
        return

    if sync_dates:
        env.cr.execute(
            """
            UPDATE stock_valuation_layer SVL SET create_date=SM.date, write_date=SM.date
            FROM stock_move SM WHERE SVL.stock_move_id = SM.id and SVL.product_id = %s;
        """,
            [product.id],
        )

    svl_to_delete = env["stock.valuation.layer"]
    misc_svls_descriptions = [  # Supported descriptions
        custom_misc_desc,
        "Product value manually modified",
        "value manually modified from",
        "Change cost to",
    ]
    for svl in svls:
        any_data["svl.description"] = svl.description
        if svl.description and "Revaluation of" in svl.description and "(negative inventory)" in svl.description:
            deletion_reason = "Revaluation of negative qty"
        elif "stock_landed_cost_id" in StockValuationLayer._fields and svl.stock_landed_cost_id.exists():
            deletion_reason = "Landed Cost - {}".format(svl.description)
        elif svl.stock_move_id and svl.product_id.id != svl.stock_move_id.product_id.id:
            deletion_reason = "Wrong stock_move associated"
        elif (
            svl.stock_move_id
            and svl.stock_move_id.location_id._should_be_valued()
            and svl.stock_move_id.location_dest_id._should_be_valued()
        ):
            deletion_reason = "Internal move: {} -> {}".format(
                svl.stock_move_id.location_id.name, svl.stock_move_id.location_dest_id.name
            )
        elif (
            svl.stock_move_id
            and not svl.stock_move_id.location_id._should_be_valued()
            and not svl.stock_move_id.location_dest_id._should_be_valued()
            and not (svl.stock_move_id._is_dropshipped() or svl.stock_move_id._is_dropshipped_returned())
        ):
            deletion_reason = "External move: {} -> {}".format(
                svl.stock_move_id.location_id.name, svl.stock_move_id.location_dest_id.name
            )
        elif svl.stock_move_id and get_move_type(svl.stock_move_id) is None:
            deletion_reason = "Move type not supported (not in [IN/OUT/DRP])"
        elif svl.stock_move_id and svl.stock_move_id.state != "done":
            deletion_reason = "Stock Move not Done"
        elif not svl.stock_move_id and not svl.stock_valuation_layer_id and not svl.description:
            deletion_reason = "No description to handle in script"
        elif (
            not svl.stock_move_id
            and not svl.stock_valuation_layer_id
            and ("Costing method change" in svl.description or "Valuation method change" in svl.description)
        ):
            deletion_reason = "Costing/Valuation method change"
        elif (
            not svl.stock_move_id
            and not svl.stock_valuation_layer_id
            and not any(svl_desc in any_data["svl.description"] for svl_desc in misc_svls_descriptions)
        ):
            deletion_reason = "Unknown misc SVL: {}".format(svl.description)
        elif (
            not svl.stock_move_id and svl.stock_valuation_layer_id and odoo_version >= 16 and svl.account_move_line_id
        ):  # field account_move_line_id does not exist before Odoo 16
            deletion_reason = "Bill price change"
        elif not svl.stock_move_id and svl.stock_valuation_layer_id:
            deletion_reason = "Unknown Revaluation (maybe to handle?): {}".format(svl.description)
        else:  # If no reason found, svl is valid
            continue
        _write_product_report("SVL #{} deleted : {}\n".format(svl.id, deletion_reason), svl.product_id)
        svl_to_delete |= svl
    svl_to_delete.sudo().unlink()


# END -- misc_valuation.py --
# START -- remaining_data.py --
def revaluate_negative_valuation(in_svl):
    """
    Create a revaluation layers to handle discrepancy between the cost of a sale without stock and the following stock incoming.
    :return: Tuple of: revaluation value, revaluation report message.
    """
    if not in_svl.stock_move_id._is_in():
        return 0

    currency = in_svl.currency_id
    replenished_qty = in_svl.quantity
    replenished_value = in_svl.value
    previous_out_svls = StockValuationLayer.search(
        [
            ("id", "in", processed_svl_ids),
            ("remaining_qty", "<", 0),
            ("company_id", "=", env.company.id),
            ("product_id", "=", in_svl.product_id.id),
        ],
        order="create_date ASC, id ASC",
    )

    if not previous_out_svls:
        return 0

    total_revaluation_value = 0
    revaluation_svls_data = []
    for prev_out_svl in previous_out_svls:
        if not replenished_qty:
            break

        quantity_to_revaluate = min(abs(prev_out_svl.remaining_qty), replenished_qty)

        # Trust me
        if in_svl.product_id.cost_method == "average":
            in_unit_cost = replenished_value / replenished_qty  # Prevent rounding issue
            corrected_out_value = currency.round(quantity_to_revaluate * in_unit_cost)

            current_out_value = float_round(
                prev_out_svl.value * (prev_out_svl.remaining_qty + quantity_to_revaluate) / prev_out_svl.quantity,
                precision_digits=precs["cp"],
            ) - float_round(
                prev_out_svl.value * prev_out_svl.remaining_qty / prev_out_svl.quantity,
                precision_digits=precs["cp"],
            )
        else:  # FIFO
            corrected_out_value = currency.round(quantity_to_revaluate * in_svl.unit_cost)
            current_out_value = currency.round(quantity_to_revaluate * prev_out_svl.unit_cost)

        value_delta = in_svl.currency_id.round(current_out_value - corrected_out_value)

        if not is_zero(value_delta, rounding=in_svl.currency_id.rounding):
            revaluation_svls_data.append(
                {
                    "description": "Revaluation of {} (negative inventory)".format(prev_out_svl.stock_move_id.origin),
                    "value": value_delta,
                    "stock_valuation_layer_id": prev_out_svl.id,
                    "product_id": in_svl.product_id.id,
                    "quantity": 0,
                    "unit_cost": 0,
                    "remaining_qty": 0,
                    "remaining_value": 0,
                    "stock_move_id": prev_out_svl.stock_move_id.id,
                    "company_id": in_svl.company_id.id,
                    "create_date": in_svl.create_date,
                }
            )
            _write_product_report(
                "\t\t" + _REVALUATION_MESSAGE.format(prev_out_svl.id, quantity_to_revaluate, value_delta, p=precs),
                in_svl.product_id,
            )

        # Update remaining data from previous negative outgoing svl
        prev_out_svl.write({"remaining_qty": prev_out_svl.remaining_qty + quantity_to_revaluate, "remaining_value": 0})
        _write_product_report("\t\tNew " + _OUT_REM_DATA_MESSAGE.format(svl=prev_out_svl, p=precs), in_svl.product_id)

        replenished_qty -= quantity_to_revaluate
        replenished_value -= corrected_out_value
        total_revaluation_value += value_delta

    rev_svls = create_svls(revaluation_svls_data)
    processed_svl_ids.extend(rev_svls.ids)

    if odoo_version < 16.2:
        replenished_value = in_svl.remaining_value * (replenished_qty / in_svl.remaining_qty)

    #  Update incoming svl to subtract negative part from previous outgoing svl
    in_svl.write(
        {
            "remaining_qty": replenished_qty,
            "remaining_value": replenished_value,
        }
    )
    _write_product_report(
        "\t\tNew " + _IN_REM_DATA_MESSAGE.format(svl=in_svl, rem_uc=get_remaining_unit_cost(in_svl), p=precs),
        in_svl.product_id,
    )
    return total_revaluation_value


def _compute_out_remaining_data(svl):
    """
    For outgoing moves, compute the context datas: remaining_qty, remaining_value, unit_cost
    :return: Dict containing unit_cost, remaining_quantity and remaining_value at the specific date.
    """
    qty_to_remove = abs(svl.quantity)

    previous_in_svls = StockValuationLayer.search(
        [
            ("company_id", "=", env.company.id),
            ("product_id", "=", svl.product_id.id),
            ("id", "in", processed_svl_ids),
            ("remaining_qty", ">", 0),
        ]
    )
    for svl_in in previous_in_svls:
        if is_zero(qty_to_remove, rounding=svl_in.uom_id.rounding):
            break

        removed_qty = min(qty_to_remove, svl_in.remaining_qty)
        removed_value = svl_in.currency_id.round(removed_qty * get_remaining_unit_cost(svl_in))

        svl_in.write(
            {
                "remaining_qty": svl_in.remaining_qty - removed_qty,
                "remaining_value": svl_in.remaining_value - removed_value,
            }
        )
        qty_to_remove -= removed_qty
        _write_product_report(
            "\t\tNew " + _IN_REM_DATA_MESSAGE.format(svl=svl_in, rem_uc=get_remaining_unit_cost(svl_in), p=precs),
            svl.product_id,
        )

    svl.write({"remaining_qty": -qty_to_remove, "remaining_value": 0})
    _write_product_report("\t\t" + _OUT_REM_DATA_MESSAGE.format(svl=svl, p=precs), svl.product_id)


def compute_remaining_data(svl):
    # Recompute Remaining Datas for OUT and IN moves.
    if svl.product_id.cost_method == "standard" and odoo_version < 16.0:
        # Before Odoo 16, remaining datas were not set for standard products
        svl.write({"remaining_qty": 0, "remaining_value": 0})
        return
    if svl.stock_move_id._is_dropshipped() or svl.stock_move_id._is_dropshipped_returned():
        svl.write({"remaining_qty": 0, "remaining_value": 0})
    if svl.stock_move_id._is_in():
        svl.write({"remaining_qty": svl.quantity, "remaining_value": svl.value})
        _write_product_report(
            "\t\t" + _IN_REM_DATA_MESSAGE.format(svl=svl, rem_uc=get_remaining_unit_cost(svl), p=precs), svl.product_id
        )
    if svl.stock_move_id._is_out():
        _compute_out_remaining_data(svl)


# END -- remaining_data.py --
# START -- init_layer.py --
def _get_moved_quantities(product, is_dest, date):
    moved_quantity = 0
    loc_f_name = "location_dest_id" if is_dest else "location_id"
    domain = [
        ("state", "=", "done"),
        ("{}.usage".format(loc_f_name), "in", ["internal", "transit"]),
        ("product_id", "=", product.id),
        ("date", "<", str(date)),
    ]
    read_fields = ["product_id", loc_f_name, "product_uom_id"]
    group_fields = read_fields + ["qty_done:sum"]
    for lines in env["stock.move.line"].sudo().read_group(domain, group_fields, read_fields, lazy=False):
        move_uom = env["uom.uom"].sudo().browse(lines["product_uom_id"][0])
        qty_done = move_uom._compute_quantity(lines["qty_done"], product.uom_id) * (-1 if not is_dest else 1)
        moved_quantity += qty_done
    return moved_quantity


def get_moved_quantities(product, date):
    quantity = 0
    quantity += _get_moved_quantities(product, True, date)
    quantity += _get_moved_quantities(product, False, date)
    return quantity


def get_last_purchase_price(product):
    env.cr.execute(
        """
        select price_subtotal / product_qty
        from purchase_order_line 
        where product_qty > 0 and product_id=%s 
        order by create_date desc 
        limit 1
        """
    )
    res = env.cr.fetchone()
    if not res:
        return 0
    return res[0]


def load_init_layer(product):
    assert init_start_date
    svls = StockValuationLayer.search([("product_id", "=", product.id), ("create_date", "<", str(init_start_date))])
    if len(svls) == 1:
        processed_svl_ids.append(svls.id)
        update_standard_price(product, svls.unit_cost)
    elif len(svls) == 0:
        # update_standard_price(product, get_last_purchase_price(product))
        pass
    else:
        raise_error(f"Multiple initial layers found for product {product.id}")


def create_init_layer(product, valuation_total):
    if not init_start_date:
        return
    # Unlink before date
    layers = StockValuationLayer.search([("product_id", "=", product.id), ("create_date", "<", str(init_start_date))])
    layers.sudo().unlink()
    _write_product_report("\nValuation deleted before {}.\n".format(init_start_date), product)
    # Get moved qty at date
    quantity = get_moved_quantities(product, init_start_date)
    value = quantity * product.standard_price
    # Create init layer with qty & standard_price
    valuation_total["value"] = value
    valuation_total["quantity"] = quantity
    if float_compare(quantity, 0, precision_digits=precs["qp"]) != 0:
        vals = {
            "create_date": init_start_date,
            "remaining_qty": quantity,
            "quantity": quantity,
            "remaining_value": max(0, value),
            "value": value,
            "unit_cost": product.standard_price,
            "product_id": product.id,
            "company_id": env.company.id,
            "description": "Odoo Support: initialisation layer.",
        }
        svl = create_svls(vals)
        processed_svl_ids.append(svl.id)
        _write_product_report("New " + _SVL_MESSAGE.format(svl=svl, uc_src="init", p=precs), product)
    _write_product_report("Current " + _VALUATION_MESSAGE.format(quantity, value, p=precs) + "\n\n", product)


# END -- init_layer.py --
# START -- product_product.py --
def restore_product_valuation(product):
    """Main function, fix svls for a specific product, by recomputing the value for each stock move."""
    precs["qp"] = rd_to_dgt(product.uom_id.rounding)  # Set UOM precision

    (
        valuation_total,
        valuation_initial,
        last_svl_date,
        stock_moves,
        state,
    ) = _init_product_restoration(product)

    if state == STATE_DONE:
        return

    for stock_move in stock_moves:
        # Update with misc valuation between stock moves
        current_svl_date = stock_move.date
        if sm_svls := stock_move.stock_valuation_layer_ids.filtered(lambda s: s.quantity != 0):
            current_svl_date = sm_svls[0].create_date
        update_with_misc_valuation(valuation_total, product, date_start=last_svl_date, date_end=current_svl_date)
        last_svl_date = current_svl_date

        # Restore classic stock move valuation
        restore_stock_move_valuation(stock_move, valuation_total)

        # Save Progress based on timed condition
        save_progress(product, stock_move, valuation_total, valuation_initial, last_svl_date, processed_svl_ids)

    # Last misc SVL Update
    update_with_misc_valuation(valuation_total, product, date_start=last_svl_date)
    product._compute_value_svl()

    _write_product_report(
        "Initial " + _VALUATION_MESSAGE.format(valuation_initial["quantity"], valuation_initial["value"], p=precs),
        product,
        1,
        0,
    )
    _write_product_report(
        "Final " + _VALUATION_MESSAGE.format(product.quantity_svl, product.value_svl, p=precs), product, 0, 1
    )

    # Product Restoration is Finished
    if log_report:  # create an Ir.Logging for the product
        log(log_context_header + product_reports[product.id], level="info")

    # Set Product valuation restoration as 'Done'
    write_product_to_db(
        product, STATE_DONE, product_reports[product.id], valuation_total, valuation_initial, [], None, None
    )
    commit()


def _init_product_restoration(product):
    """
    Handle Pre-Restoration logics
    Fetch product data and init variables needed for the restoration.
    """

    processed_svl_ids.clear()
    product_db_data = get_product_db_data(product)

    valuation_total = {"value": product_db_data["total_value"], "quantity": product_db_data["total_quantity"]}
    valuation_initial = {"value": product_db_data["initial_value"], "quantity": product_db_data["initial_quantity"]}

    if product_db_data["state"] == STATE_NEW:
        _write_product_report(_PRODUCT_MESSAGE.format(product=product, p=precs, company=env.company), product)
        write_product_to_db(
            product, STATE_IN_PROGRESS, product_reports[product.id], valuation_total, valuation_initial, [], None, None
        )
        commit()

        # SBI - we have cleaned ourselves by loading the 30/9 data
        # create_init_layer(product, valuation_total)
        # clean_svl(product)
        load_init_layer(product)

    elif product_db_data["state"] == STATE_IN_PROGRESS:
        processed_svl_ids.extend(product_db_data["processed_svls"])
        _write_product_report("[WITH SAVED DATA] - " + product_db_data["log"], product)

    elif product_db_data["state"] == STATE_DONE:
        _write_product_report("[FROM SAVED DATA] - " + product_db_data["log"], product)

    stock_moves = None
    if product_db_data["state"] != STATE_DONE:  # Operation can be slow and is not needed when product is Done
        stock_moves = get_product_stock_moves(product, product_db_data["current_stock_move_id"], init_start_date)

    return valuation_total, valuation_initial, product_db_data["last_svl_date"], stock_moves, product_db_data["state"]


def _get_last_valuated_svl(product):
    """
    Get the last valuated layer from a specific date.
    :return: Array of stock.valuation.layer
    """
    domain = [
        ("company_id", "=", env.company.id),
        ("product_id", "=", product.id),
        ("id", "in", processed_svl_ids),
        ("unit_cost", ">", 0),
    ]
    return StockValuationLayer.search(domain, order="create_date desc, id desc", limit=1)


def get_current_valuation(product):
    # Return the 'current' valuation based on the processed_svl_ids.
    domain = [
        ("company_id", "=", env.company.id),
        ("product_id", "=", product.id),
        ("id", "in", processed_svl_ids),
    ]
    past_svls = StockValuationLayer.search(domain, order="create_date desc, id desc")
    past_qty = float_round(sum(past_svls.mapped("quantity")), precision_digits=precs["qp"])
    past_value = sum(past_svls.mapped("value"))
    past_uc = abs(past_value / past_qty) if past_qty else _get_last_valuated_svl(product).unit_cost
    return {"quantity": past_qty, "value": past_value, "unit_cost": past_uc}


def _get_products_domain():
    """Return a domain to get the list of products to process"""
    domain = [("type", "=", "product")]
    if specific_products:
        domain += [("id", "in", specific_products)]
    return domain


def get_products(company=None):
    """
    Get a list of products based on the script configuration. (specific or by auto filter)
    Only the products with stock moves or stock valuation layers are returned
    :return: product.product recordset
    """
    company = company or env.company
    env.cr.execute(
        "SELECT product_id FROM tech_support_fix_valuation_v2 WHERE state = 1 AND company_id = %s", [company.id]
    )
    done_products = ProductProduct.browse([r[0] for r in env.cr.fetchall()])
    company_domain = ["|", ("company_id", "=", company.id), ("company_id", "=", False)]
    # Remove the products already done
    product_ids = ProductProduct.search(_get_products_domain() + company_domain) - done_products

    domain = [("product_id", "in", product_ids.ids)] + company_domain
    res = StockMove.read_group(domain, [], ["product_id"], lazy=False)
    res += StockValuationLayer.read_group(domain, [], ["product_id"], lazy=False)
    # Only get the products having at least one stock move or one svl
    product_ids &= ProductProduct.browse([r["product_id"][0] for r in res if r["__count"] > 0])
    if odoo_version < 14:
        return product_ids.with_context(force_company=company.id)

    print(f"{len(product_ids)} products to process")
    return product_ids.with_company(company)


# END -- product_product.py --
# START -- stock_move.py --
def get_product_stock_moves(product, sm_id=None, start_date=None):
    """
    Get a lists of the product stock moves ordered by date.
    If a sm_id is given, we remove every stock moves from before the given one.
    :return: stock.move recordset
    """
    domain = [("product_id", "=", product.id), ("company_id", "=", env.company.id), ("state", "=", "done")]
    if start_date:
        domain.append(("date", ">=", str(start_date)))
    stock_moves = StockMove.search(domain, order="date ASC, id ASC").filtered(lambda sm: get_move_type(sm) is not None)
    if sm_id:  # Every stock_moves before sm_id have already been processed.
        done_stock_moves = StockMove
        for sm in stock_moves:
            done_stock_moves = done_stock_moves + sm
            if sm.id == sm_id:
                break
        stock_moves = stock_moves - done_stock_moves
    return stock_moves


def restore_stock_move_valuation(stock_move, valuation_total):
    is_dropshipped = stock_move._is_dropshipped() or stock_move._is_dropshipped_returned()

    _write_product_report(
        _STOCK_MOVE_MESSAGE.format(direction=get_move_type(stock_move).upper(), sm=stock_move, p=precs),
        stock_move.product_id,
        1,
        0,
    )

    svl = get_stock_move_svl(stock_move, merge=not is_dropshipped)

    valued_quantity = get_valued_qty(stock_move)
    if not valued_quantity:
        # If there's no stock move lines, there's no valuation, we delete the svl, and continue with the next stock move.
        _write_product_report(
            "\tStock Move #{} has no quantity, continue.\n".format(stock_move.id), stock_move.product_id
        )
        if svl.exists():
            _write_product_report("\tSVL #{} deleted\n".format(svl.ids), stock_move.product_id)
            svl.sudo().unlink()
        return

    # Update/Create Svl with correct data
    if is_dropshipped:
        svl = compute_dropship_svls(stock_move, svl, valued_quantity)
    else:
        svl = compute_svl(stock_move, svl, valued_quantity)

    # Update Remaining Data
    compute_remaining_data(svl)

    # Revaluate Negative Quantities
    valuation_total["value"] += revaluate_negative_valuation(svl)

    # Update with potential landed cost linked to current svl
    valuation_total["value"] += compute_landed_cost(svl)

    # SVL is now correct, we can add it to the global valuation
    valuation_total["quantity"] += sum(svl.mapped("quantity"))
    valuation_total["value"] += sum(svl.mapped("value"))

    processed_svl_ids.extend(svl.ids)
    _write_product_report(
        "\tCurrent " + _VALUATION_MESSAGE.format(valuation_total["quantity"], valuation_total["value"], p=precs),
        stock_move.product_id,
    )

    # Update product standard_price
    if stock_move._is_in():
        compute_standard_price(stock_move.product_id, svl)


def get_move_type(stock_move):
    """
    Return a string with the types of move: 'in' | 'out' | 'dropship' | or 'dropship_return'
    Only valued types are returned, hence if the returned value is None, it is not a valued move.
    """
    if stock_move._is_in():
        return "in"
    if stock_move._is_out():
        return "out"
    if stock_move._is_dropshipped():
        return "dropship"
    if stock_move._is_dropshipped_returned():
        return "dropship_return"
    return None


def get_valued_qty(sm):
    """
    Return the valued quantity on a stock move
    """
    valued_quantity = 0
    move_uom = sm.product_id.uom_id

    if sm._is_dropshipped() or sm._is_dropshipped_returned():
        for line in sm.move_line_ids:
            valued_quantity += line.product_uom_id._compute_quantity(line.qty_done, move_uom, rounding_method="HALF-UP")
        return valued_quantity

    lines_in = sm._get_in_move_lines()
    lines_out = sm._get_out_move_lines()

    if lines_in and lines_out:
        with open("stock_valuation_layer.log", "a") as f:
            f.write(f"Stock Move #{sm.id} has both incoming an outgoing move lines.\n")
        print("Stock Move #{} has both incoming an outgoing move lines.".format(sm.id))

    for line in lines_in:
        valued_quantity += line.product_uom_id._compute_quantity(line.qty_done, move_uom, rounding_method="HALF-UP")

    for line in lines_out:
        valued_quantity -= line.product_uom_id._compute_quantity(line.qty_done, move_uom, rounding_method="HALF-UP")

    return valued_quantity


# END -- stock_move.py --
# START -- stock_valuation_layer.py --
def get_stock_move_svl(stock_move, merge=True):
    """
    If merge is True:
      Ensure that, a maximum of 1 SVL is linked to this stock_move.
      If multiple, then the excess is unlinked
    :return: stock.valuation.layer recordset
    """
    svls = StockValuationLayer.search(
        [
            ("stock_move_id", "=", stock_move.id),
            ("stock_valuation_layer_id", "=", None),
            ("company_id", "=", env.company.id),
            ("product_id", "=", stock_move.product_id.id),
        ],
        order="id ASC",
    )
    if len(svls) <= 1 or not merge:
        return svls

    # Merge layers into single SVL.
    svl_master = svls[-1]
    svl_master.write({"quantity": sum(svls.mapped("quantity")), "value": sum(svls.mapped("value"))})
    _write_product_report("\tSVLS ({}) merged into SVL #{}\n".format(svls.ids, svl_master.id), svl_master.product_id)
    (svls - svl_master).sudo().unlink()
    return svl_master


def _write_svl_update_report(svl, new_quantity, new_unit_cost, new_value):
    if float_compare(svl.quantity, new_quantity, precision_digits=precs["qp"]) != 0:
        _write_product_report(
            "\tQuantity changed from {:.{p[qp]}f} to {:.{p[qp]}f}\n".format(svl.quantity, new_quantity, p=precs),
            svl.product_id,
        )
    if float_compare(svl.unit_cost, new_unit_cost, precision_digits=precs["cp"]) != 0:
        _write_product_report(
            "\tUnit Cost changed from {:.{p[cp]}f} to {:.{p[cp]}f}\n".format(svl.unit_cost, new_unit_cost, p=precs),
            svl.product_id,
        )
    if float_compare(svl.value, new_value, precision_digits=precs["vp"]) != 0:
        _write_product_report(
            "\tValue changed from {:.{p[vp]}f} to {:.{p[vp]}f}\n".format(svl.value, new_value, p=precs), svl.product_id
        )


def compute_dropship_svls(stock_move, svls, valued_quantity):
    """
    Update / Create the SVLs linked to a dropshipped move with correct value/quantity/unit_cost.
    This method does not impact other SVLs, aka it does not update the remaining datas.

    Dropship moves must have 2 SVLs that are opposite of each others (the sum of their quantity and value must be 0).
    """
    if (
        len(svls) not in [0, 2]
        or (len(svls) == 2 and any(is_zero(q, digits=precs["qp"]) for q in svls.mapped("quantity")))
        or (len(svls) == 2 and not is_zero(sum(svls.mapped("quantity")), digits=precs["qp"]))
    ):
        _write_product_report(
            "\tDropship SVLs incorrect: svls #{} unlinked.\n".format(
                len(svls),
            ),
            stock_move.product_id,
        )
        svls.sudo().unlink()

    if is_new_svls := not svls.exists():
        svls = stock_move._create_dropshipped_svl(forced_quantity=valued_quantity)

    in_svl = svls.filtered(lambda s: s.quantity > 0)
    out_svl = svls.filtered(lambda s: s.quantity < 0)

    # A correct quantity is needed for compute_unit_cost_and_value
    in_svl.write({"quantity": valued_quantity})
    out_svl.write({"quantity": -valued_quantity})

    unit_cost, value, uc_src = compute_unit_cost_and_value(in_svl)

    if not is_new_svls:  # Create Report for only the IN svl, the value are the same for both of them.
        _write_svl_update_report(in_svl, valued_quantity, unit_cost, value)

    # Update value even if no difference is detected, rounding diff can still have an impact on global valuation
    in_svl.write({"value": value, "unit_cost": unit_cost})
    out_svl.write({"value": -value, "unit_cost": unit_cost})

    _write_product_report(
        ("\tNew " if is_new_svls else "\t") + _SVL_MESSAGE.format(svl=in_svl, uc_src=",".join(uc_src), p=precs),
        stock_move.product_id,
    )
    _write_product_report(
        ("\tNew " if is_new_svls else "\t") + _SVL_MESSAGE.format(svl=out_svl, uc_src=",".join(uc_src), p=precs),
        stock_move.product_id,
    )
    return svls


def compute_svl(stock_move, svl, valued_quantity):
    """
    Update / Create an SVL with correct value/quantity/unit_cost.
    This method does not impact other SVLs, aka it does not update the remaining datas.
    """
    if is_new_svl := not svl.exists():  # Create new SVL
        svl = create_svls(
            {
                "product_id": stock_move.product_id.id,
                "company_id": env.company.id,
                "description": stock_move.reference
                and "%s - %s" % (stock_move.reference, stock_move.product_id.name)
                or stock_move.product_id.name,
                "stock_move_id": stock_move.id,
                "account_move_id": stock_move.account_move_ids[0].id if stock_move.account_move_ids else None,
                "create_date": stock_move.date,
            }
        )

    svl.write({"quantity": valued_quantity})  # A correct quantity is needed for compute_unit_cost_and_value
    unit_cost, value, uc_src = compute_unit_cost_and_value(svl)

    if not is_new_svl:
        _write_svl_update_report(svl, valued_quantity, unit_cost, value)

    # Update value even if no difference is detected, rounding diff can still have an impact on global valuation
    svl.write({"value": value, "unit_cost": unit_cost})
    _write_product_report(
        ("\tNew " if is_new_svl else "\t") + _SVL_MESSAGE.format(svl=svl, uc_src=",".join(uc_src), p=precs),
        stock_move.product_id,
    )
    return svl


def compute_landed_cost(svl):
    """
    Create a Landed Cost layer linked to the layer in parameter.
    :return: Value of the Landed Cost or 0 if version not supported.
    """
    if (
        not model_exists("stock.valuation.adjustment.lines")
        or svl.product_id.cost_method == "standard"
        or not svl.stock_move_id._is_in()
    ):
        return 0

    total_additional_landed_cost_value = 0

    cost_adjustment_lines = env["stock.valuation.adjustment.lines"].search(
        [("move_id", "=", svl.stock_move_id.id), ("product_id", "=", svl.product_id.id), ("cost_id.state", "=", "done")]
    )
    for cost in cost_adjustment_lines:
        lc_svl = create_svls(
            {
                "value": cost.additional_landed_cost,
                "stock_move_id": cost.move_id.id,
                "account_move_id": cost.cost_id.account_move_id.id,
                "product_id": cost.product_id.id,
                "company_id": env.company.id,
                "description": cost.cost_id.name,
                "stock_landed_cost_id": cost.cost_id.id,
                "stock_valuation_layer_id": svl.id,
                "create_date": svl.create_date,
            }
        )
        total_additional_landed_cost_value += cost.additional_landed_cost
        svl.write({"remaining_value": svl.remaining_value + lc_svl.value})
        processed_svl_ids.append(lc_svl.id)
        _write_product_report("\t" + _LANDED_COST_MESSAGE.format(svl=lc_svl, p=precs), svl.product_id)
        _write_product_report(
            "\t\tNew " + _IN_REM_DATA_MESSAGE.format(svl=svl, rem_uc=get_remaining_unit_cost(svl), p=precs),
            svl.product_id,
        )

    return total_additional_landed_cost_value


def create_svls(data):
    """
    Create a layer based on data provided.
    Capable of setting the given create_date
    :return: stock.valuation.layer
    """
    if not data:
        return StockValuationLayer

    if not isinstance(data, list):
        data = [data]

    svls = StockValuationLayer.create(data)
    if "create_date" in data[0]:  # Set correct create_date
        env.cr.execute(
            "UPDATE stock_valuation_layer SET create_date = %s, write_date = %s WHERE id IN %s;",
            [data[0]["create_date"], data[0]["create_date"], tuple(svls.ids)],
        )
        if odoo_version >= 16:  # Refresh ORM cache
            svls.invalidate_recordset(["create_date", "write_date"])
        else:
            StockValuationLayer.invalidate_cache(["create_date", "write_date"], svls.ids)
    return svls


# END -- stock_valuation_layer.py --
# START -- main.py --
if force_clean_table:
    table_clean()
    raise_error("Table and index removed from the database!")

if show_db_products_logs:
    raise_error(log_context_header + get_summary() + "\n".join(get_logs_from_db()), raise_log)

if show_progress_status:
    raise_error(get_progress_report())

if restore_valuation:
    # Run main method
    table_init()

    if redo_done_products:
        clean_done_products()

    _env, ctx = env, env.context.copy()
    for company in specific_companies:
        # Create a new env for with the current company
        # We might need to set the remaining companies to avoid access errors
        # rem_companies = [cid for cid in _env.companies.ids if cid != company.id]
        ctx["allowed_company_ids"] = [company.id]
        env = _env(context=ctx)

        # Set the company on the models
        StockValuationLayer = StockValuationLayer.with_company(company)
        StockMove = StockMove.with_company(company)
        ProductProduct = ProductProduct.with_company(company)

        # Set the currency precision
        precs["vp"] = company.currency_id.decimal_places

        # Fix the products
        for p in get_products():  # use 'p' as variable name to prevent "Shadows name from outer scope" in IDE
            print(f"processing {p.id}[{p.default_code}]", file=sys.stderr)
            restore_product_valuation(p)
            env.clear()

    table_clean()
    raise_error(log_context_header + get_summary() + "\n".join(product_reports.values()), raise_log)

# END -- main.py --