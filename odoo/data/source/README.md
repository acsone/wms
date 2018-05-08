## convert_fournisseur_utilisateur.py

### Why this script ?
ZelAppro contains a list of responsible for each supplier and
also the day when this supplier is managed.

To import this list in Odoo, we need to manually export a CSV file from Access
(ZelAppro use Access) and convert this file to a file understandable by Odoo.

### What type file must be exported from Access ?
You need to export the table "FOURNISSEUR_UTILISATEUR" with following parameter:
- File type: CSV
- File name: FOURNISSEUR_UTILISATEUR.csv
- Delimiter: ','
- Quote delimiter: '"'
- Encoding: UTF-8 (very important !!!)

Replace the existing file by your new file

### How to execute this script ?
Simply execute the "convert_fournisseur_utilisateur.py" file.
This script will generate a new file in ../install/supplier_add_data.csv

## Mandats.csv

### What is it ?
This file is exported by an employee directly from ASF and it contains
all mandats for customers.
