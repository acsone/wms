import csv
import sys
from functools import lru_cache
from collections import defaultdict
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

env = env  # noqa


def log(s):
    print(s, file=sys.stderr)


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


def get_product_id(default_code):
    return product_id_by_default_code().get(default_code)


def load_values_from_csv(year: int, month: int):
    last_day_of_month = date(year, month, 1) + relativedelta(months=1, days=-1)
    ldm = last_day_of_month
    filename = f"{ldm.year:04d}{ldm.month:02d}{ldm.day:02d} stock.quant.csv"
    res = defaultdict(lambda: (0, 0))
    with open(filename, encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            default_code = row["default_code"] or None
            lot_name = row["lot_name"]
            if not lot_name or lot_name == "0":
                lot_name = None
            product_id = get_product_id(default_code)
            if not product_id:
                log(f"Product not found: {default_code}")
                continue
            quantity = row["quantity"]
            standard_price = row["standard_price"]
            value = row["value"]
            assert quantity, f"No quantity for product {default_code}"
            assert standard_price, f"No standard_price for product {default_code}"
            assert value, f"No value for product {default_code}"
            quantity = int(float(quantity.replace(",", "")))
            standard_price = float(standard_price)
            value = float(value)
            if quantity < 0:
                log(f"Negative quantity for product {default_code}: {quantity}")
            if standard_price < 0:
                log(
                    f"Negative standard_price for product {default_code}: {standard_price}"
                )
            if abs(value - (quantity * standard_price)) > 0.001:
                log(
                    f"Value mismatch for product {default_code}: {value} != {quantity} * {standard_price}"
                )
            prev_quantity, prev_value = res[product_id]
            res[product_id] = (prev_quantity + quantity, prev_value + value)
    for product_id, (quantity, value) in res.items():
        yield product_id, quantity, value


def main():
    # env.cr.execute("delete from stock_valuation_layer where product_id=%s", (product_id,))
    year, month = 2023, 9
    init_start_date = datetime(year, month, 1, 21, 58) + relativedelta(months=1, days=-1)
    for product_id, quantity, value in load_values_from_csv(year, month):
        #if product_id != 40049:
        #    continue
        if not quantity:
            continue
        env["stock.valuation.layer"].search([("product_id", "=", product_id)]).unlink()
        vals = {
            "create_date": init_start_date,
            "remaining_qty": quantity,
            "quantity": quantity,
            "remaining_value": max(0, value),
            "value": value,
            "unit_cost": round(value / quantity, 2),
            "product_id": product_id,
            "company_id": 1,
            "description": "Init valuation at 30/9/2023",
        }
        svls = env["stock.valuation.layer"].create(vals)
        env.cr.execute(
            "UPDATE stock_valuation_layer SET create_date = %s, write_date = %s WHERE id IN %s;",
            [vals["create_date"], vals["create_date"], tuple(svls.ids)],
        )
        svls.invalidate_recordset(["create_date", "write_date"])


if __name__ == "__main__":
    main()
