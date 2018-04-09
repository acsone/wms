## Banks and banks accounts

### Why there are two files (customer and supplier)
Bank accounts for supplier are stored in DB2. We extract these data directly
from DB2 with a script in the module DB2_export.
Bank accounts for customer are not stored in DB2 but in ASF. These data
can only be exported (Excel file) by a user in the company.

### Where come from the file res_bank_customer.csv
This a list of bank in Europe found on Internet.
