import logging

_logger = logging.getLogger(__name__)


env = env  # noqa

# first rename materialized view if exists
env.cr.execute(
    """
    DROP MATERIALIZED VIEW IF EXISTS sale_line_product_cost_history CASCADE;
"""
)

# we've restored the original table product_price_history for the
# data prior to 2023-10-01  so we need to create a new materialized
# view to get the cost of a  product for a given sale order line
# for stock moves prior to the 2023-10-01 create materialized view if not exists
_logger.info("Create materialized view alc_sale_line_product_cost_history")
env.cr.execute(
    """
    CREATE MATERIALIZED VIEW IF NOT EXISTS alc_sale_line_product_cost_history AS (
        SELECT DISTINCT
            ON (sm.sale_line_id, sm.product_id) sm.sale_line_id,
            sm.product_id,
            sm.sale_line_id as id,
            pph.cost
        FROM
            stock_move sm
            LEFT JOIN LATERAL (
                SELECT
                    pph_1.cost
                FROM
                    product_price_history pph_1
                WHERE
                    sm.sale_line_id IS NOT NULL
                    AND sm.product_id = pph_1.product_id
                    AND sm.date >= pph_1.datetime::date
                    AND sm.date < '2023-10-01 00:00:00'::timestamp without time zone
                ORDER BY
                    pph_1.datetime DESC
                LIMIT
                    1
            ) pph ON true
        WHERE
            sm.sale_line_id IS NOT NULL
            AND sm.picking_type_id in (4,8) -- Retours Client et Livraison
            AND sm.date < '2023-10-01 00:00:00'::timestamp without time zone
            AND sm.state = 'done'
            AND sm.is_additional_move = false
    );

    create index if not exists alc_sale_line_product_cost_history_line_product_id_idx
    on alc_sale_line_product_cost_history(sale_line_id, product_id);
"""
)

# create a unfified view to get the cost of a product for a given sale order line
# whatever the date of the stock move
_logger.info("Create view sale_line_product_cost")
env.cr.execute(
    """
    CREATE OR REPLACE VIEW sale_line_product_cost AS (
        SELECT DISTINCT
    ON (sm.sale_line_id, sm.product_id) sm.sale_line_id,
    sm.product_id,
    CASE
        WHEN sm.date < '2023-10-01 00:00:00'::timestamp without time zone THEN pph.cost
        ELSE svl.unit_cost
    END AS unit_cost
FROM
    stock_move sm
    LEFT JOIN stock_valuation_layer svl ON svl.stock_move_id = sm.id AND svl.product_id = sm.product_id
    LEFT JOIN alc_sale_line_product_cost_history pph ON pph.sale_line_id = sm.sale_line_id and pph.product_id = sm.product_id
WHERE
    (
        svl.product_id IS NULL
        OR svl.product_id = sm.product_id
        AND svl.unit_cost IS NOT NULL
    )
    AND sm.sale_line_id IS NOT NULL
    AND (sm.picking_type_id in (4, 8))
);
    """
)

_logger.info("Add new columns to sale_order_line")
env.cr.execute(
    """
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS margin_delivered FLOAT;
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS margin_delivered_percent FLOAT;
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS purchase_price_delivery FLOAT;
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS margin FLOAT;
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS margin_percent FLOAT;
    ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS purchase_price FLOAT;
"""
)

_logger.info("Fill new columns in sale_order_line")
env.cr.execute(
    """
    UPDATE sale_order_line sol
    SET
        margin = sol.price_subtotal - (cost.unit_cost * sol.product_uom_qty),
        margin_percent = (sol.price_subtotal - (cost.unit_cost * sol.product_uom_qty) / NULLIF(sol.price_subtotal, 0),
        purchase_price = cost.unit_cost,
        margin_delivered = sol.price_subtotal - (cost.unit_cost * sol.qty_delivered),
        margin_delivered_percent = (sol.price_subtotal - (cost.unit_cost * sol.qty_delivered)) / NULLIF(sol.price_subtotal,0),
        purchase_price_delivery = cost.unit_cost
    FROM sale_line_product_cost cost
    WHERE
        sol.id = cost.sale_line_id
        and sol.product_id = cost.product_id
    """
)
_logger.info("%s sale order lines updated", env.cr.rowcount)

# add new columns to sale_order
_logger.info("Add new columns to sale_order")
env.cr.execute(
    """
    ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS margin FLOAT;
    ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS margin_percent FLOAT;
"""
)

_logger.info("Fill new columns in sale_order")
env.cr.execute(
    """
    UPDATE sale_order so
    SET
        margin = coalesce(sol.margin, 0),
        margin_percent = coalesce(sol.margin, 0) / NULLIF(so.amount_untaxed, 0)
    FROM
        (
            SELECT
                sol.order_id,
                avg(sol.margin) as margin
            FROM
                sale_order_line sol
            GROUP BY
                sol.order_id
        ) sol
    WHERE
        so.id = sol.order_id
    """
)

_logger.info("%s sale orders updated", env.cr.rowcount)
