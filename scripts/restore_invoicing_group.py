#!/usr/bin/env python
import csv

import click
import click_odoo
from openupgradelib import openupgrade

# Call the script with -d <destination db name>


@click.command()
@click_odoo.env_options()
def main(env):
    id = []
    invoice_frequency = []
    with open("./partners_delivery.csv") as partners_delivery_csv:
        csv_reader = csv.reader(partners_delivery_csv, delimiter=";")
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
                continue
            id.append(row[0])
            invoice_frequency.append(row[1])
            i += 1

    query = """
        WITH partners_delivery AS (
            SELECT UNNEST(%(id)s)::int id, UNNEST(%(invoice_frequency)s)::VARCHAR invoice_frequency
        )
        UPDATE res_partner rp
            SET invoicing_mode =
                CASE
                    WHEN partners_delivery.invoice_frequency = '10_days' THEN 'ten_days'
                    WHEN partners_delivery.invoice_frequency = '14_days' THEN 'fourteen_days'
                    WHEN partners_delivery.invoice_frequency = '1_month' THEN 'monthly'
                END,
            one_invoice_per_shipping = True
            FROM (select id, invoice_frequency FROM partners_delivery) as partners_delivery
            WHERE rp.id = partners_delivery.id;
        WITH partners_delivery AS (
            SELECT UNNEST(%(id)s)::int id, UNNEST(%(invoice_frequency)s)::VARCHAR invoice_frequency
        )
        UPDATE sale_order so
            SET invoicing_mode =
                CASE
                    WHEN partners_delivery.invoice_frequency = '10_days' THEN 'ten_days'
                    WHEN partners_delivery.invoice_frequency = '14_days' THEN 'fourteen_days'
                    WHEN partners_delivery.invoice_frequency = '1_month' THEN 'monthly'
                END,
            one_invoice_per_shipping = True
            FROM (select id, invoice_frequency FROM partners_delivery) as partners_delivery
            WHERE so.partner_invoice_id = partners_delivery.id
            ;
    """
    openupgrade.logged_query(
        env.cr, query, {"id": id, "invoice_frequency": invoice_frequency}
    )


if __name__ == "__main__":
    main()
