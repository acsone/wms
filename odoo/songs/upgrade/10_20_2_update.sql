-- increase sequence to lower the priority of all supplierinfo without end date, bounded supplierinfo must come first
UPDATE product_supplierinfo SET sequence = 100 WHERE date_end IS NULL;
