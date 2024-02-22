with quant_quantities as (
    select
        sq.product_id,
        pt.default_code,
        sum(sq.quantity) as quant_quantity,
        sum(
            ip.value_float * sq.quantity
        ) as quant_value
    from
        stock_quant sq
        left join stock_location sl on sl.id = sq.location_id
        left join product_product pp on pp.id = sq.product_id
        left join product_template pt on pt.id = pp.product_tmpl_id
        left join ir_property ip on (
            ip.res_id = 'product.product,' || sq.product_id
            and ip.name = 'standard_price'
        )
    where
        sl.usage in ('internal', 'view')
    group by
        sq.product_id,
        pt.default_code
),
svl_quantities as (
    select
        svl.product_id,
        pt.default_code,
        sum(svl.quantity) as svl_quantity,
        sum(svl.value) as svl_value
    from
        stock_valuation_layer svl
        left join product_product pp on pp.id = svl.product_id
        left join product_template pt on pt.id = pp.product_tmpl_id
    where
        true
    group by
        svl.product_id,
        pt.default_code
)
select
    coalesce(
        quant_quantities.product_id,
        svl_quantities.product_id
    ) as product_id,
    coalesce(
        quant_quantities.default_code,
        svl_quantities.default_code
    ) as product_code,
    quant_quantities.quant_quantity,
    quant_quantities.quant_value as quant_value,
    svl_quantities.svl_quantity,
    svl_quantities.svl_value as svl_value
from
    quant_quantities full
    join svl_quantities on quant_quantities.product_id = svl_quantities.product_id
where
    coalesce(quant_quantity, 0) != coalesce(svl_quantity, 0)
    or coalesce(quant_value, 0) != coalesce(svl_value, 0)