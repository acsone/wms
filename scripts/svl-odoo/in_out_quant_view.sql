DROP MATERIALIZED VIEW IF EXISTS tmp_quant_quantities;

CREATE MATERIALIZED VIEW tmp_quant_quantities AS
SELECT
    stock_quant.product_id AS product_id,
    stock_quant.lot_id AS lot_id,
    sum(
        ROUND(
            CAST(quantity AS NUMERIC),
            CAST(
                (
                    CASE
                        WHEN UOM_UOM.rounding = 1.0 THEN 0
                        ELSE LENGTH(CAST(UOM_UOM.rounding AS VARCHAR)) -2
                    END
                ) AS INT
            )
        )
    ) AS quantity
FROM
    stock_quant
    LEFT JOIN product_product AS PRODUCT_PRODUCT ON (stock_quant.product_id = PRODUCT_PRODUCT.id)
    LEFT JOIN product_template AS PRODUCT_TEMPLATE ON (
        PRODUCT_PRODUCT.product_tmpl_id = PRODUCT_TEMPLATE.id
    )
    LEFT JOIN uom_uom AS UOM_UOM ON (PRODUCT_TEMPLATE.uom_id = UOM_UOM.id)
    LEFT JOIN stock_location ON stock_location.id = stock_quant.location_id
WHERE
    stock_location.usage in ('internal', 'view')
GROUP BY
    stock_quant.product_id,
    stock_quant.lot_id;

CREATE INDEX CONCURRENTLY tmp_quant_quantities_idx ON tmp_quant_quantities (product_id, lot_id);

--
DROP MATERIALIZED VIEW IF EXISTS tmp_outgoing_sml_quantities;

CREATE MATERIALIZED VIEW tmp_outgoing_sml_quantities AS
SELECT
    SM1.product_id,
    SM1.lot_id,
    SUM(
        ROUND(
            CAST(
                - qty_done / UOM_UOM_ML.factor * UOM_UOM_PT.factor AS NUMERIC
            ),
            CAST(
                (
                    CASE
                        WHEN UOM_UOM_PT.rounding = 1.0 THEN 0
                        ELSE LENGTH(CAST(UOM_UOM_PT.rounding AS VARCHAR)) -2
                    END
                ) AS INT
            )
        )
    ) AS quantity
FROM
    stock_move_line AS SM1
    LEFT JOIN product_product AS PRODUCT_PRODUCT ON (SM1.product_id = PRODUCT_PRODUCT.id)
    LEFT JOIN product_template AS PRODUCT_TEMPLATE ON (
        PRODUCT_PRODUCT.product_tmpl_id = PRODUCT_TEMPLATE.id
    )
    LEFT JOIN uom_uom AS UOM_UOM_PT ON (PRODUCT_TEMPLATE.uom_id = UOM_UOM_PT.id)
    LEFT JOIN uom_uom AS UOM_UOM_ML ON (SM1.product_uom_id = UOM_UOM_ML.id)
    LEFT JOIN stock_location src_sl on src_sl.id = SM1.location_id
    LEFT JOIN stock_location dst_sl on dst_sl.id = SM1.location_dest_id
WHERE
    SM1.state = 'done'
    and src_sl.usage in ('internal', 'view')
    and dst_sl.usage not in ('internal', 'view')
GROUP BY
    SM1.product_id,
    SM1.lot_id;

CREATE INDEX CONCURRENTLY tmp_outgoing_sml_quantities_idx ON tmp_outgoing_sml_quantities (product_id, lot_id);

--
DROP MATERIALIZED VIEW IF EXISTS tmp_incoming_sml_quantities;

CREATE MATERIALIZED VIEW tmp_incoming_sml_quantities AS
SELECT
    SM1.product_id,
    SM1.lot_id,
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
        )
    ) AS quantity
FROM
    stock_move_line AS SM1
    LEFT JOIN product_product AS PRODUCT_PRODUCT ON (SM1.product_id = PRODUCT_PRODUCT.id)
    LEFT JOIN product_template AS PRODUCT_TEMPLATE ON (
        PRODUCT_PRODUCT.product_tmpl_id = PRODUCT_TEMPLATE.id
    )
    LEFT JOIN uom_uom AS UOM_UOM_PT ON (PRODUCT_TEMPLATE.uom_id = UOM_UOM_PT.id)
    LEFT JOIN uom_uom AS UOM_UOM_ML ON (SM1.product_uom_id = UOM_UOM_ML.id)
    LEFT JOIN stock_location src_sl on src_sl.id = SM1.location_id
    LEFT JOIN stock_location dst_sl on dst_sl.id = SM1.location_dest_id
WHERE
    SM1.state = 'done'
    and src_sl.usage not in ('internal', 'view')
    and dst_sl.usage in ('internal', 'view')
GROUP BY
    SM1.product_id,
    SM1.lot_id;

CREATE INDEX CONCURRENTLY tmp_incoming_sml_quantities_idx ON tmp_incoming_sml_quantities (product_id, lot_id);

-- tmp_sml_quantities
CREATE VIEW tmp_sml_quantities AS
select
    product_id,
    lot_id,
    sum(quantity) as quantity
from
    (
        select
            product_id,
            lot_id,
            quantity
        from
            tmp_outgoing_sml_quantities
        union
        all
        select
            product_id,
            lot_id,
            quantity
        from
            tmp_incoming_sml_quantities
    ) x
group by
    product_id,
    lot_id;

--- discrepancies by product and lot
select
    coalesce(qq.product_id, sq.product_id) as product_id,
    pt.default_code as product_code,
    coalesce(qq.lot_id, sq.lot_id) as lot_id,
    sl.name as lot_name,
    qq.quantity as quant_quantity,
    sq.quantity as sml_quantity
from
    tmp_quant_quantities as qq full
    join tmp_sml_quantities sq on (
        qq.product_id = sq.product_id
        and coalesce(qq.lot_id, 0) = coalesce(sq.lot_id, 0)
    )
    left join product_product pp on pp.id = coalesce(qq.product_id, sq.product_id)
    left join product_template pt on pt.id = pp.product_tmpl_id
    left join stock_lot sl on sl.id = coalesce(qq.lot_id, sq.lot_id)
where
    coalesce(qq.quantity, 0) != coalesce(sq.quantity, 0)
order by
    product_id,
    lot_id;

--- discrepancies by product
with tmp_quant_quantities_by_product as (
    select
        product_id,
        sum(quantity) as quantity
    from
        tmp_quant_quantities
    group by
        product_id
),
tmp_sml_quantities_by_product as (
    select
        product_id,
        sum(quantity) as quantity
    from
        tmp_sml_quantities
    group by
        product_id
)
select
    coalesce(qq.product_id, sq.product_id) as product_id,
    pt.default_code as product_code,
    qq.quantity as quant_quantity,
    sq.quantity as sml_quantity,
    coalesce(qq.quantity, 0) - coalesce(sq.quantity, 0) as delta
from
    tmp_quant_quantities_by_product as qq full
    join tmp_sml_quantities_by_product sq on (qq.product_id = sq.product_id)
    left join product_product pp on pp.id = coalesce(qq.product_id, sq.product_id)
    left join product_template pt on pt.id = pp.product_tmpl_id
where
    coalesce(qq.quantity, 0) != coalesce(sq.quantity, 0)
order by
    delta;
