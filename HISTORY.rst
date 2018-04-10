.. :changelog:

Release History
---------------

Unreleased
++++++++++

**Data Migration**

* ALCN-1224: set fiscal position to "Wholesaler without APB" to customer in category "Grossistes vétérinaires et Callcenter"


**Features and Improvements**

* Allow to send to scrap location at reception

**Bugfixes**

**Build**

* db2_import: get sale/purchase history from pre-generated csv files to limit number of querries to DB2

**Documentation**


10.18.7 (2018-04-25)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1183: Add and import from db2 call_name for customer and add nom_suite in view tree
* ALCN-1187: Add warning (in description and colored line) on sale order line when product out of stock at the supplier
* ALCN-1214: Add restriction rules on sale order lines
* ALCN-1216: Add quantity canceled on sale order line
* ALCN-1262: Add create helpdesk ticket from picking operation line
* ALCN-1273: Set the Zetes picking type on the picking type himselft and not on the picking
* Invoice: show description and comment if any. Add a column on the SO report to display the product code (to align with invoice display behavior). As there is a column with product code on the SO/invoice, do not put internal code prefix on the line description.

**Bugfixes**

* ALCN-1285: Fix crash on opening stock picking
* Fix rights on esbflux when managing promotions


10.18.6 (2018-04-18)
++++++++++++++++++++

**Build**

* Fix migration steps of 10.18.2
  Add missing update of res.bank.csv file
  Fix bank customer account and banking madate csv files
  by removing XXX on some xmlids to avoid mismatch and
  by removing mandates that links to unexisting bank account




10.18.5 (2018-04-18)
++++++++++++++++++++

**Build**

* Fix migration steps of 10.18.2
  Fix xmlids in bank csv data
  Deactivate VIES check on vat while reimporting supplier in full mode


10.18.4 (2018-04-17)
++++++++++++++++++++

**Build**

* Fix migration steps of 10.18.2
  miscalled step of import for banks data on full mode only

10.18.3 (2018-04-17)
++++++++++++++++++++

**Build**

* Fix migration steps of 10.18.2
  A module adding some field made the migration steps failed because of inconsistency between
  database schema and code.
  This is fixed by playing the migration steps after the update of the modules.


10.18.2 (2018-04-17)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1030: Add legal mention on fiscal position and display this mention on the invoice report
* ALCN-1167: Add the module specific_security to fit with Alcyon requirement (please read the attached document in module specific_security)
* ALCN-1173: Use a job to initialize and start esb connector
* ALCN-1241: Import a list of bank accounts for supplier (DB2) and customer (Generate from a Excel file)
* ALCN-1241: Import a list of banks (European Banks)
* ALCN-1241: Import a list of mandates
* ALCN-1243: Improve claim ticket creation, add link to picking, product, invoice; remove reference, add default values
* ALCN-1251: Add for customer the information if he will help with shipping fee and import data from db2
* ALCN-1253: Add Group, Subgroup and  Business Unit in XML product export (ws02)
* ALCN-1258: Configuration helpdesk (claims), add default Team, Reason, Stage
* ALCN-1259: Add new helpdesk button on account invoice
* ALCN-1268: Display the zetes state on picking and allow inventory manager to edit this value + search picking with or without an operator for zetes
* Configure product expiry delays
* Delivery Rounds: Load tags lundi,mardi,mercredi,jeudi,vendredi
* Small improvements: don't compute Business Rate when there is no business unit defined
* Small improvements: display a warning message when we cannot assign a round to a picking
* Small improvements: Remove the view kanban for products and change the display order for partners
* Stock reservation: Disable force availability

**Bugfixes**

* ALCN-1147: Set state to done for transfered internal transfer without any line processed
* ALCN-1167: Add some missing access rules to have a minimum access for all employees.
* ALCN-1261: Fix carrier_id and remove some fields in the data on create web sale order web service.
             For carrier_id use the esb_ref.
             Removed fields are : shipping_address_id, shipping_method, amount_total, amount_tax, amount_untaxed
* Delivery Rounds: Fix delivery round import itinerary
* Picking's delivery round cannot be propagated to backorder
* Logistics: Remove backorder popup at transfer. Manage properly reception, customer return and internal transfer for backorders. Do not manage claim at that stage
* Zetes tech data must not be propagated to backorder


**Build**

* db2_import: Remove last_date from db2_import
* db2_import: Do not auto update start_date and end_date on db2_import


10.18.1 (2018-04-05)
++++++++++++++++++++

**Bugfixes**

* Fix session on camptocamp platform due to change in Odoo core [1]


[1] https://github.com/odoo/odoo/pull/22612



10.18.0 (2018-03-29)
++++++++++++++++++++

**Data Migration**

* Update imported data on 2018-03-29
* ALCN-1065: Fix creation of backorders on sale import
* ALCN-1108: Remove mapping adaptation of tracking using serial type
* ALCN-1128: Set customer as company when having a legal entity defined
* ALCN-1155: import supplier categories, goods and general expenses
* ALCN-1205: import create_date on products
* ALCN-1234: Add name and date on history invoices on purchases

**Features and Improvements**

* ALCN-187: Modify templates for labels (add the checksum on package label)
* ALCN-760: Create the product category "Service" and modify the file accounting_product to add missing accounting service products
* ALCN-808: Add MTO/MTS procurement rules
* ALCN-1140: Add 2 missing fr_BE translations for module account_invoice_check_total
* ALCN-1236: Add user Limelogic
* ALCN-1247: Add Email node in pharmacy xml also when empty (wso2)
* ALCN-1249: Add user Smile
* Revert Belgium Taxes names and codes to v8 setup (before F.P. messed them all) + add missing Belgian standard taxes
* Allow to use numpad point in float numbers
* Add in Stock Valution Report last in/out dates for stock depreciation
* Launch import of 3 years of order on C2C_PLATFORM

**Bugfixes**

