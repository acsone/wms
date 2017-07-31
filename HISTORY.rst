.. :changelog:

Release History
---------------

Unreleased
++++++++++

**Features and Improvements**

**Bugfixes**

**Build**

**Documentation**


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
