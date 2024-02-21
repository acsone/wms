copy(
    select svl.create_date as svl_create_date,
        sm.date as sm_date,
        sm.price_unit as sm_price_unit,
        sm.quantity_done as sm_quantity,
        svl.value as svl_value,
        svl.quantity as svl_quantity,
        svl.remaining_qty as svl_remaining_qty,
        svl.description as svl_description,
        src_sl.usage as src_usage,
        dst_sl.usage as dst_usage,
        src_sl.name as src_name,
        dst_sl.name as dst_name,
        case
            when (
                src_sl.usage in ('internal', 'view')
                and dst_sl.usage not in ('internal', 'view')
            ) then 'out'
            when (
                src_sl.usage not in ('internal', 'view')
                and dst_sl.usage in ('internal', 'view')
            ) then 'in'
            else 'internal'
        end as direction
    from stock_move sm
        left join stock_location src_sl on src_sl.id = sm.location_id
        left join stock_location dst_sl on dst_sl.id = sm.location_dest_id
        left join stock_picking_type spt on spt.id = sm.picking_type_id
        full join stock_valuation_layer svl on sm.id = svl.stock_move_id
    where sm.product_id = 7653

        or svl.product_id = 7653
    order by coalesce(sm.date, svl.create_date)
) to stdout csv header