* ALCN-187: Fix the method to search the best picking (reserve and parking) with Zetes and uncomment the package label printing in domain print
* ALCN-1248: Fix both promotion changed on a product and only one is updated by connector (ws02)
* ALCN-1250: Fix bug creation helpdesk ticket and add automatic sequence in name field.
* Accounting: Fix invoice encoding, setup journal sequences (numbering per year or per month) and config, setup intrastat, configure fiscal positions for Alcyon accounts
* Add missing basic access rights on 2 models of the ESB connector
* Fix default_code import on inactive products

**Build**

* Update odoo/enterprise to latest commit
* Update odoo/src to latest commit
* Sync with project template


10.17.4 (2018-03-26)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1188: Move sale_channel field in the header of sale order
* ALCN-1203: Set is_business_unit on 2nd level categories
* ALCN-1215: Remove "Analytic tags" field from sale order line
* ALCN-1221: Change helpdesk ticket view, reordering field and replacing id with the name field.
* Delivery round: remove useless name sequence (TOUR/XXXX). Only use already existing complete_name
* Sale Consignement: Allow to make a SO for consignment. Goods are send to dedicated customer consignment location.


10.17.3 (2018-03-19)
++++++++++++++++++++

**Data Migration**

* Update min and max stock rules on products

**Features and Improvements**

* ALCN-1177: Set unique and automatic default_code on product
* ALCN-1192: Activate auto export of Pharmacy and Promotions Alcyon (wso2)
* ALCN-1194/ALCN-1193: Implement XML Action tag with Create Delete on product.supplierinfo (wso2)
* ALCN-1195: Do not export incomplete client addresses (wso2)
* ALCN-1202: Add accessories in product XLM (wso2)
* ALCN-1207: Add warning information on product category
    * On product category add multi language warning
    * On sale order confirmation add warning if category present
    * Add message in product xml (wso2)
* ALCN-1213: Set Reference field on Customer/Supplier to readonly
* ALCN-1218: Changes to a sale order line must activate the process of the sale order by the connector

**Bugfixes**

* ALCN-1228: Fix a bug with orderpoint on product template
* Delivery Rounds (Alcyon specific): add missing README and module auto install in migration.yml


10.17.2 (2018-03-12)
++++++++++++++++++++

**Data Migration**

* ALCN-1089 Automate initial stock inventory launch after transactional data import
* ALCN-1049: Setup routes on product based on locator informations

**Features and Improvements**

* ALCN-1200: Filter product in price XML (wso2)
        Export only of type product, for sale and with a Sku

* ALCN-1201: Change format of some fields in product xml (wso2).
    For five fields instead of 0/1 use False/True.
* ALCN-1199: Change esb_ref on Alcyon Group Id for customer and add some more (wso2)

* Accrual of returned products
* Data: Configure delivery round template on delivery carrier

* ALCN-1135: Add auto sequence on client ref field
* ALCN-1153: Set standard buying price in product cost field
* ALCN-161: Remove the module specific_zelapro and add the module code ABC (code extracted from zelapro)
* ALCN-161: Modify the procurement wizard to allow the user to select a specific day or a supplier
* ALCN-161: Add module stock_orderpoint_product
* ALCN-1069: Add import min/max
* ALCN-1204: Add Cp2z02 (fardelage) in product xml (wso2)
* ALCN-1208: Remove tags in product xml (wso2)
    Date péremption 1er lot (LotEch), Fractionnement (Cplz29), Déconditionnable (ges.cov)
* ALCN-161: Add module website_purchase_review

**Bugfixes**

* ALCN-1196: Repeat each promotion fo Alcyon Group Id >= 100 in special promotions XML (ws02)
* ALCN-1197: Change checksum calculation (use ids) for special promotions XML (wso2)
* ALCN-1150: Set minimum access rules for user roles
* ALCN-1154: Missing removal of discount_pricelist from purchase line in purchase report replaced by promotion_supplier
* Fix test on delivery rounds that was failing after 19h due to overlap on next day.
* ALCN-1166: Change checksum calculation for buyx gety xml (wso2)
* ALCN-1206: Filter product in stock XML (wso2)
    Export only product stockable, which are for sale and the Sku is defined

**Build**

* Change mailtrap host to smtp.mailtrap.io as mailtrap.io is now closed.


10.17.1 (2018-03-05)
++++++++++++++++++++

**Data Migration**

* ALCN-1109: Create partial receptions on imported in progress purchases
* ALCN-1109: Set invoiced quantities by creating an invoice on imported in progress purchases

**Bugfixes**

* Fix failing purchase db2 import missing a column for discount global


10.17.0 (2018-03-02)
++++++++++++++++++++

**Data Migration**

* ALCN-1016: Add inventory for products without lot.
* ALCN-1067: Improve Sale order import to set fiscal position and pricelist and limit the api calls.
* ALCN-1088: Change db2 import of sale order accessory products.
    Sale order line for product which are free and an additional product are not imported.
* ALCN-1105: Inverse imported value from DB2 of customer acceptance of backorder.
* ALCN-1112: Import unit of mesures on purchase orders from DB2.
* ALCN-1113: get discount_global from AS400 on purchase order lines.

**Features and Improvements**

* ALCN-136: Setup locations for scrap, return to supplier, return from customer.
* ALCN-1061: Set the default purchase tax.
* ALCN-1100: Set digits precision for product uom to 0.
* ALCN-1114: Performance: Product form view loading and sort order.
  (sort by internal reference and not by name otherwise the ORM creates
  a subselect on the translations in many requests)

**Bugfixes**

* ALCN-1141: Do the missing load of free products information of supplierinfo.
* ALCN-1145: The code on round itinerary must be required.

* ALCN-1163: Fix Error 500 in wso2 flux form Magento.
    Due to multiple line of tax on the sale order line.
    Also change the quantity used to compute the total.

* ALCN-1164: Fix generation error of the sale order report for NL customers.

* Delivery rounds: Do not allow to delete a started delivery round. Display a progress by picking zone.
* Fix reservation of expired product (migration to v10 issue).
* Fix expired product removal. Make one operation per expired quant location.

**Build**

