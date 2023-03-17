\set ON_ERROR_STOP

update
    stock_quant_package
set product_packaging_id = null
where
    product_packaging_id is not null
    and product_packaging_id not in (select id from product_packaging);
