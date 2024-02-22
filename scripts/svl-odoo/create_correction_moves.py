import csv
import sys
from collections import defaultdict
from datetime import date, datetime
from functools import lru_cache

from dateutil.relativedelta import relativedelta

from odoo import Command

env = env  # noqa


INVENTORY_LOC_NAME = "CORRECTION-IN-OUT"
INTERNAL_LOC_NAME = "CORRECTION-IN-OUT"


def load_quantities_from_excel(year: int, month: int):
    last_day_of_month = date(year, month, 1) + relativedelta(months=1, days=-1)
    ldm = last_day_of_month
    filename = f"{ldm.year:04d}{ldm.month:02d}{ldm.day:02d} stock.quant.csv"
    res = defaultdict(int)
    with open(filename, encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            default_code = row["default_code"] or None
            lot_name = row["lot_name"]
            if not lot_name or lot_name == "0":
                lot_name = None
            product_id, lot_id = get_product_id_lot_id(default_code, lot_name)
            if not product_id or (lot_name and not lot_id):
                log(f"Product/lot not found: {default_code} {lot_name}")
                continue
            key = (product_id, lot_id, default_code, lot_name)
            quantity = row["quantity"]
            assert quantity, f"No quantity for product {default_code} lot {lot_name}"
            quantity = int(float(quantity.replace(",", "")))
            res[key] += quantity
    return res


@lru_cache
def product_id_by_default_code():
    env.cr.execute(
        """
            SELECT pt.default_code, pp.id, pp.active
            FROM product_product pp
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            WHERE pt.default_code is not null
              and pt.default_code != ''
              and pt.detailed_type = 'product'
            ORDER BY active DESC
        """
    )
    multi = set()
    res = {}
    for row in env.cr.fetchall():
        default_code, product_id, active = row
        if default_code in res and active:
            # more than one active product with the same default_code
            res[default_code] = None
            multi.add(default_code)
        else:
            res[default_code] = product_id
    if multi:
        log(f"Products codes with multiple product.product: {multi}")
    return res


@lru_cache
def product_id_lot_id_by_default_code_and_lot_name():
    env.cr.execute(
        """
            SELECT pt.default_code, l.name, pp.id, l.id
            FROM stock_lot l
            LEFT JOIN product_product pp on pp.id = l.product_id
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            WHERE pt.default_code is not null
              and pt.default_code != ''
              and pt.detailed_type = 'product'
        """
    )
    rows = env.cr.fetchall()
    res = {(row[0], row[1]): (row[2], row[3]) for row in rows}
    assert len(res) == len(rows)
    return res


@lru_cache
def get_product_id_lot_id(default_code, lot_name):
    if not lot_name:
        return (product_id_by_default_code().get(default_code), None)
    return product_id_lot_id_by_default_code_and_lot_name().get(
        (default_code, lot_name), (None, None)
    )


def get_sml_quantities_by_default_code_and_lot_name(before: date):
    env.cr.execute(
        """
            SELECT
                pp.id as product_id,
                slt.id as lot_id,
                pt.default_code,
                slt.name as lot_name,
                SUM(
                    ROUND(
                        CAST(
                            qty_done / UOM_UOM_ML.factor * UOM_UOM_PT.factor AS NUMERIC
                        ),
                        CAST(
                            (
                                CASE
                                    WHEN UOM_UOM_PT.rounding = 1.0 THEN 0
                                    ELSE LENGTH(CAST(UOM_UOM_PT.rounding AS VARCHAR)) -2
                                END
                            ) AS INT
                        )
                    ) * (
                        CASE
                            WHEN src_sl.usage in ('internal', 'view') THEN -1
                            WHEN dst_sl.usage in ('internal', 'view') THEN 1
                            ELSE 0
                        END
                    )
                ) AS qty_done
            FROM
                stock_move_line AS sml
                LEFT JOIN product_product AS pp ON (sml.product_id = pp.id)
                LEFT JOIN product_template AS pt ON (pp.product_tmpl_id = pt.id)
                LEFT JOIN uom_uom AS UOM_UOM_PT ON (pt.uom_id = UOM_UOM_PT.id)
                LEFT JOIN uom_uom AS UOM_UOM_ML ON (sml.product_uom_id = UOM_UOM_ML.id)
                LEFT JOIN stock_lot AS slt ON slt.id = sml.lot_id
                LEFT JOIN stock_location src_sl on src_sl.id = sml.location_id
                LEFT JOIN stock_location dst_sl on dst_sl.id = sml.location_dest_id
            WHERE
                sml.state = 'done'
                and (
                    (
                        dst_sl.usage not in ('internal', 'view')
                        and src_sl.usage in ('internal', 'view')
                    )
                    or (
                        src_sl.usage not in ('internal', 'view')
                        and dst_sl.usage in ('internal', 'view')
                    )
                )
                and pt.detailed_type = 'product'
                and sml.date < %(before)s
                -- ignore move lines where the lot and the product don't correspond
                and (sml.lot_id is null or sml.product_id = slt.product_id)
            GROUP BY
                pp.id,
                slt.id,
                pt.default_code,
                slt.name
        """,
        {"before": before},
    )
    return {
        (product_id, lot_id, default_code, lot_name): quantity
        for product_id, lot_id, default_code, lot_name, quantity in env.cr.fetchall()
        if quantity != 0
    }


@lru_cache
def get_inventory_loc():
    res = env["stock.location"].search(
        [("usage", "=", "inventory"), ("name", "=", INVENTORY_LOC_NAME)]
    )
    assert len(res) == 1
    return res


@lru_cache
def get_internal_loc():
    res = env["stock.location"].search(
        [("usage", "=", "internal"), ("name", "=", INTERNAL_LOC_NAME)]
    )
    assert len(res) == 1
    return res


@lru_cache
def get_last_move_date(product_id, lot_id):
    where = "product_id = %(product_id)s"
    if lot_id:
        where += " AND lot_id = %(lot_id)s"
    else:
        where += " AND lot_id IS NULL"
    env.cr.execute(
        f"""
            SELECT date
            FROM stock_move_line
            WHERE {where}
            ORDER BY date DESC
            LIMIT 1
        """,
        {"product_id": product_id, "lot_id": lot_id},
    )
    res = env.cr.fetchone()
    if res:
        return res[0]
    return None


def create_correction_inventory_move(
    product_id, lot_id, quantity, year, month, correction_in_month
):
    """
    Create done inventory move without affecting the quants.

    Fool the system by setting the state to cancel to avoid any reservation or quant
    creation then write the state to done.

    qty > 0: create in move
    qty < 0: create out move
    """
    if quantity == 0:
        return
    elif quantity < 0:
        location = get_internal_loc()
        location_dest = get_inventory_loc()
    else:  # qty > 0
        location = get_inventory_loc()
        location_dest = get_internal_loc()

    product = env["product.product"].browse(product_id)

    end_of_month = datetime(year, month, 1) + relativedelta(months=1, hours=-3)

    last_move_date = get_last_move_date(product_id, lot_id)
    if not last_move_date or correction_in_month:
        # no move, set correction move at last day of month
        move_date = end_of_month
    else:
        move_date = min(end_of_month, last_move_date)

    move = env["stock.move"].create(
        {
            "state": "cancel",
            "name": "CORRECTION-IN-OUT",
            "date": move_date,
            "date_deadline": move_date,
            "company_id": 1,
            "product_id": product.id,
            "product_uom_qty": abs(quantity),
            "product_uom": product.uom_id.id,
            "location_id": location.id,
            "location_dest_id": location_dest.id,
            "procure_method": "make_to_stock",
            "is_inventory": True,
            "move_line_ids": [
                Command.create(
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "reserved_uom_qty": 0.0,
                        "qty_done": abs(quantity),
                        "lot_id": lot_id,
                        "date": move_date,
                        "location_id": location.id,
                        "location_dest_id": location_dest.id,
                        "date_planned": move_date,
                    },
                )
            ],
        }
    )
    move.state = "done"
    return move