* Update submodules


10.16.7 (2018-03-01)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1170: Change TaxCode in wso2 customer export
    0 is Belgium VAT number
    1 is no VAT number
    3 VAT number out of Belgium

**Bugfixes**

* ALCN-1152: Fix sale order report name bug, for client without reference
* ALCN-1156: Fix product price xml export, wong node name and type of export
    Change node <Root> in <Prix> and <Row> into <PriceInfo>
    Make the export not differential but always full
* ALCN-1157: WS02 Do no export pharmacist whose all clients are inactive


10.16.6 (2018-02-21)
++++++++++++++++++++

**Data Migration**

* Improve import_db2 dev tool to export SELECT query as csv file

**Features and Improvements**

* ALCN-864: Add an export of document zip to Magento
    Store in ir.attachment the order confirmation, invoice, credit note and
    a specific delivery note generated in a csv file.
    Export all documents generated during the day in a zip file to Magento
* ALCN-1119: Remove XML version node and ROOT node if no data present in XML export
* ALCN-1122: Add SerialNo implementation in customer export
* ALCN-1123: Remove unnecessary fields in customer export
    (MsrpSticker, BackorderEnable, plus empty fields)

**Bugfixes**

* ALCN-1106: Fix display alignment columns on sale order line detail form.
* ALCN-1118: Fix Customer Address export when esb_ref is empty
* ALCN-1119: Return empty string instead of False in XML export
* ALCN-1120: Change format IdRound in customer export
* ALCN-1121: Fix OnlinePayment and False in string values on customer export


10.16.5 (2018-02-16)
++++++++++++++++++++

**Features and Improvements**

* New temporary module stock_inventory_controller: Add a failsafe way to validate inventory logging errors.


10.16.4 (2018-02-16)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1094: Add default sftp directory in env variables
* Setup Cutoff Accrual - Do not make accrual of taxes

**Bugfixes**

* ALCN-1096: Change XML Promotions Alcyon
   * If both percent are zero do not include the entry
   * Add the promotions on all products contained in the price list.

* ALCN-1097: Fix XML Pharmacy, node e-mail contains False if email not referenced
   * Also fix that the XML nodes (fax, phone, city, zip) would contain False if
     their respective field is empty

* ALCN-1103: XML Customer Address, set AddressId for shipping to zero if it is not a specific address

**Build**

* ALCN-1087: Add option to select DB2HOST without using tunnel via rasberryPi
* ALCN-1087: Disable Camptocamp platform specifics by default
  plus add an opt-in with a new environment variable C2C_PLATFORM
* Generate invoices automatically every 10 days

**Documentation**

* Document new option to enable platform mode (by default disabled)
* Document DB2 options to connect importer to AS400 database


10.16.3 (2018-02-09)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1091 : Add product stock update through calls to WSO2 web service


10.16.2 (2018-02-08)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1093: Changes in Special Promotion XML export
   * Rename Percent in Percent1
   * Add Percent2 with fixed value zero
* ALCN-858: Add XML export to WSO2 for Buy X Get Y on products



10.16.1 (2018-02-06)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1092: Changes in Promotion Alcyon XML export
   * Rename Percent in Percent1
   * Add Percent2 with fixed value zero
* ALCN-1090: Financial Reporting by product category. Ensure cutoff entries are generated by product category.
* ALCN-1056: Add create, update sale_order call to WSO2 web service

**Bugfixes**

* ALCN-1085: Fix export PharmacyPrice in ProductPrice XML.
  * Make the method that update the related computed field called on all export not only cron jobs.

**Build**

* Upgrade nginx container to 1.2.1 - adding cache improvements


10.16.0 (2018-02-01)
++++++++++++++++++++

**Data Migration**

* Update imported data on 2018-01-31
* ALCN-933: Set default value to supplier backorder acceptance
* ALCN-978: Floor to 0 imported inventory quantities
* ALCN-1048: Import additional_products and quantities on product
* ALCN-1048: Import promotional products on supplier info
* ALCN-1081: Create channel to ease paralelization of import jobs
* ALCN-1081: Update queue branch and apply patch for retries
* ALCN-1064: Assign taxes on imported purchase order lines

**Features and Improvements**

* ALCN-859: ESB export special promotions
* ALCN-970: Stock Inventory Valuation
* ALCN-1039: Add esb_ref on deliver_carrier and update import data
* ALCN-1039: Add suite_name remove invoice_address_id on webservice sale order web
* ALCN-1050: Add the time limit of order on the partner
* ALCN-1054: Add tag OnlinePayment and change rule StatisticCode on customer xml export
* ALCN-1055: add last suite name on the partner
* ALCN-1057: Add IdRound in Customer XML export
* Enable discount on sale order lines
* Setup Cutoff Accrual

**Bugfixes**

* ALCN-1053 : Add change requested on customer adresses xml export
* Fix the method get_product_qty_unavailable in the module specific_sale (search stock.move whit a product)


10.15.2 (2018-01-23)
++++++++++++++++++++

**Features and Improvements**

* Reception screen priority computation optimization
* In reception wizard, allow to transfer. Process current operation before making transfer

**Bugfixes**

* GRN PO unlinking


10.15.1 (2018-01-23)
++++++++++++++++++++

**Features and Improvements**

* At reception, automatically assign operator when receiving + do not allow to receive more than the expected remaining quantity

**Bugfixes**

* Do not copy picking printed and operator_id field (important for backorder creation)
* Fix db2 importer songs setup failing on date computation


10.15.0 (2018-01-19)
++++++++++++++++++++

**Data Migration**

* Update imported data on 2018-01-19
* Fix import of sale order when assigning tax to last product line. The sequence was not respected.
* Fix creation of picking and match of lot by filtering by products
* ALCN-1038 Import product indicated price
* ALCN-1041 Import customer option to print sale price on their labels

**Features and Improvements**

