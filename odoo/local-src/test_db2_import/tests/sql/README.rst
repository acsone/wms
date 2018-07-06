To generate one of those sql files

doco run --rm -e DB_NAME=<db_name> odoo pg_dump --no-owner --inserts -a --table db2_<table> > db2_<table>.sql

Don't forget to cleanup the file
