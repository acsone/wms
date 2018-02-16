# DB2 options

The module `importer_db2` requires access to DB2 server to pull the data.

Here are the environment variables to set:

```
DB2USER: db2 role
DB2PWD: db2 password
DB2HOST: ip of db2 server or 'pissh'
```

If intramuros, you can use DB2HOST with the ip address of the server

PROD: 10.2.2.3
REPLICATE: 10.2.3.99

Otherwise from camptocamp platform you need to activate the pissh container with SSH key.
And set `DB2HOST=pissh`