* ALCN-1008: Raise an error when a user try to "deliver" a round with partially available pickings
* ALCN-1044: Add user authentication to webservices from connector_esb
* ALCN-898: Add the module sale_cancel_remaining
* ALCN-831: Remove blank in the invoice report
* ALCN-1037 Set ESF ref on product states data
* ALCN-187: Add the parking and reserve feature
* ALCN-869: Add webservice for a customer delivery fee
  * as of 19.01.18 customer wanted this webservice
    to always return a static message

**Bugfixes**

* ALCN-1047: Fix filter in statistics/form webservice
* ALCN-1045: Fix statistic webservice returning 500 error

**Build**

* BIZ-1093: Update odoo-cloud-platform

10.14.1 (2018-01-10)
++++++++++++++++++++

**Data Migration**

* Fix parallel import of supplierinfo csv by grouping entries by product template

10.14.0 (2018-01-10)
++++++++++++++++++++

**Data Migration**

* Update imported data on 2018-01-06
* ALCN-957 Import suite name on partners
* ALCN-986: Import standard price from AS400
* ALCN-1003: Adapt mapping of tracking to use serial type
* ALCN-1005: Fix active and default_code values on product.template copied from product.product
* ALCN-1040: Import passport requirement on customers from AS400
* ALCN-1042: Fix key in dict of values that made the import of purchases fail

**Features and Improvements**

* Removed obsolete modules
* ALCN-560: Default account per supplier on vendor bills
* ALCN-957 Add field suite name on partners
* ALCN-966: Merge same shipping (same partner) in the delivery report
* ALCN-974: Promotions (free extra product) and free accessories (free other product)
* ALCN-982: Add a picking zone on picking type, product and location
* ALCN-997: Rewrite entirely sale order line discounts
* ALCN-1006: Add field vet_subscription_number
* ALCN-1006: Import vet_subscription_number from AS400
* ALCN-1006: rename field depot_number to vet_depot_number
* ALCN-1006: rename field depot_number_visible to is_veterinary
* ALCN-1010: Don't display canceled picking when the view daily delivery rounds
* ALCN-1011: When the delivery address is used on a picking, search the itinerary with the company
* ALCN-1012: Add filters on round instances and round templates
* ALCN-1014: The user must first start the picking to validate after
* ALCN-1017: re-reserve stock when goods are put in stock (not only at reception)
* ALCN-1018: Display quants moved in the stock.move form view
* ALCN-1019: Fix mapping for country in Pharmacy export
* ALCN-1024: Fix wrong translation
* ALCN-1025: Add route for onorder to fridge, add routes for products, add routes per zone for nouveautés and achetés-vendus
* ALCN-1031: Add narcotic filter on sale report
* ALCN-1034: On product search, filter partner proposition with only suppliers
* ALCN-1035: Allow to import supplier info with CNK code to link product
* ALCN-1035: Improvements of supplier info list view
* ALCN-1035: Open supplier promotion in form with a button from editable list view
* ALCN-1035: Use purchase base price on supplier info onchange instead of list price
* Delivery rounds: when trying to set delivery round, only assign moves that are not yet assigned.
* Delivery rounds: when assigning moves, do not set again the delivery round if it is already part of it.
* Picking grouping: when cleaning operations, we really need to delete them before unreserving the moves.
* Picking grouping: at cancelation, before recomputing pack operation, we need to check if there are no other moves that could be reserved.

**Bugfixes**

* Stock: launch BO wizard for any reception + allow to generate BO even if no line processed
* ALCN-1033: Fix a bug when the shelf number is greater than 9

**Build**

* ALCN-1032:

 * Update project from odoo-template
 * Apply depreciation of demo in favor of sample
 * Clean empty data directories
 * Fix import_db2 scripts with sample data
 * Install base_technical_features and web_environment_ribbon modules
 * Upgrade docker-compose to 1.17.1

* Fix connector_esb tests with incorect relative delta

**Documentation**

* README of stock modules updated

**Build**

* Disable lang install on CI to reduce travis build time
* Remove unused PO files to reduce docker image size

10.13.0 (2017-11-30)
++++++++++++++++++++

**Features and Improvements**

* ALCN-982: Add a picking zone on picking type, product and location
* ALCN-994: Add smartbutton for helpdesk tickets on sale and purchase
* ALCN-997: Rewrite entirely sale order line discounts
* ALCN-999: Fix some small bugs with the module delivery_rounds
* ALCN-999: Fix some small bugs with the module delivery_rounds and add a cron to create delivery daily plan
* ALCN-1001: Don't copy the delivery round when we create a back order of a picking
* ALCN-1002: Move the field food_type to specific_zetes and rename it with is_portable_printer
* Stock: Enable internal transfer
* Allow to define a carrier having no round template and still group pickings

**Bugfixes**

* ALCN-988: Fix compute_price_rule in product price category module
* ALCN-991: Fix display of 'sale price 2' on product form view
* ALCN-1023: Fix email in imported users file
* ALCN-1026: Fix custom sale exceptions
* Delivery Round: stock move action_done: singleton expected error
* Fix delivery_rounds: generate plan wizard: fix execution date
* Fix zetes view inheritance, speed-up product zone computation
* Import DB2: Fix a bug with the location parser

**Build**

* ALCN-1028: Refresh all data (demo and full data)

**Documentation**

* Complete readme on modules
* Udpdate README for module specific_print and specific_purchase


10.12.1 (2017-11-17)
++++++++++++++++++++

**Build**

* Make attachment_s3 compatible with AWS


10.12.0 (2017-10-31)
++++++++++++++++++++

**Data Migration**

* ALCN-983: db2_importer module creates sale/purchase without tracking
* Add antibiotic contributions lines as sale order line taxes
* ALCN-967: add payment mode "Domiciliation" and do the mapping
* ALCN-973: add mapping for packaging quantities (box, pallet, shrink wrapping)
* ALCN-989: automatize hot DB2 data import for INT and PROD
* ALCN-981 - Set fridge route on product stocked in Q sector
* ALCN-161: Add the export ZelAppro "Stock" and improve exports
* Refresh cold data
* ALCN-918: Restore old mapping on promotion_pricelist_id to set it up on supplier_promotion_allowed as boolean
* ALCN-918: make sure sale order import will copy the value from partner_id.supplier_promotion_sale_allowed
* ALCN-918: Rewrite supplierinfo to include promotio
* ALCN-891: add mapping for delivery notes as comment on partner

