/*
Stock valuation from quants at last purchase price.

Author: JEB
*/
copy (
    with stock as (
        select
            product_id,
            sum(quantity) as qty
        from
            stock_quant
            left join stock_location on stock_quant.location_id = stock_location.id
        where
            stock_location.usage = 'internal'
        group by
            product_id
    )
    select
        product_product.default_code,
        product_template.name->>'en_US' as product_name,
        stock.qty,
        coalesce(dpa.cost, 0) as dpa,
        coalesce(dpa.cost, 0) * stock.qty as value_dpa
    from
        stock
        left join product_product on stock.product_id = product_product.id
        left join product_template on product_product.product_tmpl_id = product_template.id
        left join lateral (
            select
                distinct on (purchase_order_line.product_id) round(purchase_order_line.price_subtotal / purchase_order_line.product_qty,2) as cost
            from
                purchase_order_line
                left join purchase_order on purchase_order_line.order_id = purchase_order.id
            where
                purchase_order_line.product_id = stock.product_id
                and purchase_order.state in ('purchase', 'done')
                and purchase_order_line.product_qty != 0
            order by
                purchase_order_line.product_id,
                date_order desc
        ) as dpa on true
) TO STDOUT CSV HEADER;
