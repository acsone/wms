-- set origin_country_id based on the manufacturer origin
UPDATE product_template set intrastat_product_origin_country_id =
(select rp.country_id from res_partner as rp
where product_template.manufacturer = rp.id );
-- set origin_country_id based on the supplier origin if not ser before
UPDATE product_template set intrastat_product_origin_country_id =
(select rp.country_id from res_partner as rp
where product_template.supplier_id = rp.id ) where intrastat_product_origin_country_id is null;
-- set origin_country_id on invoice line
UPDATE account_invoice_line set intrastat_product_origin_country_id =
(select pt.intrastat_product_origin_country_id from product_template
as pt,product_product as pp where pp.product_tmpl_id = pt.id
and pp.id = account_invoice_line.product_id )
 where intrastat_product_origin_country_id is null and invoice_id in 
 (select id from account_invoice where date_invoice >= '2019-01-01');