**Features and Improvements**

* ALCN-946: Add tags on itinerary to easily target customers
* ALCN-705: Update labels and improve the way to print labels (add printer code)
* ALCN-980: Translate journal "Wage" and "Miscellaneous Operations" and remove duplicate journal
* ALCN-946: Add tags on itinerary to easily target customers
* ALCN-161: Add the export ZelAppro "Stock" and improve exports

**Bugfixes**

* There is no fridge product category. This is a route selectable on the product.
* Setup warehouse name, shorten picking type name (use warehouse code instead of name)
* Allow to select "Zone Médicament" logistic route on products.
* Allow to create a lot at reception with standard interface
* Fix new flake8 errors
* ALCN-979: Fix import from DB2 assignation of bin to products

**Build**

* Clean migration.yml file
* ALCN-985: Update all repositories
* ALCN-985: Install cloud_platform_exoscale module after update repositories
* ALCN-985: Add a pull request to (maybe) increase performance

**Documentation**

* ALCN-984: Update readme for import_db2 scripts (update ssh command line)
* DB2 Import - Improve module doc


10.11.0 (2017-10-13)
++++++++++++++++++++

**Bugfixes**

* Fix access righs product storage temperature
* Fix db2_importer for sales import
* Fix db2_importer tables xmlid
* Fix reception of products without lot
* Fix migration to v10: fix call to read that always returns a list since v10


10.10.0 (2017-10-02)
++++++++++++++++++++

**Data Migration**

* ALCN-972: Import delivery lead time on suppliers
* Set delivered and invoiced qty on sale order and purchase order which were imported and are in state done
* Extend db2_import module to import a subset of partner (10 by default) and their sale orders
* Adds 4 fields to product exported csv from DB2

  * product state, storage temperature, web published and barcode

* Update product categories with new categories

**Features and Improvements**

* [IMP] Do not group pickings when a specific carrier is defined on sales order
* ALCN-865: Web service create web sale order
* ALCN-965: Load payment terms
* ALCN-963: Update translations for the module specific_purchase
* [IMP] Re-reserve corresponding pickings in backorder when goods are received in stock

**Bugfixes**

* Issue github 305: Replace string replacement in logger.* functions
* ALCN-960: On picking form view, display 'Receive' button only for reception
* ALCN-966: Add product quantities in delivery report
* Add missing dependence on specific_sale module
* ALCN-961: Changes on delivery rounds

  * Replace sequence on picking by rank
  * Add smartbutton for picking/shipping in delivery round instance form view
  * Add a customer/rank list on delivery round instance

**Build**

* ALCN-959: Set esb_ref for some models
* Refresh data full and data demo
* ALCN-968: Update imported users file


10.9.0 (2017-09-15)
+++++++++++++++++++

**Data Migration**

* Extend db2_import module to import purchase orders

**Features and Improvements**

* ALCN-143: Remove useless sale_product_additional module
* [IMP] Don't overwrite the method action_confirm
* ALCN-940: Improve the delivery slip and set a new logistic option
* ALCN-881: Add the module specific followup to replace existing followup mails
* ALCN-941: Update the round delivery
* ALCN-964: Remove constrains on sequence
* [IMP] Disable tracking for sale order validation and improve the code to avoid to recompute quantities when it's not needed
* [IMP] Fix a bug with the travis.yml file
* ALCN-886 Add CNK code on products
* ALCN-911: Manage backorder with helpdesk

**Bugfixes**

**Build**

* Optimize complete build in migration.yml file
* Use module product_price_category from OCA instead of local sources
* Add a update of module stock in migration.yml to avoid to have an error of updating view


10.8.0 (2017-08-31)
+++++++++++++++++++

**Features and Improvements**

* ALCN-143: Manage additional product by bill of material
* Recompute pack operation properly at SO confirmation/cancelation

**Bugfixes**

* ALCN-187: Fix a bug with Zetes
* ALCN-945: On duplicate of sale order, confirmation date must not copied
* Fix missing mailtrap configuration
* At SO confirmation, do not recompute pack operation for each line
* Delivery round: stock reservation and assignment to delivery round

**Build**

* Update all repositories


10.7.0 (2017-08-25)
+++++++++++++++++++

**Data Migration**

* Reduce demo data size
* ALCN-735 Add delivery carrier on customers
* ALCN-674 Fix VAT import for customer and suppliers

**Features and Improvements**

* Reception/Picking: Hide some fields based on the context. Sequence must be asc. Prevent changing sequence for receive orders
* ALCN-187: Add missing depends and set the type of product
* Mark customers exported to ESB as such ('esb_exported' field)
* ALCN-161: Add the module specific_zelapro to manage daily Zelapro exports

**Bugfixes**

* Fix two mappings on client export esb
* Fix an error when when a product export file for ESB was generated for no products

10.6.1 (2017-08-22)
+++++++++++++++++++

**Bugfixes**

* Fix table creation with VARCHAR for DB2 data

10.6.0 (2017-08-04)
+++++++++++++++++++

**Features and Improvements**

* ALCN-33: Module to import Sale orders


10.5.0 (2017-07-31)
+++++++++++++++++++

**Data Migration**

* Update all data files
* ALCN-934: Add import for bin, inventory and lot (full mode)

**Features and Improvements**

* ALCN-756: Add the module [MIG][10.0]account_cutoff_accrual_picking, for testing purpose
* ALCN-796: Use the available quantity on product for the reception wizard
* ALCN-856 ESB export of stock
* ALCN-857: Add esb export price
* ALCN-860: Add esb export of promotions Alcyon
* ALCN-863: ESB export of customer and customer addresses
* ALCN-866: Add webservice for a product a client yearly purchase statistics
* ALCN-867: Add webservice for customer yearly statistics
* ALCN-868: Add webservice returning statistics for a customer
  according to parameters passed using a form
