#!/usr/bin/env python
from contextlib import contextmanager

import click
import click_odoo
import psycopg2

DB_16_POSTMIG = "alcyon-16-migrated-by-odoo"

# Call the script with -d <destination db name>


@contextmanager
def cursor(db):
    with psycopg2.connect("dbname=" + db) as conn:
        with conn.cursor() as cr:
            yield cr


@click.command()
@click_odoo.env_options()
def main(env):
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            SELECT id, invoice_frequency
                FROM res_partner
                WHERE invoice_grouping = 'by_delivery';
        """
        cr.execute(query)
        partners_delivery = cr.fetchall()

        print(partners_delivery)
    id = (x[0] for x in partners_delivery)
    invoice_frequency = (x[1] for x in partners_delivery)

    # converting to list
    id = list(id)
    invoice_frequency = list(invoice_frequency)
    env.cr.execute(
        "SELECT UNNEST(%(id)s)::int, UNNEST(%(invoice_frequency)s)::VARCHAR AS t",
        {"id": id, "invoice_frequency": invoice_frequency},
    )
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
    env.cr.execute(query, {"id": id, "invoice_frequency": invoice_frequency})


if __name__ == "__main__":
    main()
