-- Put all product_template belgium_only to false

UPDATE product_template
    SET belgium_only = 'false'
    WHERE belgium_only = 'true';