* ALCN-870: Add webservice for obtaining stock level for products in connector_esb
* ALCN-909 Rename Delivery Rounds models and load new delivery rounds setup
* ALCN-913: Add the unique supplier on the product form
* ALCN-916: Manage supplier promotion
* ALCN-917: Add a month filter on account invoice report
* ALCN-922: Add the module purchase_cancel_reason
* ALCN-923: Send an email when a purchase order is canceled
* ALCN-924: Add a view to manage supplier promotions
* ALCN-926 Install module Specific Data and remove references to __setup__
* Create an user with login WSO2 to allow Smile to use restricted controllers
* IMP: Add the module web_sheet_full_width

**Bugfixes**

* ALCN-929: Fix sale order report inherit
* Sales Priority: First ordered, is first served

**Build**

* Clean migration.yml because we reset integration instance


10.4.0 (2017-07-10)
+++++++++++++++++++

**Data Migration**

* ALCN-33 Sale order (demo only)
* ALCN-721 Customer addresses (demo only)
* ALCN-912: Import sale orders (demo data) on mode full

**Features and Improvements**

* ALCN-187: Add the indicated price on product
* ALCN-187: Add the new module specific_print to manage labels printing
* ALCN-187: Add the new module specific_zetes to manage the voice picker (read the README for more information about this module)
* ALCN-187: Fix a bug with the test test_1_picking_transfer
* ALCN-187: Retrieve the checksum on lot according the day of week
* ALCN-187: Update the deliveryslip report and add the passport report
* ALCN-838: Compute the scheduled date on the lead time of the supplier info
* ALCN-840: Add a cron to create the daily inventory
* ALCN-873: If no exception, hide exception group in sale order form view
* ALCN-885: Add a month filter on sale report
* ALCN-887: Hide confirmed sale order to quotation view
* ALCN-889: Add purchase manager on partner and as follower on helpdesk
* ALCN-890: Add sale order and purchase order fields on helpdesk ticket
* ALCN-892: Custom reference field on helpdesk ticket
* ALCN-900: Add helpdesk ticket smartbutton on partner form view
* ALCN-900: Hide potential smartbutton on product template form view
* ALCN-902: Redefine picking on helpdesk ticket with the reference field
* ALCN-903: Auto-fill fields when create helpdesk ticket from picking
* ALCN-904: Custom purchase report (add new measures)
* Setup song: do not reset admin pwd for devs

**Bugfixes**

* ALCN-888: Fix add a sale order line into a confirmed sale order
* ALCN-901: Fix 'Add partner vendor on follower when create helpdesk ticket'
* HOTFIX: Fix a bug when a purchase order line doesn't have a product
* HOTFIX: Fix a bug when a sale order line is not linked to a product

**Build**

* Add a ssh tunnel container for developpment
* Remove override of anthem/marabunta version to use the default version of docker-odoo-project
* TMP use `enterprise` from c2c
* Update OCA repositories to latest commits, rebuild pending-merges
* Update odoo/enterprise to latest commit
* Update odoo/src to latest commit
* Upgrade Docker image to 10.0-2.3.0
* Upgrade server-tools repository


10.3.0 (2017-06-15)
+++++++++++++++++++

**Data Migration**

**Features and Improvements**

* ALCN-551: Add the module account_credit_control
* ALCN-820: Add specific module to shipping costs calculation
* ALCN-823: Add the module "specific_purchase"
* ALCN-831: Version 2 of the invoice report
* ALCN-832: Import new account type
* ALCN-833: Update chart of accounts (add account 0 and 8)
* ALCN-836: Add 'Sale Order Lines Unavailable' menu in Sales > Report
* ALCN-837: Allow to define a delivery round on delivery carrier
* ALCN-844: Add field Reference to helpdesk ticket
* ALCN-845: Install modules Helpdesk and Specific Helpdesk (Ticket Reason)
* ALCN-847: Add CNK field to product template
* ALCN-849: Add smart button to link stock.picking to helpdesk.ticket
* ALCN-850: Add partner vendor on follower when create helpdesk ticket
* ALCN-854: Add a responsible on purchase order

**Bugfixes**

* Migration to v10

  * ALCN-852: Fix activation of sales prices based formula

**Build**

* Update to docker image 10.0-2.2.0
* Update project from odoo-template
* Update cloud platform addons to use Redis Sentinel in session_redis


10.2.0 (2017-05-19)
+++++++++++++++++++

**Features and Improvements**

* ALCN-641: Custom sale order report
* ALCN-824: Add a custom sale order line exception

**Bugfixes**

* ALCN-828: Fix product compute price on sale order with pricelist
* ALCN-830: Fix sale product additional module (onchange function)
* ALCN-835: Fix discount with sale product additional module
* Fix sale_exception Singleton errors (on constraint and on action confirm)


10.1.1 (2017-05-08)
+++++++++++++++++++

**Bugfixes**

* Upgrade base image
  Fixes security vulnerability CVE-2017-8291


10.1.0 (2017-05-05)
+++++++++++++++++++

**Data Migration**

**Features and Improvements**

* ALCN-673: Fix some bugs on report due to v10 migration and add line on report invoice
* ALCN-740: Add tools to integrate a voice picking (Zetes) in Odoo
* ALCN-788: Set the reference with the supplier invoice number
* ALCN-794: Set the flag "update_posted" on several journals and set the field check total required on vendor bills.
* ALCN-817 / 821: Add logistics informations in sale order form view
* Logistics: Reception: fix set default lot name with date, added some help, reception wizard (added button to allow to move to next destination)

**Bugfixes**

* ALCN-810: Allow to receive a lot that already exist: change reception picking type to use existing lot instead of create new lot
* ALCN-812: Add missing ir.model.access
* Delivery rounds: Fix delivery in case of lot
* Sales order confirmation if no stock: fix move assignment in case of no quant available

**Build**