def log(s):
    print(s, file=sys.stderr)


# year, month, correction_in_month
MONTHS = (
    (2023, 9, False),
    (2023, 10, True),
    (2023, 11, True),
    (2023, 12, True),
    (2024, 1, True),
)

product_id_by_default_code()
product_id_lot_id_by_default_code_and_lot_name()

for year, month, correction_in_month in MONTHS:
    log(f"processing {year}-{month:02d}")

    log("loading quant quantities from csv")
    quant_quantities = load_quantities_from_excel(year, month)
    log(f"{len(quant_quantities)} quant quantities")

    log("loading sml quantities from db")
    sml_quantities = get_sml_quantities_by_default_code_and_lot_name(
        before=date(year, month, 1) + relativedelta(months=1)
    )
    log(f"{len(sml_quantities)} sml quantities")

    for key in set(quant_quantities.keys()) | set(sml_quantities.keys()):
        product_id, lot_id, default_code, lot_name = key
        quant_quantity = quant_quantities.get(key, 0)
        sml_quantity = sml_quantities.get(key, 0)
        if quant_quantity != sml_quantity:
            delta = int(quant_quantity - sml_quantity)
            print(
                f"{product_id},[{default_code}],{lot_id},[{lot_name}],{delta},", end=""
            )
            create_correction_inventory_move(
                product_id=product_id,
                lot_id=lot_id,
                quantity=delta,
                year=year,
                month=month,
                correction_in_month=correction_in_month,
            )
            print("ok")
    log("commit")
    env.cr.commit()
