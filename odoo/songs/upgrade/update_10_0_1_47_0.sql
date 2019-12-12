/*
This is what is asked for :
Check all the products with an empty vendor_product_code
For the empty ones, check the value of the supplier info records, if one 
is filled for the product code but others are not then fill the empty ones with the value
of the filled one.
Check ALCYN-2322

A dash in the product_code is treated like an empty value.
There is NO product_supplierinfo with a product_code set to an empty string

After this script there is 21 product with product_supplierinfo.product_code with 2 or
more distinct values that need to be handled by hand.
*/


UPDATE product_supplierinfo
    SET product_code = (
        SELECT DISTINCT(product_code) 
            FROM product_supplierinfo AS goodsupplierinfo 
            WHERE goodsupplierinfo.product_tmpl_id = tempdb.id
                  AND COALESCE(product_code, '-') <> '-')
    FROM (
            SELECT pt.id
                FROM product_template AS pt
                INNER JOIN product_supplierinfo AS psi ON pt.id = psi.product_tmpl_id
                WHERE (pt.vendor_product_code = '' OR pt.vendor_product_code IS NULL)
                GROUP BY pt.id, pt.name HAVING count(DISTINCT(coalesce(psi.product_code,'-'))) = 2
        ) tempdb
    WHERE product_supplierinfo.product_tmpl_id = tempdb.id
          AND COALESCE(product_supplierinfo.product_code, '-') = '-'