* Migration to v10

  * ALCN-813: Fix putaway, must always return id and not recordset
  * ALCN-822: Fix import with 'from openerp...' and fix migration of specific_report


10.0.0 (2017-03-24)
+++++++++++++++++++

**Build**

* Migration to v10

  * Fix technically migration

    * Fix submodules versions for migration v10
    * Disable l10_be_* (not migrate in v10 again) dependences on specific_account module
    * Temporary deactivate displaying of fields on company view in V10
    * Temporary deactivate displaying of field on invoice view in V10
    * Fix nginx version for migration v10
    * Temporary deactivate accounting product import in V10
    * Fix travis script with odoo V10
    * Cancel auto-installing of procurement_jit

  * ALCN-770: Update data, adapt taxes and fix multi process update
  * ALCN-779: Sale modules migration to v10
  * ALCN-777: sale_exception module migration to v10
  * ALCN-795: Migrate import accounting products (replace xml id for account)
  * Stock modules migration to v10 + reception unit test


9.11.0 (2017-03-10)
+++++++++++++++++++

**Data Migration**

* standardize all xmlid replacing remaining 'scenario' by
  __setup__ for data created once and __import__ for data generated
  by import script
* Import MTO and MTS routes on products
* ALCN-704: Add control code on locations
* ALCN-713: Add new journals
* ALCN-722: Add product price and vendor code
* ALCN-758: Add new chart of account
* ALCN-760: Add accounting products
* ALCN-785: Change the default account for the tax "	Frais de voiture - TVA 50% Non Deductible"
* ALCN-786: Import account analytic tag
* ALCN-787: Import account analytic account

**Features and Improvements**

* Add the report delivery slip
* Improve the report invoice
* Add the delivery round report
* Rewriting sale_product_additional module
* Logistics: Add Parking for Aliments and routing
* ALCN-229: Add new journals, new chart of accounts and new products
* ALCN-723: Check if the removal date is expired when we receive goods
* ALCN-739: Show the column "End of Life Date" only for picking IN. Improve reception useability by adding a new reception wizard.
* ALCN-741: Add check of rule exception on sale order line
* ALCN-742: Add custom back order informations on sale order
* ALCN-761: Add a new menuitem to access to analytic tags
* ALCN-762: Activate by default the flag "Check Total on Vendor Bills"
* ALCN-763: Add new repo account-analytic and install the module account_analytic_required
* ALCN-768: Activate the module account_banking_sepa_credit_transfer

**Bugfixes**

* Fix sale order line amount computation on pricelist_discount module
* ALCN-701: Move tracking of lot under sheet instead of inside sheet
* ALCN-769: Fix a bug when an user try to duplicate a supplier invoice
* ALCN-772: Fix compute sale price 2 on product template


9.10.0 (2017-02-23)
+++++++++++++++++++

**Features and Improvements**

* ALCN-741: Add check of rule exception on sale order line
* Logistics: restored routing and added routing for MTO
* Logistics: parking for frigo, materiel + related putaway strat + rangement + demo data
* Logistics: picking of human products
* Logistics: rangement/reassort priorities

**Bugfixes**

* stock_refill: improve the way to compute available qty in bins
  in order to optimize it and being able to do the computation on
  thousands of locations

**Build**

* Move to new test platform
* Upgrade attachment_s3
* Remove letsencrypt test container
* Create a minion at the end of the build


9.9.0 (2017-02-09)
++++++++++++++++++

**Data Migration**

* Defer parent computation for all locations
* Paralelize full data import for locations
* Disable tracking messages for products and partners
* Fix duplicated locations in full data
* Remove loading of chariots location in full data (wrongly added)
* Do product import before location import to avoid a bug leading to OOM

**Features and Improvements**

* Add the module account_invoice_check_total from OCA repo account-invoicing
* ALCN-620: Change the wizard "Update quantity by hand" due to a wrong developpment
* ALCN-731: Compute a checksum on the lot according some rules
* ALCN-739: Show the column "End of Life Date" only for picking IN
* ALCN-723: Check if the removal date is expired when we receive goods

**Build**

* Rewrite part of import script to split csv files in maximum 500 lines


9.8.2 (2017-01-24)
++++++++++++++++++

**Bugfixes**

* Fix location import typo with extra parameter context


9.8.1 (2017-01-23)
++++++++++++++++++

**Data Migration**

* ALCN-707: Import fiscal position on customers
* ALCN-704: Import stock locations A, G, Q, P and E
* ALCN-77: Create product categories and set them on products
* ALCN-77: Remove putaway strategy
* ALCN-77: Standardize xmlids in logistics to __setup__ and __import__


9.8.0 (2017-01-23)
++++++++++++++++++

**Features and Improvements**

* ALCN-38: Upgrade account-financial-tools and l10n-belgium repositories
* ALCN-175: Stock locations
* ALCN-179: Stock reception priorities
* ALCN-180: Stock arrangement and priorities
* ALCN-252: Traceability
* ALCN-269: Stock reserves and reassortment priorities
* ALCN-621: Force the lot for the wizard update quantity
* ALCN-622: Add three checksum bin on the stock location
* ALCN-669: Add the module stock_picking_assignment to assign a picking
* ALCN-701: Add tracking for all date on lot
* ALCN-708: Add the report intrastat
* ALCN-711: Set "VIES VAT check" on the company by default
* ALCN-710: Add the structured communication on supplier invoice
* ALCN-712: Add a flag on the sequence to use the end date of the range to compute prefix with range
* ALCN-717: Add the module refund_invoice. This module allows to create customer/supplier refunds
* ALCN-718: Add the module account_banking_sepa_direct_debit from the repo bank-payment (OCA)

**Build**

* Change merge policy for git merge on HISTORY.rst
* Improve travis build by speeding up submodule download
  from GitHub zip archives
* Update odoo-cloud-platform
* Use redis integration on test instance
* Upgrade anthem version to 0.6.0

**Documentation**


9.7.1 (2017-01-13)
++++++++++++++++++

**Bugfixes**

* ALCN-623: Manage stock quants expiration (Fix unit tests)


9.7.0 (2017-01-13)
++++++++++++++++++

**Data Migration**

**Features and Improvements**

* Change admin password at the end of setup
* ALCN-623: Manage stock quants expiration
* ALCN-624: Manage stock production lot expired dates
* ALCN-668: Move internal reference field on partner form view
* ALCN-672: Add sale prices on products tree view
* ALCN-677: Specific manage stock production lot expired dates

**Bugfixes**

* Force nginx sidekick to use ipv4
* Add openoffice temp files to gitignore

**Build**

* Transfer Rancher templates
* Pin latest to integration server
* Skip missing rancher files
* Store let's encrypt certs in a named volume


9.6.5 (2016-12-13)
++++++++++++++++++

**Bugfixes**

* Upgrade version of submodule odoo-cloud-platform (for fix)


9.6.4 (2016-12-13)
++++++++++++++++++

**Bugfixes**

* Upgrade version of submodule odoo-cloud-platform (for fix)


9.6.3 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Undo Rollback: Importer script to parallelize import of big csv file.


9.6.2 (2016-12-12)
++++++++++++++++++

**Build**

* Move integration db on cluster postgres


9.6.1 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Rollback: Importer script to parallelize import of big csv file.


9.6.0 (2016-12-12)
++++++++++++++++++

**Data Migration**

* [ALCN-674] Import VAT on customers
* [ALCN-675] Import product taxes
* [ALCN-676] Don't remove archived product in full data on import

**Features and Improvements**

* Change default config for default invoice

**Build**

* Use camptocamp/odoo-project:9.0-1.7.1
* Rancher stacks: nginx sidekicks, letsencrypt, db_maxconn


9.5.1 (2016-11-28)
++++++++++++++++++

**Build**

* Fix cloud platform installation

9.5.0 (2016-11-25)
++++++++++++++++++

**Data Migration**

* ALCN-637: Import pharmacist id in customer.
* ALCN-638: Customer active flag.
* ALCN-639: Import product tracking configuration.
* ALCN-243: Invoice report (work in progress)

**Features and Improvements**

* ALCN-635: Remove domain from pharmacist field on customer.
* ALCN-645: Display 'Accounting Entries' menu for Accountants
* ALCN-625: Configure mailtrap for test/integration server.
* Activation of l10n_be
* Reception workflow.

**Bugfixes**

* ALCN-646: Fix install data of account journal

**Build**

* Migrate on Odoo cloud platform.

**Documentation**

* Fix DB2 import Readme.


9.4.1 (2016-11-10)
++++++++++++++++++

**Data Migration**

* Fix partner title mapping.

9.4.0 (2016-11-10)
++++++++++++++++++

**Data Migration**

* ALCN-640: Customer categories.
* ALCN-605: Customer title and legal entity.
* ALCN-634: Customer & supplier lang

**Features and Improvements**

* ALCN-22: Custom display product sale prices on template/pricelist form views
* ALCN-132: Add sale_exception module and add rules into it
* ALCN-262: Install warning module
* ALCN-601: Adds additional products on product template which used on sale order
* ALCN-642: Add city filter on partner tree/kanban views
* ALCN-635: Add associated pharmacist in customer form.
* ALCN-631 & ALCN-624: Install module l10n_be_intrastat (and report_instrastat by dependency)
* ALCN-618: Customer reference for sale order is no more required.
* ALCN-633: Depot number for veterinary.
* ALCN-634: Enable german language.

**Bugfixes**

* Pricelist discount: Fixing bugs when discount manually filled.

9.3.0 (2016-10-28)
++++++++++++++++++

**Data Migration**

* Customer pricelists
* Import partners phone, fax, mobile, email.
* Bank account & bank creation.
* Users creation.
* Import pricelists.

**Features and Improvements**

* Accounting configuration.
* Adapt chart of account.
* Enable pricelist report even if no variants.
* Fix company information.

9.2.1 (2016-10-14)
++++++++++++++++++

**Data Migration**

* Import full AS400 data for integration (product/partner)
* Importer script to parallelize import of big csv file.
* Demo data for delivery rounds

**Bugfixes**

* Multiple fixes in delivery rounds.
* Pricelist discount: Hide standard discount field instead of replace (in case someone used it)

9.2.0 (2016-09-29)
++++++++++++++++++

**Features and Improvements**

* Supplier promotion and Alcyon discount.
* Add price category in product which can be used in pricelist.
* Add Alcyon Category in partner.
* Add Medical Device boolean in product.
* Add sale channel field in sale order.
* Improve delivery rounds.
* Update demo csv files with AS400 imported data

**Build**

* Extend the server timeout of HAProxy on Rancher to 6h to align with the nginx
  option (we can have very long requests on Odoo!)
* Now using the new migration stack (anthem and marabunta), oerpscenario is
  deprecated
* Improve the documentation, including a page on the new stack
* Upgrade docker-odoo-project to 1.5.0


9.1.0 (2016-07-11)
++++++++++++++++++

Jira's Sprint 2.

**Features and Improvements**

* Add first version of the addon for the delivery rounds (``delivery_rounds``)
* Add a local module that adds a subcode on pickings
  (``stock_picking_subcode``)
* Add data for logistics and products


**Build**

* Setup Rancher for the test and integration servers
* Use docker compose files v2
* Fix .dockerignore, reducing size of roughly 2GB

9.0.0 (2016-06-01)
++++++++++++++++++

This is the first iteration of the project which corresponds to the Sprint 0,
this is why the version is `9.0.0` (`9` meaning that it is based on Odoo 9.0).

**Features and Improvements**

* Add base scenario with base data (company address, logo, languages, ...)

**Bugfixes**

**Build**

* Add the private Odoo enterprise repository in the submodules

**Documentation**

* Improve project's documentation (Docker, submodules, processes)


Creation of the project (2016-05-09)
++++++++++++++++++++++++++++++++++++

Bootstrap of the project with the Docker template.

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

.. Template:
