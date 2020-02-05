.. :changelog:

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

Release History
---------------

latest (unreleased)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* ALCYN-2366: fix delivered qty assigned to consignment location
* ALCYN-2364:Fix to add delivery fees on the SO before creating the invoice

**Build**

**Documentation**


10.0.1.47.3 (2020-01-29)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2401: hotfix: remove the locking introduced in ALCYN-2266 (causes deadlocks)
* update queue_job to remove the errors about missing field removal_interval on queue.job.channel


10.0.1.47.2 (2020-01-22)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2377: change domain for Newpharma products



10.0.1.47.1 (2020-01-14)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2373: simplify closing dates handling
* ALCYN-2374: Add a warning when multiple tax of type VAT are selected on sale order lines
* ALCYN-2371: Speed improvement for ESB stock update
* ALCYN-2375: Don't reset the BO value to 0

**Bugfixes**

* ALCYN-2266: Concurrent access on delivery round assignment (fix implementation)
* ALCYN-2150: fix performance issue (ALCYN-2372)
* ALCYN-2373: force proper filtering of pickings on delivery round
* ALCYN-2354: improve purchase planned date implementation
* Product Price Mass import improvements

**Build**

* ALCYN-2373: update translation


10.0.1.47.0 (2020-01-03)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2330: use a database lock to avoid interaction between zetes and
  stock_groupbypartner
* ALCYN-2333/ALCYN-2334: Add indexes in database to speed up some Stock operations
* ALCYN-2322: Add existing vendor product code in new product supplier info, if
  it does not exist set a dash.
* ALCYN-2282: Add partners holidays schedules, enable holidays in delivery roundings
* ALCYN-2323: Add a warning when multiple tax of type VAT are selected on invoice lines
* ALCYN-2130: fix issues with delivery rounds and back orders
* Product Prices Mass Import
* ALCYN-2359: Fix ALCYN-2299 don't decrease product uom qty
* ALCYN-2150: special case for MTO product: purchase them straight away

**Bugfixes**

* ALCYN-2344: Change invoice sending method to have right method for all customer type


10.0.1.46.1 (2019-12-12)
++++++++++++++++++++++++

Include content of 10.0.1.46.0 and the following changes

**Bugfixes**

* ALCYN-2339: fix purchase discount computation for lines added via purchase
  review
* ALCYN-2281: install 'purchase_delivery_split_date' and fix views and model name


10.0.1.46.0 (2019-11-28) [YANKED]
+++++++++++++++++++++++++++++++++

Content moved to 10.0.1.46.1

**Features and Improvements**

* ALCYN-2279: Set technical group on route category field
* ALCYN-2294: Always subscribe on partner with note
* ALCYN-2300: New sale order coming in the web service with an unknown product must be accepted and a message logged (ESB)
* ALCYN-2305: Auto-cancel Unavailable Sale Line Quantity
* ALCYN-2313: Change priority of job for creating new sales orders to 2
* ALCYN-2281: Customizations of purchase dates management

  * New wizard to move Stock Moves to another delivery order
  * Smart button to product form for quick search incoming not finished moves
  * Split scheduled time in purchase order in two fields (date / time)

**Bugfixes**

* ALCYN-2268: Fix issue with random wrong discount computation on the first
  line of the invoice
* ALCYN-2300: Fix sale channel web on export of sale order (ESB)
* ALCYN-2309: Fix cancellation of sale orders after some delay
* ALCYN-2261: Voice picking, wrong product qty returned
  The quantity of the current stock location is now returned instead of the
  total stock within the warehouse.
* ALCYN-2307: fix stock valuation with PMP based on current stock
* ALCYN-2266: Concurrent access on delivery round assignment

**Build**

* updated OCA/queue to get test helpers.

**Documentation**


10.0.1.45.3 (2019-11-20)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2311: fix recomputation of taxes in invoice fast line entry


10.0.1.45.2 (2019-11-19)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2313: change priority of job "Create a sale order with data coming from
  webservices" to 2 instead of 25

**Bugfixes**

* ALCYN-2317: fix issues with purchase discounts
* ALCYN-2309: Fix cancellation of sale orders after some delay


10.0.1.45.1 (2019-11-14)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2303: Fix improvement of purchase invoice encoding (ALCYN-2260)
  The invoice lines are generated through an onchange when filling the PO field,
  as such readonly fields are not send to the server to be stored.
  The use of 'web_readonly_bypass' from OCA/web solves this issue (equivalent
  of 'force_save' field attribute on Odoo >= 11).
* ALCYN-2302: Add missing sale warning for stupefiant vet


10.0.1.45.0 (2019-10-30) [YANKED]
+++++++++++++++++++++++++++++++++

Note: moved to 10.0.1.45.1

**Features and Improvements**

* ALCYN-2249: Change account reconciliation partner domain
* ALCYN-2260: Improvement of purchase invoice encoding
* ALCYN-2224: make blocking documents visible in archive wizard
* ALCYN-2259: Add new product.category and add exception.rule for it
* ALCYN-2204: Recompute taxes on invoice when invoice line are deleted

**Bugfixes**

* ALCYN-2263: Fix CNK unicity error when duplicating a product
* ALCYN-2256: Union credit and payment lines, sort in chronological order
* ALCYN-2242: Fix rounding computing
* ALCYN-2206: Add unique constraint on product cnk_code field
* ALCYN-2236: Fix differences with inventory to date and stock valuation
* ALCYN-2268: Fix rounding issue with taxes on invoice.

  Taxes are now computed on rounded base price.
  The rounding was done on base price only after tax computation.
  It fixes the tax amount and the base price of few cents of difference.


10.0.1.44.3 (2019-10-29)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2284: Fix recompute of additional product
* ALCYN-2292: Fix triple discounts miscomputations in some conditions


10.0.1.44.2 (2019-10-23)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2275: fix sort order of delivery rounds


10.0.1.44.1 (2019-10-17)
++++++++++++++++++++++++

**Fixes for 10.0.1.44.0**

* ALCYN-2256: Show debit lines on credit control report
* ALCYN-2217: Fix the consolidated branch that did not pull the last changes
* ALCYN-2264: Fix default creation date for sale order in connector_esb
* ALCYN-2264: Fix decimal precision on partner Max delay on sale order operation
* ALCYN-2263: Fix CNK unicity error when duplicating a product

**Features and Improvements**

* ALCYN-2232: Take into account OPW for cache issue on related fields on
  inherited models
* ALCYN-2233: l10n_be_intrastat: propagate country_id
* ALCYN-2239: Change the stock location name computation, a location keeps the
  same name if it is of usage 'view' or has the "act as view" flag set.
* ALCYN-2241: Improve margin SQL views performance
* ALCYN-2217: Improve auto reconcile module, adding an option to reconcile only
  credits on the same journal than the invoice
* ALCYN-2244: Allow for the cancellation of sale order at creation and
  confirmation if the time to run the jobs is too long based on a value set for
  each customer.
* ALCYN-2177: Add erp_name when exporting sale order to the ESB
* ALCYN:2246: Add a flag on stock location to mark the ones whose product
  quantity should not be used in the immediately available quantity computation
* ALCYN-2091 refactor purchase discount computations
    * onchange on purchase order line quantity was calling price_unit computation (`_compute_price_unit`)
      numerous times through the triggers `api.constraint` which is preventing jobs
      from restarting correctly in case of concurency errors.
    * move logic to the procurement instead of trying to be universal with api.constrains
      it might requires more code, but will be more readable
* ALCYN-2139: Add a specific module to customize the credit control report
* ALCYN-2206: Add unique constraint on product cnk_code field
* ALCYN-2129: Add last selling and purchasing date on Inventory valuation
* ALCYN-2178: Make sure lots are not archived when receiving products

**Bugfixes**

* ALCYN-2164: Exclude scrap locations from the life date computation
* ALCYN-2223: Fix context error for printing labels
* ALCYN-2141: lock picking on printing and validation commands received from Zetes


10.0.1.44.0 (2019-10-07) [YANKED]
+++++++++++++++++++++++++++++++++

Moved to 10.0.1.44.1


10.0.1.43.1 (2019-09-18)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2188: Handle inventory shortage of products without tracking
* ALCYN-2166: Make sure partners belong to an itinerary when creating
  a pharmacy reception
* ALCYN-2165: Remove spaces in product_template cnk_code field
* ALCYN-2181: Move menu 'Stock Pack Operation Report' to Reports
* ALCYN-2127: Add priority on jobs, improve channels configuration

**Bugfixes**

* ALCYN-2225: Correct sending of email from Customers Statements,
  add partner as follower (OPW-2041448)
* ALCYN-2180: Fix "immediately_available_qty" computation & ignore parking locations
* ALCYN-2197: Fix model not up to date after pending-merge update

**Build**

* ALCYN-2190: Add script to correct cutoff entries from april and may 2019


10.0.1.43.0 (2019-09-09) [YANKED]
+++++++++++++++++++++++++++++++++

Moved to 10.0.1.43.1


10.0.1.42.7 (2019-09-02)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2213: Update "date_range" module as its data model changed
* ALCYN-2214: Correct total amounts of rounding in invoice report
* ALCYN-2222: Fix correction in account_invoice_accrual
* ALCYN-2178: Make sure lots are not archived when receiving products


10.0.1.42.6 (2019-08-29) YANKED
+++++++++++++++++++++++++++++++

Moved to 10.0.1.42.7


10.0.1.42.5 (2019-08-21)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2211: Invoice reconciliation jobs blocked


10.0.1.42.4 (2019-08-14)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2201: Remove side-effects from "api.constrains", which prevent HTTP
  requests and Jobs to be retried on concurrent transaction errors
* ALCYN-2201: Fix issue with sale exception taking excessive locks and
  preventing to create or confirm sale orders concurrently


10.0.1.42.3 (2019-08-07)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2195 Hotfix exception concurency errors


10.0.1.42.2 (2019-08-06)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2195 Fix MemoryError on WS sale order creation due to recheck of all existing lines.


10.0.1.42.1 (2019-08-05)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2046: Install account_reconcile_restrict_partner_mismatch
* ALCYN-2067: Add archive wizard to realocate sales, invoices and pickings to
  an other customer.
* ALCYN-2079: Install module account_invoice_split_refund
* ALCYN-2079: Split generation of invoices and refunds in cron job
* ALCYN-2080: Install account_invoice_payment_report
* ALCYN-2080: Install account_payment_mode_auto_reconcile
* ALCYN-2155: Update translations for invoice and delivery slip reports
* ALCYN-2155: Display product name in customer lang in delivery notes

**Bugfixes**

* ALCYN-2137: Enable re-printing product label without lot
* ALCYN-2145: Fix creation of credit control lines
* ALCYN-2163: Fix invoice creation when there is no more invoiceable qty

**Build**

* Remove Danger Systems checks


10.0.1.42.0 (2019-07-31) [YANKED]
+++++++++++++++++++++++++++++++++

**And moved into 10.0.1.42.1**
**with revert of ALCYN-2091**


10.0.1.41.0 (2019-07-16) [YANKED]
+++++++++++++++++++++++++++++++++

**Extracted patch into 10.0.1.40.2**
**And moved other features into 10.0.1.42.0**

10.0.1.40.3 (2019-07-29)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2186: Fix cutoff computation error (last day of the month for invoice)


10.0.1.40.2 (2019-07-22)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2100: Add pivot view with operator for picking
* ALCYN-2100: Add right for stock manager to see operator picking pivot view
* ALCYN-2169: Change fields to see operator picking pivot view
* ALYCN-2126: bank statement auto match button based on structured ref

**Bugfixes**

* ALCYN-2089: Fix the expiration date in sale order line, by taking into account only quants in physical location and not reserved.
* ALCYN-2094: Fix product used to add shipping cost on sale order line

10.0.1.40.1 (2019-07-09)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2121: Fix error in check of purchased quantity for MTO products


10.0.1.40.0 (2019-07-08)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2092: Improve Sales Orders confirmation performance
* ALCYN-2081: Display Delivery Orders linked to sale orders on invoice report

**Bugfixes**

* ALCYN-2101: Reservation per units - error in comparison
* ALCYN-2124: Fix Stock History filters and group by product category


10.0.1.39.1 (2019-07-02)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2087: Add the FreeShipping node to the customer XML payload exported to the ESB
* ALCYN-2086: Update stock move reassign trial to improve performance


10.0.1.39.0 (2019-07-01) [YANKED]
+++++++++++++++++++++++++++++++++

**Moved to 10.0.1.39.1 to revert dev of ALCYN-2O78**


10.0.1.38.0 (2019-06-21)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2064: decrease qty on linked procurement order when the qty on a PO
  line is decreased.
* ALCYN-2015: Display supplier reference in general ledger reports

**Bugfixes**

* ALCYN-2061 / ALCYN-2012: Prevent stock move to be consolidated in closed
  delivery round


10.0.1.37.1 (2019-06-07)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2043: change stock locations with usage 'view' to 'internal' with a new flag "act as view".
  We cannot move quants to such location, but still they need to have an 'internal' usage to be considered
  properly by the stock addon's code.
* ALCYN-2043: Improve inventory handling:

 - Fix error "Record does not exist or has been deleted" when the update
   quantity wizard on a product fails
 - Handle correctly an inventory with the same product more than once (it would
   set the same error on all the lines)
 - Display a cleaner error message both in the inventory lines and pop-up
 - Unit tests using inventory in other modules will not fail

* ALCYN-2006: do not allow to change delivery round of an outgoing picking
  when the PICK one has been started (printed=True)

**Data**

* ALCYN-2070: Recompute last historic average price of products


+ corrections of 10.0.1.36.1



10.0.1.37.0 (2019-05-29) [YANKED]
+++++++++++++++++++++++++++++++++

Moved to 10.0.1.37.1 to include corrections of 10.0.1.36.1.


10.0.1.36.1 (2019-06-07)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2066: Use a single "zetes" user for Zetes operations and change operator users to
  Portal users

**Bugfixes**

* ALCYN-2075: Fix state done when exporting sale order to ESB


10.0.1.36.0 (2019-05-24)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2027: Execute reconciliations as jobs at Payment Orders's file uploaded
  confirmation.
* ALCYN-2027: Add indexes to optimize payment order queries
* ALCYN-2027: Add index to optimize Sale count widget on products
* ALCYN-2020: Make ref field for res.partner model readonly
* ALCYN-2055: update translations for website_purchase_review, specific_purchase
* ALCYN-2050: Add custom filters and the residual amount field on the Account Items view

**Bugfixes**

* ALCYN-2045: set order to proper tax computations
* ALCYN-1990: Upgrade intracom VAT report module to fix xml report
* ALCYN-2065: Fix delivery note generating with non ascii characters in product names
* ALCYN-2049: Fix that sometimes on Magento a sale order back order is not up to date.
* ALCYN-1982: Do not export to the ESB sale order line that are actually delivery information.

**Build**

**Documentation**


10.0.1.35.4 (2019-05-17)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-2013: Extend the products available by Newpharma adding all products in the category 'Médicaments vétérinaires belges' (ESB)
* ALCYN-2008 Optimize "Remains to deliver" filter performance
* ALCYN-2009: Improve `sale.order.line` views
* ALCYN-2041: account_mass_reconcile: Display partially reconciled items

**Bugfixes**

* ALCYN-2002: fix average price computation when purchase price is changed
  after the confirmation of the purchase
* ALCYN-2012: Prevent shop move to be consolidated in closed delivery round
* Remove deprecated t-esc-options instruction in delivery slip report, showing a
  warning on each print
* ALCYN-2045: set order to proper tax computations

**Build**

* ALCYN-2017: Upgrade wkhtmltopdf to version 0.12.5

10.0.1.35.2 (2019-05-13) [YANKED]
+++++++++++++++++++++++++++++++++

Replaced by 10.0.1.35.4

10.0.1.35.1 (2019-05-06) [YANKED]
+++++++++++++++++++++++++++++++++

Replaced by 10.0.1.35.4


10.0.1.35.0 (2019-05-02) [YANKED]
+++++++++++++++++++++++++++++++++

Replaced by 10.0.1.35.1


10.0.1.34.3 (2019-05-06)
++++++++++++++++++++++++

**Data**

* ALCYN-2029: lower erroneous stock quantities which were around ``1*10^64``
  provoking wrong computations on the concerned product

**Features and Improvements**

* ALCYN-2031: Install account_mass_reconcile_partner


10.0.1.34.2 (2019-04-16)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-2005: Fix web service create web sale order when the carrier_id value in the data is None


10.0.1.34.1 (2019-04-02)
++++++++++++++++++++++++

**Data**

* ALCYN-1553: Set APB Authorization field on non Veterinary customers

**Bugfixes**

* ALCYN-1987: fix ALCYN-1966 to invoice SOs configured with "unique invoice"


10.0.1.34.0 (2019-03-28)
++++++++++++++++++++++++

**Features and Improvements**

* ALCYN-1966: Apply SO unique invoice on all invoicing cases
* ALCYN-1610: Add SQL views calculating the margin by product for the BI tool
* ALCYN-1973: install account_analytic_no_lines, purchase_delivery_split_date
* ALCYN-1977: Scrap expired products through "Inventory control / Scrap" menu
  and through inventory adjustments
* ALCYN-1978: Update OCA/l10n-belgium to the last version
* ALCYN-1980: Disable domain for mto rules
* ALCYN-1809: Add optional label report printing

**Bugfixes**

* ALCYN-1983: Update account_financial_report_qweb

**Build**

* ALCYN-1985: upgrade FROM docker image to 10.0-3.1.2


10.0.1.33.1 (2019-03-19)
++++++++++++++++++++++++

**Bugfixes**

* ALCYN-1975 Fix crash with .format() called bytestrings


10.0.1.33.0 (2019-03-19)
++++++++++++++++++++++++

**General changes**

* Switch to 5 digits version [10.0] represents the Odoo version and [1.33.0] the project's one.
* Enforce 'pre-commit' on the project with black, isort, pyupgrade and few others

**Features and Improvements**

* Add picking type on declared loss
* ALCYN-1962: Speed up loading of partner form view

  The computed field 'last_suite_name' on 'res.partner' performs a search on
  'sale.order' using 'LIMIT 1', this makes PostgreSQL very slow to get the
  relevant row. Adding a partial index on corresponding fields fix the
  performance issue.

* ALCYN-1972: Create filter for articles in BO on purchase
* ALCYN-1956: Allow to receive products directly in stock (without going through the parking)
* ALCYN-1965: Add the storage temperature when exporting a product to the ESB.

**Bugfixes**

* ALCYN-1948: add invoice number + date invoice in the invoice footer


10.32.1 (2019-03-11)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1957: Reduce the time to open the list of purchase orders.

  The field 'nbr_lines_bo' on PO was quite big to compute (itself based on the
  'immediately_usable_qty' computed field of product).
  As the this field is displayed on the PO form, it has been removed from the
  tree view to reduce drastically the time to open the view.

**Bugfixes**

* BIZ-3075: Fix intrastat report layout


10.32.0 (2019-03-07)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1810: Allow optional printing 'Entry register' part in delivery slip
* ALCYN-1953: Install account_mass_reconcile module
* ALCYN-1921: Allow users of the Accountant group to read Stock Inventory
* ALCYN-1958: Track change on chatter for field: is_sale_back_order_accepted, is_sale_back_order_cancel
* ALCYN-1963: Allow to access picking subcode (PICK, LOSS, ...) on stock move. Convenient for reporting

**Bugfixes**

* Fix label printing of non-ascii characters
* Correct hidden dependency between addons
* ALCYN-1961: Some lots created at reception are not linked to the right product
* BIZ-3075: update tags instead of add new one in intrastat report
* Fix some startup warnings:

  - onchange on dotted path field is not supported
  - add missing ACL on Report Stock Overview
  - clean "ir.model" which exists in DB but have been removed from code


10.31.1 (2019-03-05)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1954: Add Inventory Value in the pivot view of Stock History Valuation
  and remove Location which gives useless results

**Bugfixes**

* ALCYN-1950: Hack board.board to fix RPC calls
  When `custom_view_id` is not valued it gets translated to JS undefined.
  When the unfold action in the dashboard calls `/web/edit_custom`
  it uses `JSON.stringify` to send params but it strips out undefined values
  and the RPC call is broken for a missing argument.
  Here we make sure we always have a good falsy value.
* ALCYN-1951: apply specific styling only for invoice report
* ALCYN-1940: set correct precision on numbers for intrastat report and set close to false in Data tag
* ALCYN-1954: add an index on product_price_history.product_id, makes the stock valuation very slow
* ALCYN-1954: apply a patch correcting the groupbys on stock history (https://github.com/odoo/odoo/commit/ba09b8989ebbe10aa336dbf850d075fbcda558d0)
* ALCYN-1954: optimize stock history with new indices and a code optimization on groupbys (https://github.com/odoo/odoo/pull/31540)
* ALCYN-1955: Fix crash on the Sales Orders' Fast Line Entries view

**Data**

* ALCYN-1940: Correct country of origin on invoice lines and products


10.31.0 (2019-02-28)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1945: Delivery notes improvement (returns + newpharma CNK)
* ALCYN-1896: Change sorting of products in sales / products and when in
  sale_order_line product selection
* ALCYN-1947: Add the zone in the default name based on the location coordinates
* ALCYN-1903: compute stock history valuation based on VLB locations
* ALCYN-1903: store stock history as materialized view, allowing to
  improve browsing performance thanks to indices and the fact that
  data is stored

**Data**

* ALCYN-1903: fix moves which have had their source or destination location moved out of the stock

* Include a performance patch, improving x3 computation of stock availability for
  a product (https://github.com/odoo/odoo/pull/30545/)

**Bugfixes**

* ALCYN-1946: Products labels do not print when the file send to the printer is
  to big. Reduce file size by sending repeat command to the printer instead of
  repeating the label inside the file.
* ALCYN-1949: Fix Zetes UnicodeEncodeError for users with non ascii characters in the name
* BIZ-3022: Magento sends only an order date without time, in a previous change (ALCYN-1930),
  the time 12:00 (UTC) was appended to the Magento date, now the current time at the import
  will be appended. The correct solution would be that Magento send the time alongside the date.
* ALCYN-1940: Backport country of origin

**Build**

* ALCYN-1942: Add the repo mis-builder from OCA and install the module:
    mis_builder, mis_builder_budget, l10n_be_mis_reports, analytic_tag_dimension
    analytic_tag_dimension_purchase_warning, analytic_tag_dimension_sale_warning
    sql_request_abstract, base_import_security_group

**Documentation**


10.30.24 (2019-02-22)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1813: Fix removal strategy and fix Zetes tests. Consume entirely a pallet before going to next one.
* ALCYN-1833: Prevent reception order to be unreserved due to undelivered customer in delivery round
* ALCYN-1886: Display picking zone also on product (not only template)'
* ALCYN-1870: Partner. Display amount of sales lines that remains to deliver instead of total amount of lines
* ALCYN-1937: Fix set account analytic on imported purchase orders
* Install Belgium intrastat 2019

**Bugfixes**

* ALCYN-1880: Sales line "Current BO" cannot be bigger than what remains to be delivered

* ALCYN-1930: Fix order_date on sale order created by the web service (ESB)

* ALCYN-1898: Remove consignment from remain to deliver
* ALCYN-1941: Prevent cleanup of pack operations when a move line is added in a ship.
  When an already picked product is again ordered while the picking of the
  first product was already done but the shipping was not yet validated,
  the shipping move line of the first picked product was unreserved and
  never processed.


10.30.23 (2019-02-19)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1908: Fix/improve delivery note (font-size, nbr packs)
* ALCYN-1910: make sure all products needing resupply have a default
  procurement order (except MTO products)
* ALCYN-1912: Automatically cancel procurement from OP on purchase line deletion
* ALCYN-1914: Check procurement when qty 0 is purchased
* ALCYN-1919: When an inventory is validated, we need to cancel any remaining pending inventory moves
* ALCYN-1928: Manage backorders of additional products (accessories). Support
  use cases where the computed quantity of additional product to pick is not
  processed or partially processed. Do not propagate to backorder. The quantity
  in the backorder will be recomputed based on the main base product quantity
  to pick.
* ALCYN-1936: Allow inventory user to post inventory without requiring write rights on product

**Bugfixes**

* ALCYN-1856: Two new columns available in debug mode:

    - the picking zone of the product is displayed on sale order lines
    - the procurement group is displayed on the delivery order lines in favor
      of the SO reference

* ALCYN-1926: Fix processing of delivery round deletion.
* BIZ-2869: Prevent canceling a sale order already prepared

**Bugfixes**

* ALCYN-1932: add a field on SO lines to record returned qty
* ALCYN-1933: some delivery slips / CSV delivery notes would not get the lot
  numbers for all lines
* move back quants from "Fix Sortie 20181220" that should be shipped

**Build**

**Documentation**


10.30.22 (2019-02-11)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1894: Update the repo OCA sale-workflow - fix the bug to compute the total amount on a sale order if there is a discount
* ALCYN-1884: add a flag "Create Invoice On Transfer" on picking types.
  This flag is active on Delivery Orders and Customer Returns (for refund).
  Previously this feature was only active on Delivery Orders.
* ALCYN-1894: Update the repo OCA sale-workflow - fix the bug to compute the total amount on a sale order if there is a discount

**Bugfixes**

* ALCYN-1913: Cannot delete multiple delivery rounds at once

**Data**

* ALCYN-1884: generate refunds for Customer Returns grouped by delivery
  which were done in the past
* ALCYN-1897: recompute invoiced quantity on imported purchase orders from AS400 based on received quantities


10.30.21 (2019-02-10)
+++++++++++++++++++++

**Features and Improvements**
* fix the name of moves for promotional products
* display the order for SHIP moves (in debug mode)

**Bugfixes**
* ALCYN-1900: fix lot swapping in PICK in case of a rupture
* ALCYN-1854: Make the delivery method only required when SO is editable
* ALCYN-1906: Hide transfer button when picking is done. Display put in pack only for Pick operation
* ALCYN-1867: fix some reservation problems

**Build**
* Add a script to clean the output location


10.30.20 (2019-02-05)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1877: add a fast view for the input of supplier invoice lines


**Bugfixes**

* ALCYN-1876: Fix handling of lot in multiple locations when a product is several times in a picking,
  replace patch by a more thorough one (https://github.com/odoo/odoo/pull/30681#issuecomment-460254826)
* BIZ-2925: Fix missing translation in report
* BIZ-2926: set some accounts being reconciliable


10.30.19 (2019-02-04)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1708: add a fast view for the input of sale order lines
* Change SMTP and IMAP configuration to mail.abl.grp

**Bugfixes**

* ALCYN-1876: Fix handling of lot in multiple locations when a product is several times in a picking
* ALCYN-1879: Fix post inventory rollback on error
* ALCYN-1892: Zetes: do not revert quantity added to a lot when call to skip a
  lot fails
* ALCYN-1879: Fix post inventory rollback on error
* ALCYN-1893: Fix cutoff lines generation - Do not generate lines twice

**Build**

* Upgrade docker-odoo-project base image to 3.1.1

  * Bugfixes

    * Remove the NO_DATABASE_LIST option, does not exist, the sole option is DB_LIST

  * Libraires

    * Bump requests version
    * Bump PyYAML version for CVE-2017-18342


10.30.18 (2019-02-01)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1866: Block edition of confirmed purchase lines but description,
  price_unit, discount and promotion.

**Bugfixes**

* BIZ-2905: Terms not translated in specific sale
* BIZ-2915: Add import invoice with reference type : Structured in payment order
* BIZ-2937: Fix invoice_ids append on invoicing job
* ALCYN-1878: Fix supplier promotion created twice on Magento (ESB)
* ALCYN-1885: Fix concurrency issue in package creation


10.30.17 (2019-01-28)
+++++++++++++++++++++

**Features and Improvements**

* BIZ-2823: optimize number of requests sent by the Wizard for returning stock
  operations, might have an effect on the server load

**Bugfixes**

* ALCYN-1875: properly rollback on errors happening during the posting of an inventory
* ALCYN-1875: correct handling of exceptions during exchanges with Zetes,
  properly rollback changes on error


10.30.16 (2019-01-24)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1805 : remove puchase order locked(done state) from cut-off
* ALCYN-1854: Make the delivery carrier on sale order required and set its default value to Alcyon Delivery Method
* ALCYN-1872: When a sale order line is added in an already confirmed SO for a product already ordered, the reservation of that product must be relaunched
* Add module "web_cache_name_get" reducing requests to name_get on same records

**Bugfixes**

* ALCYN-1529 Claim view: set proper ctx for purchase order view

  Setting `show_purchase` on PO view hides/shows meaningful information: use it!

* ALCYN-1811: Exclude service products from Remains to deliver filter
* ALCYN-1853: take priority and stock losses in the sale order line missing qty


10.30.15 (2019-01-23)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1829: Improve the default search on name for customer by including the "Nom d'appel" in the search
* ALCYN-1864: Sale order, do not allow the modification of order lines if the
  order is confirmed.

  The only fields which remain editable are:
    * description
    * route
    * promotion
    * discount
* ALCYN-1865: Some shippings are sometimes not delivered. While this should not happen, prevent this to cause any side effect in the reservation
* Simplify and remove extra cursor in the job generating the invoice for a partner
* Improve backorder logging message

**Bugfixes**

* ALCYN-1824 website_purchase_review: fix onchange on new PO line
* ALCYN-1857: Retry queue jobs failing due to "Unable to use closed cursor"
* website_purchase_review: fix ZeroDivisionError on PO w/out lines
* ALCYN-1858: Job exports do not fail if the record to export has been deleted
  on Odoo
* ALCYN-1859:
    * Fix an error with the arrangement workflow (Zetes); wrong value received from Zetes
    * Fix the label (data sent to Zetes) if the user switch lot in the same transaction
* ALCYN-1861: Fix backorder quantities on sale order lines for additional products
* ALCYN-1869: Launch reservation of moves added in an existing picking in waiting state

**Build**

* ALCYN-1857: Update queue_job with the latest corrections
* docker-compose: SERVER_WIDE_MODULES is enough, no need for `--load` param


10.30.14 (2019-01-22)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1796 Add field for product.template.nb_days_out_of_stock
* ALCYN-1800: Display the barcode value below the barcode
* ALCYN-1819: Remove account.chunk_size and never use one for
  _job_invoices_by_partners. It allows us to have one job per client and it is
  better in case of failure.

**Bugfixes**

* ALCYN-1788: restore display of backorders on delivery slip
* ALCYN-1815: Fix pharmacist emails sent in triplicate

**Build**

* ALCYN-1745: Reactivate all remaining unittest for Zetes


10.30.13 (2019-01-21)
+++++++++++++++++++++

**Features and Improvements**

* BIZ-2795: Add account-financial-report-qweb for journal reporting
* BIZ-2796: Add account-financial-report-qweb
* ALCYN-1801: do not send "You have been assigned to..." email to new followers on any documents

**Bugfixes**

* ALCYN-1785: do not delay jobs for generating pdf files on supplier invoices
* ALCYN-1843: Recompute picking having a reserved quant stolen by an inventory adjustment
* ALCYN-1844: Reservation not properly updated in case of stock increase and picking already partially served
* ALCYN-1847: Fix free product promotion on sales to be given only to allowed customer
* ALCYN-1850: after changing manually a delivery round on a transfer, new moves
  will not be grouped with this transfer anymore
* ALCYN-1851: Do not deliver shipping not available

**Build**

* ALCYN-1736: Apply patches for ODOO-SA-2018-11-28


10.30.12 (2019-01-18)
+++++++++++++++++++++

**Bugfixes**

* ALCYN-1675: group moves in pickings considering the delivery method


10.30.11 (2019-01-17)
+++++++++++++++++++++

**Bugfixes**

* ALCYN-1838: Fix product price for sale order created through the web service (ESB) The product pricelist assigned to the customer was not used.
* ALCYN-1837: Fix delivery condition in Dutch on delivery slip
* ALCYN-1837: Add missing translation for "Number of package" in Dutch
* ALCYN-1837: Fix product names translations in delivery slip lines
* ALCYN-1837: Always show price on consignements
* ALCYN-1837: Print entry register only if the customer has a Veterinary depot number


10.30.10 (2019-01-16)
+++++++++++++++++++++

**Bugfixes**

* ALCYN-1771: Fix very slow export for the stock introduced by this Jira card
* ALCYN-1806 : Unpack stock quant package if it's a return from a customer
* ALCYN-1841: Fix SQL query in delivery_rounds that forced to roll back release 10.30.9 and improve testing


10.30.9 (2019-01-15)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1258: Improve sale warning on product out of stock at supplier level
* ALCYN-1774: Improve mass invoicing
    * Add a filename with a pdf extension to the report file, to ease file download.
    * Sort the invoices by customer ref in the report file.
    * Set the invoices state to 'sent' later in the job to avoid erroneous state if the job fails.

**Bugfixes**

* ALCYN-1763: Fix blocked pickings that contains only partially available lines
* ALCYN-1793: Date on delivery slip and entry register mismatch
  The right date is date_done defined on the delivery slip
* ALCYN-1802: Improve customer reference on delivery note filename by searching for the custmoer on sale order related to the stock picking.
* ALCYN-1837: Remove grand-total tax included on delivery slip as it
  doesn't use the same computation as in invoice it could lead to
  mismatch on cents.
* ALCYN-1839: Fix failing 'rupture' declared in the voice picking
* ALCYN-1840: Remove duplicated 'Partner' field on delivery form


10.30.8 (2019-01-14)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1781: Show primary unit price, net unit price and VAT an delivery orders
* Prevent to process additional moves when there is no (small speedup)

**Bugfixes**

* ALCYN-1799: Fix possible error with carrier_id field in new web sale order web service (ESB)
* ALCYN-1832: Fix special promotion appearing twice on Magento after changing it's end date.
* ALCYN-1834: Fix print delivery slip traceback


10.30.7 (2019-01-11)
++++++++++++++++++++

Move to 10.30.8

10.30.6 (2019-01-10)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1705: Add the canceled quantity in the sale order line view of a product
* ALCYN-1745: Reactivate some unittests for Zetes
* ALCYN-1758: Update the order date when the procurement update or create a purchase order
* Add menuentries to customer invoices/refunds for sales users in sales and accounting

**Bugfixes**

* ALCYN-1763: Prevent already picked product but not yet delivered to be accounted in the quantity still to pick and blocking the reservable quantity
* ALCYN-1771: Fix product expiration date exported to the ESB.
* ALCYN-1784 Update OCA/account-analytic. The goal is to be able to invoice a
  supplier with an expense tax
* ALCYN-1802: Fix customer reference on delivery note filename.
* ALCYN-1804: Fix invoicing address for sale order created on the web
* ALCYN-1820 Do not override sale confirmation date when an order is canceled for modification and then reconfirmed
* Remove unused restriction for inventory
* Workaround on cutoff extremely slow display by hiding taxes field.

**Build**

* Remove db2_import

**Data Migration**

* Import supplier journal items and post all imported items


10.30.5 (2018-12-31)
++++++++++++++++++++

**Bugfixes**

* ALCYN-1792 fix in customer invoice report


10.30.4 (2018-12-23)
++++++++++++++++++++

**Bugfixes**

* ALCYN-1787: Fix the name search of round template
* Fix delivery round include itinerary


10.30.3 (2018-12-23)
++++++++++++++++++++

**Bugfixes**

* Fix reservation by unit - exclude domain at each step
* ALCYN-1726: reverse list of customers on delivery round report
* ALCYN-1726: reverse list of customers on delivery round report: solves the
  right report and revert change on the wrong one

**Features and Improvements**

* Prevent to cancel a pick/ship and allow to recover the one already canceled
* Assign waiting pickings to delivery rounds and show default itineraries
* BIZ-2655: add filename named accoring to the mandate sequence

10.30.2 (2018-12-20)
++++++++++++++++++++

**Bugfixes**

* Automaticaly unreserve a move that is sent to backorder


10.30.1 (2018-12-20)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1775: Only generate a lot name for aliments at the reception
* ALCYN-1772: Add manufacturer information in product export (ESB)

**Bugfixes**

* Fix additional products and pushed moves. Limit additional products to pick only

* ALCYN-1774: Wizard for sending invoice by email, fix inconsistencies with sending method and email used.


10.30.0 (2018-12-19)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1761: generate and send pdf invoices in background


10.29.19 (2018-12-18)
+++++++++++++++++++++

**Features and Improvements**

* Refactor refill report (arrange, reassort) for real-time computation
* ALCYN-1761: improve the view of the action to send invoices by email / print, make it less confusing
* ALCYN-1761: the "Related" button on the job related to invoices now try to open the correct view (customer or supplier)
* Take only pickings to generate the delivery round
* Delivery round: Cancel BO for customer that do not want BO
* ALCYN-1563: Import the final customer balance and post all new journal entries

**Bugfixes**

* ProgrammingError: syntax error at or near ")"
* BIZ-2640: Customer Reference on invoice
* ALCYN-1750: Review Layout invoice to add antibiotics
* ALCYN-1767: Fix delivery note csv for product with no vat info on sale order, look for vat in product directly.
* ALCYN-1762: fix transactional errors during background delivery of delivery rounds
* Fix missing records during a reception with additional product


10.29.18 (2018-12-18)
+++++++++++++++++++++

Move to 10.29.19


10.29.17 (2018-12-14)
+++++++++++++++++++++

**Features and Improvements**

* Change environment ribbon name to "preprod" for integration
* ALCYN-1582: add 'base' amount field for taxes on supplier invoices (was added manually already)
* Add separate picking zone for Human products (AFMPS requirement)
* Extend automatic reassignment to canceled moved and priority change

**Bugfixes**

* ALCYN-1755: Fix subtotal calculation on the delivery slip report
* Take care of the restricted lot in the reservation (solving reservation of human products)
* Correctly catch an error with Zetes to avoid the crash of the voice console
* ALCYN-1760: Fix delivery note csv so no quantity are missing compared to the pdf version.
* ALCYN-1766: Change Gescgr to 1 for Psychotrope so they are not flagged as medicament and will be visible on Magento


10.29.16 (2018-12-11)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1680: keep the email sent for the fax on the sales' chatter thread
* ALCYN-1754: keep delivery note emails once sent to keep track of them
* ALCYN-1754: show delivery note emails in the delivery mail thread
* ALCYN-1754: send the delivery note email to the first parent having an email
  address when the recipient does not have one
* ALCYN-1730: Fix report Feuille de route. Adding customer Alycon reference. Changing column header Equip to Mat

**Bugfixes**

* Change the type of model for the pharmacy reception
* Fix a bug with the name_search of product.product
* Fix a bug with the wizard to "put in pack"
* ALCYN-1749: propagate the option to prevent quick create on views to all workers in multiprocess
* Fix a bug with the pharmacy reception (take also pickings with the state waiting)

**Build**

* ALCYN-1756: Pin pending-merges to prevent unwanted changes


10.29.15 (2018-12-11)
+++++++++++++++++++++

Moved to 10.29.16

10.29.14 (2018-12-10)
+++++++++++++++++++++

**Bugfixes**

* HOTFIX : Run delivery of rounds in background


10.29.13 (2018-12-09)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1713: run delivery operations of a round in background. The rounds have
  a new state "Delivering". The delivery operations run in background and if
  there any error, the round stays in this state, with a warning logo. A cron
  "Check Round Delivery State" is added to transition from Delivering to Done.

**Bugfixes**

* ALCYN-1746: Change cplz19 on export product with web_published field (ESB)
* ALCYN-1746: Invert Gescge mapping on export product (ESB)
* ALCYN-1746: Have all products even the unactive ones to be exported to the ESB
* It has been removed on https://github.com/camptocamp/alcyon_odoo/commit/3c5776ffa12e31ba133475e8151d01d7c0bd35f6
  but and added into the release 10.29.12 this morning
* Zetes: Add the possibility to change a lot and some blocking bugs

* Fix singleton error


10.29.12 (2018-12-07)
+++++++++++++++++++++

**Bugfixes**

* Fix Delivery Round delivery ongoing error message
* Fix missing record in cache


10.29.11 (2018-12-07)
+++++++++++++++++++++

**Features and Improvements**

* ALCYN-1717: Do not export to ESB sale order whose customer does not have an email as it will not be accepted by the ESB
* Reception: Change lot default name to dmy instead of Ymd
* Reception: Allow to mark a stock location as acceptable destination for a reception
* Add constraints in logistics to ensure data integrity
* Inventory: Disable restriction as it is to restrictive
* Picking: allow to dis/enable passport per picking type

**Bugfixes**

* ALCYN-1744: Disable sending New Pharma sale order to the ESB.
* ALCYN-1704: fix crash when printing a supplier fax content document on sales
* ALCYN-1723: Fix delivery note, add one line for each quant to not have multiple lot on a line
* Send Delivery Note emails using the mail queue, not as direct. Prevent
  sending emails more than once when there is an error during the validation of
  a picking. Warning: the "Email Queue Manager" cron must be active.
  orders without associated pharmacist
* Product Additional: Fix additional move unlink on main unreserve/transfer (traceback singleton error)


10.29.10 (2018-12-06)
+++++++++++++++++++++

**Features and Improvements**

* Add some logistics onchange tracking
* Add some track changes in logistics
* Group by partner: Prevent to create a backorder and use existing picking if possible (like move assignment created from procurement)

**Bugfixes**

* ALCYN-1723: Fix delivery note csv (last column, tax and file encoding)
* Improve the wizard to validate a picking and add the possibility to view all datas about a picking
* Use sudo to remove stock.move when we need to delete an additional pack op
* Product Additional: Fix additional move unlink on main unreserve/transfer'

**Build**

* Disable tests of DB2 import tool to speed CI testing


10.29.9 (2018-12-05)
++++++++++++++++++++

**Bugfixes**

* ALCYN-1725: Fix 'Via Pharmacy' in Magento in product export (ESB)
* ALCYN-1735: Zetes Assignement - return only open pickings
* Fix regression on export of stock for life_date


10.29.8 (2018-12-04)
++++++++++++++++++++

**Features and Improvements**

* Improve put in pack: manage picking without lines done + count amount of products for Food'
* Create an unique Wizard to validate a picking (passport) and/or change a lot

**Bugfixes**

* Fix checksum generation for colis pharmacy
* On export of stock exported life_date is now based on lot with quantities > 0


10.29.7 (2018-12-04)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1707: Disable assignation mailing to salesman on WS create order

**Bugfixes**

* Delivery rounds: Fix singleton error
* ALCYN-1712: Fix default filter on delivery_round, adding today_search as well.
* ALCYN-1709: On new sale order coming from web service. Fix quantity at zero on sale order line with sale exception (ESB).
* Fix falsy value for qty_ordered on sale order line (ESB)


10.29.6 (2018-12-04)
++++++++++++++++++++

**Features and Improvements**

* Add in picking view: weight, operator, partner, zetes_state
* ALCYN-1567: Do not show a notification popup when a sales order is confirmed in background

**Bugfixes**

* ALCYN-1711: Fix delivery note format, adding a separator at the end of each line ';'
* Fix reception pharmacy
* Fix delivery note: 'NoneType' object has no attribute 'is_consignement'
* Improve at lot of Zetes features
  * Set limit to 30 characters on partner name on product labels
  * Add a field to print multiple labels at once
  * Add a wizard to change lot used in a picking
  * Add better error catching and logs when add the picked quantity on the pack lot
* Ensure webservice.message.sale.order.status returns 0 when availability is negative.


10.29.5 (2018-12-02)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1703: Add an ENV variable to control mail sender for mails sent to OVH fax service.

**Bugfixes**

* Fix quants reservation for pallet/box/wrap preferred reservation


10.29.4 (2018-12-02)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-163: Send emails on order confirm to pharmacist to unlock human drup picking flow


10.29.3 (2018-12-02)
++++++++++++++++++++

**Bugfixes**

* Fix some problems with zetes and not send an email with an user cancel a purchase order


10.29.2 (2018-12-02)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1695: Add a flag on product to not print label for these product
* ALCYN-1696: Add the possibility to print a lot label

**Bugfixes**

* ALCYN-1686: Use the date done on the delivery slip and on the exported CSV
* ALCYN-1694: An user without the group accounting cannot see standard fields


10.29.1 (2018-12-01)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1667: Allow to search a product by the reference of the supplier
* ALCYN-1684: Force the user to put in pack before validate a picking
* ALCYN-1681: Display the depot number on the sale order report
* ALCYN-1682: Add a menu entry to open an UOP

**Bugfixes**

* ALCYN-1649: sale_triple_discount: Fix tax total on report
* ALCYN-243: Set the serial number on the picking out
* ALCYN-1689: Fix a bug with the passport and use the right printer for the passport

10.29.0 (2018-11-30)
++++++++++++++++++++

**Data Migration**

* Update full csv data from DB2 prod server at 2018-11-30 13:50:00

**Features and Improvements**

* ALCYN-1623: Sort bins on products to take first bins for label printing
* ALCYN-1658: Add a context to display the internal quantity of lots on the view product
* ALCYN-1683: Speed up stock export by using direct sql for the sale_average computation (ESB)
* ALCYN-1685: Disable location translation
* Update setup of locations for "Aliments". Define rows for "reserve" and set picking_zone

**Bugfixes**

* ALCYN-1487: Fix sale exception translations
* ALCYN-1602: Never set a scrap location on a reception pack operation
* ALCYN-1668: Add a QR code on lot labels (#PRODUCT_REF#LOT_NAME) and a QR code on label without lot (PRODUCT_REF)
* ALCYN-1669: Mark customer return as to be refunded by default
* ALCYN-1670: Fix cancel remaining quantity to deliver on a sales order
* ALCYN-1683: Fix date_peremption on stock export (ESB)

**Build**

* SMTP and IMAP config for PROD server


10.28.1 (2018-11-26)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1575: Update the default credit/debit account on journals
* ALCYN-1642: Indicate if the order is a consignment on the delivery slip
* ALCYN-1601: Update the list of users
* ALCYN-1657: Display the UOP on the picking view and allow users to search by UOP
* ALCYN-1645: Add `done_date` to stock.picking view
* ALCYN-1563: Update the product categories to add analytic accounts and reimport customer/supplier balance
* ALCYN-1600: Improve stock export to make multiple calls to the ESB based on max_record
* ALCYN-1651: Allow picking with barcode for material

**Bugfixes**

* ALCYN-1656: Add missing access rule on the model account cutoff lines for employees
* ALCYN-1595: Define helpdesk.ticket team_id context according to calling model
* ALCYN-1643: Fix main_exception_id not found in parent view
* ALCYN-1644: Fix typo on consignment report
* ALCYN-1655: Fix a bug when the user try to print a delivery split on a picking not linked to an order
* ALCYN-1631: Fix product import on PIM for product with warning_info too long
* ALCYN-1664: Fix tax required (rule was not applied on invoice validation)
* ALCYN-1652: Delivery Note must always display the "numero de depot"
* ALCYN-1566: Align Partner Display on delivery slip (also fix entry register)
* ACLYN-1666: Fix 'Acheté Vendu' in flux product (ESB)

**Build**

* Add tasks/local_requirements.txt to install libs required for project specific invoke tasks


10.28.0 (2018-11-21)
++++++++++++++++++++

**Data Migration**

* Update full csv data from DB2 prod server at 2018-11-20 16:00:00


10.27.4 (2018-11-20)
++++++++++++++++++++

**Data Migration**

* ALCYN-1604: Cleanup old bins, old "new" routes info and supplier info
* ALCYN-1619: Delete purchase orders when all lines were deleted.
* ALCYN-1622: Adapt setup and migration for "Aliments" chaotic storage
* ALCYN-1624: Fix regexp used to detect nine-ish value implemented for ALCYN-417 for indicated_price

**Features and Improvements**

* ALCYN-1596: Consider consignement flag on sale order report
* ALCYN-236: Add sale warning for human medicine and cascade import product
* ALCYN-253 helpdesk: mail templates
* ALCYN-1455: Add the price on the delivery slip report and add a field on partner to hide these prices
* ALCYN-1636: Duplicate ir.cron connector ESB exporting documents zip
* ALCYN-1637: Install OCA financial reports
* ALCYN-1617: Delivery round. Separate partner list locking and picking launching
* ALCYN-337: Set some parameters for alcyon delivery carrier
* ALCYN-1612: Change customer and customer address export for customer chapeau (ESB)

**Bugfixes**

* ALCYN-1633: display chapeau traceback
* ALCYN-1607: Take care of the delivery carrier when picking is assigned (reserved) for the delivery round instance selection
* ALCYN-1600: Fix bug with customer addresses. But as well change timestamp failesafe.
* ALCYN-1460: Fix sale exception customer backorder, if the quantity on the line is zero it should not be raised
* ALCYN-264: Fix psychotrope sale exception on wrong category (supefiant)
* ALCYN-1632: Products are not sent to the parking according to the zone forced on the product
* ALCYN-1600: Fix split export of stock, take in basic failsafe locking into account


10.27.3 (2018-11-19)
++++++++++++++++++++

* Moved to 10.27.3


10.27.2 (2018-11-12)
++++++++++++++++++++

**Data Migration**

* ALCYN-1541: Set suite name on sale orders when customer is veterinary.

**Features and Improvements**

* ALCYN-1504: Display the intrastat table inside the main table (with products) to avoid break page for small invoice
* ALCYN-62: Add translations on Dutch for reports
* ALCYN-1576: ALCYN-1576: Remove customer/supplier balances import. Balances will be imported later (after go live)
* ALCYN-1540 : For sale order from the web recover the suite_name from the received data (ESB)
* ALCYN-1218: Set a default price on new promotion and add some constrains on promotions
* ALCYN-1614: Update the balance for customers and suppliers + update mandats
* ALCYN-1600: Add a maximum of record that can be exported to a web service when ran from a cron, this is to improve the stock status update (ESB).
* ALCYN-1612: Fix customer address export for is also delivery invoice address for customer 'chapeau'

**Bugfixes**

* ALCYN-1566: Align Partner Display on reports + screen
* ALCYN-1589: Allow to mark a partner of both type invoicing and delivery
* ALCYN-1524: Reload helpdesk.ticket.reason datas from specific_helpdesk

**Build**

* pin pip requirements
* Add Mailhog container for mail testing in dev environment
* Define server_environment for mailhog for dev and integration environments


10.27.1 (2018-11-05)
++++++++++++++++++++

**Data Migration**

* ALCYN-1568: Fix delivered and invoiced quantities on partially delivered and expired sale orders.
* ALCYN-1568: Set canceled quantities on partially delivered and expired sale orders.
* ALCYN-1581: Fix delivered quantities in the history of closed orders
* ALCYN-447: Add a menu to edit the pricelist (sale price 2)

**Features and Improvements**

* ALCYN-1563: Add products account analytics tags and accounts
* ALCYN-1571: Force to update the module specific_followup for update followup templates
* ALCYN-1574: Add missing translations for the module specific_report and use the right tag to translate the invoice report
* ALCYN-1564: Add the SEPA Creditor Identifier of Alcyon to be able to generate the payments file
* ALCYN-1228: Hide the field "US Code" in the view product.template. This field duplicate the field Intrastat
* ALCYN-459: Add a warning on sale order lines for a product 'Acheté-Vendu'
* ALCYN-1516: Change default language of new partners to "French (BE)"

**Bugfixes**

* ALCYN-1562: Fix settings_lot_base_date song not setting the value


10.27.0 (2018-10-26)
++++++++++++++++++++

**Data Migration**

* ALCYN-1552: Fix a bug in location assignation on pickings generated by imported orders.
* ALCYN-75: Update price lists
* ALCYN-98: fix that reverse alert_date and removal_date on lots
* ALCYN-1554: Fix an issue in shippings with additional products being added on imported sale orders
* ALCYN-1485: SO import - Fix error in shipping backorders grouping by partners
* ALCYN-481: Set "Belgium Only" on products for given list and remove previous
* Update full csv data from DB2 prod server at 2018-10-25 18:00:00

**Features and Improvements**

* ALCYN-1495: Add the entry register report just after the delivery report (only if required)
* ALCYN-1544: Improve response time of customer 2 years stat web service (ESB).
* ALCYN-1542: Add import of code intrastat
* ALCYN-1535: Add veterinary references on product labels
* ALCYN-1555: Add invoke tasks for the connector ESB.

**Bugfixes**

* ALCYN-1557: Security. Allow Inventory User to cause SO cost line without requiring sales rights
* ALCYN-1559: Security. Allow Sales User to reassign delivery to another delivery round
* ALCYN-1522: Fix invoice generation automatic validation
* ALCYN-1560: Delivery round kanban wrong button label (print delivery round instead of print invoices)
* ALCYN-1561: Fix the quantity send by the ws product quantity. Quantity must be the available one not the physical one.


10.26.0 (2018-10-22)
++++++++++++++++++++

**Data Migration**

* ALCYN-1532: add tools to disable MTO for the duration of the import
* ALCYN-1508: Set 0 prices and special journal on migration purchase invoices.
* ALCYN-1514: New imported field sale_channel on sale orders
* ALCYN-1525: Create migration sale invoices with dedicated journal and prices to zero.
* ALCYN-98: recompute all production lot alert_date and removal_date
* Update full csv data from DB2 replication server at 2018-10-19 18:00:00
* Fix parner titles, give proper references (XMLID with __setup__) to the tiles
  plus recreate and reassign those titles which were lost during last 'update base'
* ALCYN-1551: Add the possibility to reset the special promotion and buyx gety flux with a script.

**Features and Improvements**

* ALCYN-1024: Re-send sale order to ESB when the back order quantity of one line has changed.
* ALCYN-1536: Display quant supplier for products to return to supplier
* ALCYN-1538: Delivery round state change for long term deliveries.
* ALCYN-65: Add a button on the purchase order to allow a purchase user to compute additional lines by himself. Don't recompute additional lines when the PO is validated.
* ALCYN-1420: Cash on delivery. Allow to delivery by customer
* ALCYN-1216: Update translations for terms used in the view res.partner
* ALCYN-58: Load delivery rounds setup as defined on 2018-10-18 and customer mapping as of 2018-08-10.

**Features and Improvements**

* ALCYN-58: Add tags on delivery rounds templates to support current setup

**Bugfixes**

* ALCYN-410: Fix helpdesk ticket not with a sequence as name when created from backorder wizard
* ALCYN-1543: Fix product_type in customer form statistique (ESB), the param and the return value must use full word MAT is materiel.
* ALCYN-1546: Fix stock export, export the quantity immediately usable not the physical one.


10.25.4 (2018-10-15)
++++++++++++++++++++

**Data Migration**

* ALCYN-74: Set new APB tax on products
* ALCYN-455: Set BO to zero on imported sale orders.
* ALCYN-1515: Fix import creation of orderpoints when importing values of stock min/max on products
* ALCYN-1485: Fix grouping errors due to paralllism, there is still an issue of duplicates which will be adressed in a second fix.
* ALCYN-1485: Fix grouping errors due to paralllism, create jobs that will be executed at end of sale order import.


**Features and Improvements**

* ALCYN-429: Add Autorisation/APB Fields to res.partner and account.view_partner_property_form
* ALCYN-1460: Add a sale exception for customer that do not want back order.
* ALCYN-1530: Install the module product_analytic from akretion
* ALCYN-221: Add on sale order line a warning exception message if it will include a some promotional products.
* ALCYN-1462:
  * Add module stock_lot_loss to be able to change a lot operation during a picking (used by Zetes)
  * Add a voice identifier (3 letter) on a the lot label and adapt the lot label to add the voice identifier
  * Adapt Zetes to indicate to the operation which lot he must take and offer the possibility to change the current lot in an operation
* ALCYN-432: Improve the responsiveness of the customer stat form web service, by implementing the fetching of data with a sql query (ESB)
* ALCYN-1497: Add sequence (INV/######) and a note on inventory. Modify the view list of inventory to add some details.

**Bugfixes**

* ALCYN-1519: Disable procurement_order cron with noupdate.
* ALCYN-1528: Search partner by ref. Search on ref with exact match and return matched code at first

**Build**

* Use Dockerimage: 3.0.0
* Update base odoo src to include latest security build


10.25.3 (2018-10-08)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-1496: Create a new route in the connector ESB to retrieve the stock with SKU. I decided to not use the existing route because we need to be able to retrieve all stocks (filtered by user).
* ALCYN-1461: Manage packaging during reservation. Reserve in priority nearly entire pallet, box, shrink-wrap instead of fefo when applicable
* ALCYN-1487: Add the possibility to have sale exception as warning only. When a sale order line raise a warning some additional information is added to the description of the line.
* ALCYN-236: Add on the sale order line for psychotropic product a specific warning message. And a sale exception when thos product are order through the phone.

**Build**

* ALCYN-1511: Remove stock_picking_invoice_link from migration and uninstall


10.25.2 (2018-09-28)
++++++++++++++++++++

**Data Migration**

* ALCYN-1485: Fix grouping errors due to paralllism, there is still an issue of duplicates which will be adressed in a second fix.

**Features and Improvements**

* ALCYN-1491: Remove copy from suite_name(SO) and ref(partner)
* ALCYN-1517: Recompute pack operations of a picking for 1 product. Required in case a reserved lot is (partially) physically missing. For Zetes integration
* ALCYN-70: Import product name translation

**Bugfixes**

* ALCYN-1520: Fix connector_esb test, test export sale order was not called by Travis


10.25.1 (2018-09-24)
++++++++++++++++++++

**Data Migration**

* ALCYN-461: Force picking zone as "Frigo" wasn't set on products, this correct creation of pickings using "Frigo" Route
* ALCYN-481: Set "Belgium Only" on products for given list and remove previous
* ALCYN-1494: Fix a regression introduced by ALCYN-465 that was generating errors in imports of sales and purchases
* ALCYN-1485: SO import - Group shipping backorders by partners
* ALCYN-126: On import switch discounts when both are set, or when product has GMA price category
* ALCYN-1500: Create a migration location for a fake stock to use as a source on imported Sale orders

**Features and Improvements**

* ALCYN-1445: Add unittests for the API NewPharma
* ALCYN-1490: Invoice report (pdf): display suite name and customer if different from invoice address
* ALCYN-107: Adapt chart of accounts (remove useless accounts, rename 3 accounts and create 12 new accounts)
* ALCYN-153: Always display the field Opt-out (opt_out) on the view res.partner
* ALCYN-1482: Improve performance for the reception of products

**Bugfixes**

* ALCYN-1492: Fix error on customer action duplicate.
* ALCYN-1503: Fix Picking Force availability does not move a quant
* ALCYN-1512: Module declaration should be named __manifest__
* ALCYN-1509: Fix flux promotion Alcyon, code for all other product is different than previously specified (ESB).

**Build**

* Improve unit test speed by using SavepointCase instead of TransactionCase
* Improve test coverage reporting by filtering `*/tests/*` and `*/__manifest__.py`


10.25.0 (2018-09-14)
++++++++++++++++++++

**Data Migration**

* Update full csv data from DB2 Production server at 2018-09-14 12:00:00
* ALCYN-98: Set production lot alert date and removal date
* ALCYN-481: Set "Belgium Only" on products for given list
* ALCYN-1475: Don't create purchase orders when importing sale orders

**Features and Improvements**

* ALCYN-196: Rename the payment method "Manual" by "Domiciliation" and "Virement" by "Virement Manuel"
* ALCYN-195: Add promotional product just after their corresponding product in the sale order lines sequence.
* ALCYN-471: Add the legal note from fiscal position on the invoice report
* ALCYN-1445: Modify the existing ESB connector to add a new API for the wholesaler NewPharma (a route to retrieve the stock, send a command and get the status of this command)

**Bugfixes**

* ALCYN-1484: At reception, MTO pickings in backorders are not assigned to delivery round
* ALCYN-1483: Cannot cancel SO with accessories. Fix error missing record in recordset.
* ALCYN-1454: Update report delivery slip and fix a bug with the report passport
* ALCYN-1486: Enable group shipping, to have only 1 OUT shipping per delivery (for Alcyon delivery only; not for specific carriers)
* ALCYN-1479: Fix the filter on which records are exported in the customer flux (ESB)

**Build**

* Upgrade from odoo-template to add Dangerfile fixes


10.24.1 (2018-09-10)
++++++++++++++++++++

**Data Migration**

* ALCYN-465: On update of orders delete lines which are tagged from AS400 (this requires first to launch the script to detect deleted lines)
* ALCYN-465: For all lines tagged as deleted on AS400 check if the order line exists and force recomputation of the order if it does
* ALCYN-1474: Fix purchases imported and closed which created unwanted pickings

**Features and Improvements**

* ALCYN-1449:

  * Fix a bug (set the right name) with the additional line (product with an additional product) in a purchase order
  * Remove lines with a quantity == 0 in the purchase order report.
* ALCYN-143: Show a warning "Narcotic voucher is required" when such product is ordered
* ALCYN-1417: Fix ESB connector following addition of customer hierarchy
* ALCYN-1432: Create the tax 100 outside EU
* ALCYN-1433: Archive outside EU taxes (21, 12%, 6% and 0%)
* ALCYN-1434: Update tax "TVA à l'entrée 0% Hors EU EXTRACOM - Approvisionn. et marchandises"

**Bugfixes**

* ALCYN-1469: Fix zero/falsy value in product export and convert the volume in the required unit of measure (ESB)
* ALCYN-1468: Add a missing ir.model.access for queue.job (raise an error when an user tried to validate a sale order)

**Build**

* Upgrade project to 10.0-2.7.0
* Upgrade from odoo-template


10.24.0 (2018-09-03)
++++++++++++++++++++

**Data Migration**

* Update full csv data from DB2 Production server
* Update mandates with a file generated by Catherine (10/08/2018)
* ALCYN-159: Fix undone picking stuck without backorder creation for purchase order import due to stock.backorder.choice wizard
* ALCYN-89+ALCYN-409: Unreserve all backorders created by import of sale orders and purchase orders

**Features and Improvements**

* ALCYN-386: Remove useless information and change french label in SO tree view
* ALCYN-74: Create APB tax for 2018, and increase decimal prectision to 5 digits
* Upgrade curl docstring to latest data from smile

**Bugfixes**

* ALCYN-1438: skip ESB export of sales orders without lines, they are refused by the ESB
* ALCYN-1436: orders created from ESB must have 'web' sale channel
* ALCYN-1437: sales orders created from ESB correctly compute the discount field on lines
* ALCYN-1439: Do not export sales to Magento if they are not yet confirmed
  (handle not only 'draft' state, but also 'sent' and 'background confirm')
* ALCYN-1441: allow dulication of already exported sales orders
* ALCYN-1441: never copy references to the ESB when records are duplicated
* ALCYN-13: Accounting cut-off: add two pending merges (#70 and #73) from OCA/account-closing
* ALCYN-439: updates of non-web orders pushed to Magento correctly changes lines on Magento
* ALCYN-1446: on /connector_esb/statistics/form, make only the customerErpId field mandatory, others are optional


10.23.3 (2018-08-29)
++++++++++++++++++++

**Data Migration**

* ALCYN-1421: Migration of bad payers that must pay at order
* ALCYN-1422: Fix sale import without found fiscal position
* ALCYN-450: Skip ESB update on inital product csv import
* ALCYN-416: Fix history of imported sale orders setting the right invoice address
* ALCYN-132: Fix mapping for pricelist on partners
* ALCYN-451: On sale order import, skip jobs to create draft invoices
* ALCYN-417: on products set to 0 indicated_price filled with nine-ish values.
* ALCYN-404: Close Purchase orders older than 120 days

**Features and Improvements**

* ALCYN-1419: Manage sales prepayment (bad payers)
* ALCYN-163: Add a reception wizard for the dropshipping of human drug packs
* ALCYN-491: Add an Anthem song to be called manually for setting up the ESB cron jobs after the data migration.
* ALCYN-173:

  * Enable the flag "Expects a Chart of Accounts" on the company
  * Install the module account_chart_update (OCA - account-financial-tools) to create new taxes later (if needed)
  * Create a song to create new Antibiotic taxes
* ALCYN-464: Remove the supplier_promotion_allowed flag to the purchase order
* ALCYN-1431: Customer Rank on Delivery Round instance x1000

**Bugfixes**

* ALCYN-243: Serial number must be encoded/visible only on delivery orders
* ALCYN-125: Fix partner contact ref
* ALCYN-1423: Fix error singleton printing multiple sale order
* ALCYN-1428: Fix a bug with the procurement. The method to compute promotion defined all quantity to 1.
* ALCN-1428: Stock: Set destruction source location

**Build**

* Disable git-lfs on travis tag builds


10.23.2 (2018-08-22)
++++++++++++++++++++

**Data Migration**

* ALCYN-1412: Imported sale orders are considered done is older than 120 days even if partially delivered.
* ALCYN-457: Fix TypeError in purchase import jobs
* ALCYN-457: Add non regression tests on purchase import

**Features and Improvements**

* ALCN-1189/ALCYN-338: Add fax service and send sale order confirmation through it, if sale channel is fax.
* ALCYN-184: Add `web` to sale_channel. Remove sale_channel_invisible.
* ALCYN-449: Set a default bin_checksum, set the bin_checksum_2 and update parking locators
* ALCYN-448: Fix duplicating sequences in sale_order lines on additional products
* Update sample data: bis repetita placent

**Bugfixes**

* ALCYN-348: Add missing sales BO route to push a line in BO from SO
* ALCYN-1418: Fix SQL request if no partner. Allow delivery address in itinerary
* ALCYN-484: Customer/Suppliers with parent company cannot be searched as customer/supplier
* ALCYN-399:

  * Fix the situation with more than one sale order confirmation being saved in ir attachment
  * Fix an error when printing multiple invoice (see error in queue jobs logs)
* ALCYN-411: Add new search fields for helpdesk.ticket
* ALCYN-482: Format order min/max on the import of products to avoid incorrect min/max value (eg: 500.000 must be 500 and not 500K)
* ALCYN-488:

  * Display lots on product.product and product.template
  * Fix a bug on the query to compute lot to archive. No lots was archived
  * On lots change ref to product quantity
* ALCYN-486: When creating a new sale order coming from the web service, make sure it is set with the appropriate default values (calling the existing onchange methods)
* ALCYN-489: Change web service stock/product so it understand array how skus are sent in parameters
* ALCYN-467: Use jobs to update promotion on purchase orders when the procurement is running
* ALCYN-480: Fix sale exceptions, improve restriction on ordering medicine and veterinary products for customer with undefined Alcyon category


10.23.1 (2018-08-15)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-384: Track who forced the delivery round on a shipping
* ALCYN-385: Set SO sequence padding to 7 digits
* ALCN-1386: Confirmation par email de la livraison client
* ALCN-1226: Push product on sales order in backorder
* ALCYN-436: Improve web service new sale order from Magento, splitting job using confirm in background job.
* ALCN-757: Accounting cut-off

**Bugfixes**

* ALCYN-435: Fix random error in test on connector_esb when testing filename
* ALCYN-420: Fix rapport Invoice/Credit note: apb, layout, ref payment
* ALCYN-489: Add debugging log for stock and sale order web service (ESB)
* ALCYN-378: Fix delivery round picking counter
* ALCYN-380: Allow to deliver even if all pickings are not available
* ALCYN-382: Print partner note on delivery round document + add button in kanban
* ALCYN-415: Cannot make invoice for customers having a ref <100
* ALCYN-419: Fix Delivery round delivery address and rank


10.23.0 (2018-08-10)
++++++++++++++++++++

**Data Migration**

* ALCYN-403: ungroup picking created on final confirmation of imported sale orders from DB2
* ALCYN-166: Set "Belgium Only" on products for given list
* ALCYN-446: Fix KeyError 'odoo_id' in purchase import jobs, purchase lines without product code
             weren't fully skipped.

**Features and Improvements**

* ALCYN-80: Display suite name on SO view and report
* ALCYN-416: Allow to set type on partner without opening master and editing contacts'
* ALCYN-416: Link affiliate to partners and change types of partners.
* ALCYN-434: Create 3 Reception users. These users will be assigned later to a specific printer.
* ALCYN-428: On web service returning xml data, set the content-type to text/xml (ESB)

**Bugfixes**
* ALCYN-431: User mciolii must be mciolli

* ALCYN-405: Display `Numéro d'inscription`(`Subscription number`) field for
  Alcyon category = `Etudiants et assimilés sans dépôt`
* ALCYN-418: Fix CSV delivery note not generated when delivery round is delivered
* ALCYN-121: Fix a bug when the user try to print the reception report
* ALCN-1418: Final fix for the infamous 10 != 8 bug in tests
* ALCYN-437: Fix concurent access on sale order export (ESB)
* ALCYN-398: Fix zip document filename being exported (ESB)
* ALCYN-433: Fix document filename "note d'envoi" by changing res_partner.ref instead of id
* ALCYN-441: Fix prices with/without tax on sale order line send to web service (ESB)
* ALCYN-430: Fix delivery fee web service remove an xml node.
* ALCYN-161: Fix product export (ESB)
    * Make sure that gesfou is nerver empty but as zero by default.
    * Make sure that gescgr and gescsg are always an integer.


10.22.5 (2018-08-06)
++++++++++++++++++++

**Features and Improvements**

* ALCYN-383: Add unicity constraint on sale order esb reference. This prevents duplicates of sale order when web
  service is stressed with multiple create call for the same sale order.

**Bugfixes**

* ALCYN-393: Fix write_date not getting changed on partner, when discount_pricelist_id is changed
* ALCYN-400: Fix empty file on export documents.zip ESB
* ALCYN-396: Fix error on deleting multiple partners (customer)
* ALCYN-414: Fix account_invoice report filename, being exported. The two first letter are 'fc' for an invoice 'nc' for credit note and 'cf' confirmation order.
* ALCYN-395: Change lock mechanism when exporting records (ESB)
* ALCYN-401: Fix customer_id in export of sale order to Magento


10.22.4 (2018-07-31)
++++++++++++++++++++

**Data Migration**

* ALCYN-83: Change supplier payment mode mapping, value 1 from AS400 is for "Domiciliation"

**Features and Improvements**

* ALCYN-188: Improve apb tax calculation on sale order export ESB, by using the tax set on products and not the value set in the invoice.
* ALCYN-130: Set the partner default delivery carrier on web service create sale order if it is not specificed in data (ESB)

**Bugfixes**

* ALCYN-120: Fix missing timestamp kind on export of product when running from cron ESB
* ALCYN-120: Fix error when locking multiple records on ESB stock export
* ALCYN-115: Fix saleorder creation when address has ref from partner
* ALCYN-127: Fix document zip export when ir_attachment has no data.
* ALCYN-123: Process sale order confirmations jobs sequentially. Need this configuration in the deployment:
             ``root.background.sale_confirm:1:sequential`` to add in ODOO_QUEUE_JOB_CHANNELS
             The ODOO_QUEUE_JOB_CHANNELS configuration must set the channel for
             this job as "sequential", so they are processed in order of
             creation, even if jobs are retried.  If a job fails, the others
             jobs will wait.
* ALCYN-124: Store the original sales order confirmation date when confirmed in background


10.22.3 (2018-07-23)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1355: Block product quick create
* ALCN-1407: Add product stock synchronization when state is changed (ESB).
             The export of stock status to the ESB is scheduled by cron and based on
             the stock_quants. But in the data the state of the product is sent
             as well and then not always updated. Here we add a realtime export when
             a product state has been changed.
* ALCN-1435: Change the color for product in BO in the view tree of purchase order and in the view purchase review
* ALCN-1456: Add field Gescov with a fixed value to allow for testing while waiting for a resolution for this issue (product ESB).
* Update users list with new groups assignment
* Define the default purchase manager for ZelAppro import

**Bugfixes**

* ALCN-827: Do not exclude reserved quants from views. Exclude in Zetes.
* ALCN-1406: Internal Transfer: Do not compute product putaway on fixed location otherwise destination is always product's locator
* ALCN-1413: On client: name_get itinerary: include tags + align colors between tags and kanban
* ALCN-1444: Compute promotion when the procurement is running
* ALCN-1448: Rename "End of Life" by "Expiration date" and display lots in a product
* ALCN-1454: Fix delivery rounds plan generation error
* ALCN-1455: Fix new sale order exported with status empty in xml (ESB)
* ALCN-1458: Reception: cannot process products without lot + life date is not reset
* ALCN-1460: Fix a bug when a picking is partially received which was blocking validation of picking
* ALCN-1461: In product price xml send Msrp node even when equal to zero (ESB).


10.22.2 (2018-07-17)
++++++++++++++++++++

**Data Migration**

* ALCN-1073: import claims from DB2
* ALCN-1417: moved sale line unavailable functionality to the basic sale lines view
* ALCN-1277: Import invoice frequency and invoice type from DB2
* ALCN-1400: Delay a job to create when a picking is validated (only for partner invoiced by delivery)
* ALCN-1278: Import customer invoice sending method

**Features and Improvements**
* ALCN-1278: Invoice sending method
* ALCN-1400: Invoice copies. Allow to generate multiple copies of the invoice in the pdf.

* ALCN-1104: Add missing translations and remove the module specific_translations
* ALCN-1452: Add sale order esb_ref (Magento order n°) to the view
* ALCN-1415: Improve esb export so records being updated while an export is running will not be missed on next export.
             The scheduled exports to the esb are run with queue_job.
* ALCN-1442: Sale order in draft state are not to be exported to esb/magento.
* ALCN-1440: Add some required fields for customer invoicing and delivery addresses, so they can be sent to the ESB.
* ALCN-1409: For invoice do not save pdf in ir.attachment table if invoice in 'draft'
* ALCN-1441: On newly created sale order received by the web service, set the current time as the confirmation_date.
* ALCN-1245: Import the initial customer and supplier balance

**Bugfixes**

* ALCN-1418: Fix for the infamous 10 != 8 bug in tests
* ALCN-1452: Fix bug with AddressId in customer address export
* ALCN-1419: potential fix for the 90 != 100 bug,
  if returns i added  debug info to test

**Build**

* Upgrade Dockerimage to 2.6.1
* Update from odoo-template
* Upgrade nginx to X-1.3.0


10.22.1 (2018-07-04)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1116: Add the module CSV File Export and CSV File Import
* ALCN-1428: Stock: Do some small improvements from J.-E. Feedback: Set the right default location on scrap locations and define the location on the scrap model
* ALCN-1358: process confirmation of sales order in background
* Limit multiple job creation for the same update on a sale order.
* Install monitoring_status. Previously it has been manually installed and we want to keep it
* ALCN-1379: Remove taxes from SER-705008 accounting products
* ALCN-1403: Zetes: ignore pickings who contain inventoried products
* ALCN-1421: Add missing Antibiotic taxes in the external module l10n_be_antibiotic_tax


10.22.0 (2018-07-02)
++++++++++++++++++++

**Data Migration**

* ALCN-1205: copy create_date from product_product to parent object product_template to be coherent.
             Creation date of product is imported already but the value needs to be available not
             only on variant but also on product templates. Because all used views are product template,
             exporting products to a csv file would give you only the wrong date.
* ALCN-1309: reset inventory line
* ALCN-1363: import suppliers contacts

**Features and Improvements**

* ALCN-1171: generate sales order and invoice reports in background jobs to reduce the user's time taken at confirmation
* ALCN-1232: Anticipated picking. In delivery rounds, add pending state, remove obsolete name field. On delivery rounds' pickings, display picking type. Zetes: Allow to assign a picking to an operator and send to voice even if delivery round is not started
  * Reorganize the view supplier info to group fields by domains (sale, purchase, ...)
  * add additional lines when a purchase order is validated
* ALCN-1358: Add indexes and optimizations for faster operations
* ALCN-1372: Reorganize the view supplier info to group fields by domains (sale, purchase, ...)
             add additional lines when a purchase order is validated
* ALCN-1401: Add the module stock_inventory_products to allows to create an inventory from a list of products and automatically create inventory lines with lots
* ALCN-1411: Add missing security rules for cron.delivery.plan and round.tag


**Bugfixes**

* ALCN-1392: Delay only one export job when creating / modifying a sales order
* Fix erroneous backend timestamp and kind

**Build**

* Refresh full data


10.21.1 (2018-06-20)
++++++++++++++++++++

**Features and Improvements**

* ALCN-1291: In sale report remove header payment_term and vendor
  and add NL translations
* ALCN-1332: Add a script to import customer banks accounts and madats
* ALCN-1225: Add a serial number on stock move and display this serial number in the delivery slip
* ALCN-1350: Split a CODA file by statement and ignore statements with an account not managed by Alcyon.
* ALCN-1116: Add the module CSV File (this is a generic module)
* ALCN-1404: Update followup letter and update translations
* Purchase review: Add the ordered quantity in the advised quantity and disallow to edit the min/max for MTO product
* ALCN-1427: Refactor reception wizard helpdesk (moved code to specific_helpdesk), filter reasons in reception wizard, allow to set scrap location on reception wizard, translate reasons

**Bugfixes**

* ALCN-1426: Add missing Inputmask library
* ALCN-1424: Fix filename for esb export product and fix invalid esb_ref in product category (business unit)

**Build**

* Add the repo connector-interfaces from OCA and install the module base_import_async


10.21.0 (2018-06-13)
++++++++++++++++++++

**Data Migration**

* ALCN-1287: Filter taxes by fiscal position on purchase orders
* ALCN-1366: Disable computation of promotional products on confirm imported SO

**Features and Improvements**

* ALCN-1319: Replace the legal entity by a relation field and create the new model legal.entity
* ALCN-1321: Replace orderpoint computed fields on product by a simpler field and update the order point by a constrains
* ALCN-1408: Setup delivery carriers fees

**Bugfixes**

* ALCN-864: Fixing the csv document generated as a delivery note by improving float number format and adding no suite, lot name, tax amount.
* ALCN-1420: Fix sale order export to esb: Verify prices default to 0, fix delivery carrier esb_ref, communication channel default to phone

**Build**

* ALCN-1394: Disable the module account_sepa (enterprise) and install the module l10n_be_iso20022_pain
* Deactivate all crons jobs


10.20.3 (2018-06-12)
++++++++++++++++++++

**Bugfixes**

* Add missing file of 10.20.2


10.20.2 (2018-06-08)
++++++++++++++++++++

**Data Migration**

* ALCN-1303: Filter sale order of type 2 which are credit notes (remove already imported one which are 'draft' or 'done')
* ALCN-1305: Add importation product of length, width, depth
* ALCN-1306: Set received quantities on purchase lines, take the value from actually received qty instead of ordered
* ALCN-1310: Import the payable account on suppliers (this replaces the mapping for categories)
* ALCN-1317: Add missing delivery addresses which were only in schema GENDATA in DB2
* ALCN-1326: Fix mapping of product weight
* ALCN-1330: Following Revert of ALCN-1153 restore importation of standard_price
* ALCN-1340: Recompute alert and removal dates on lots based on life date
* ALCN-1385: Fix broken update of Purchase order in final mode for in progress states
* ALCN-1357: Import antibiotic taxes on products
* ALCN-1341: Raise sequence on unbounded supplierinfo to give them a lower priority
             We usually want current seller prices which are bounded in time.
* ALCN-1341: Compute promotions in importer sale order lines
* ALCN-1341: Fix mapping of discount on sale order lines
* ALCN-1402: Import products with category Human as services
* Add created or update record id in "Results" of importer queue jobs
* update suppliers
* update products to introduce types and antibiotic taxes

**Features and Improvements**

* ALCN-1132: Reactivate the Unit Of Measure "liter"
* ALCN-1295: Define the default header/footer for all reports and make some improvements (translations, layout) for the purchase report
* ALCN-1340: Set setting 'base date for product lot' to 'life date'
* ALCN-1364: Add exception rule to prevent SO lines with negative value
* Change date widget in reception screen (remove calendar popup and apply mask)
* Reactivate backorder reasons at reception and helpdesk ticket generation

**Bugfixes**
* Revert ALCN-1153: Set standard buying price in product cost field

**Bugfixes**

* ALCN-1000: Add missing ir.model.access for stock.move.lots and round.instance
* Revert ALCN-1153: Set standard buying price in product cost field
* Recover journal selection at top of invoice form view.


10.20.1 (2018-05-18)
++++++++++++++++++++

**Data Migration**

* Force update of all existing draft orders on final mode
* ALCN-1324: Add missing csv files for relation between customer and master partner.
* ALCN-1327: Fix mapping on clients affecting multiple values, mapping was based on "Statistique" instead of "Activité"
  Changes mapping for promotions, partner categories, alcyon categories and fiscal positions.

**Features and Improvements**
* Make stock inventory menu entry available (was hidden to users)

* ALCN-1299: Add smartbutton "Tickets" on supplier invoices.

**Bugfixes**

* ALCN-1299: Fix crash of smartbutton "Tickets" on invoices. A context wasn't closed properly.
* ALCN-1322: Fix a typo on "Article retiré de la vente" in french
* ALCN-1333: Remove the account number in the name of banks (ING, Belfius, CBC, BNP)
* ALCN-1377: Improve connector esb, catching malformed json response
* ALCN-1384: ESB sale order creation route now expect ref instead of DB id
* Fix labels printing (raw text data cannot be to long on 1 line). Send quantity to printer. Fix product label (no lot) at reception


10.20.0 (2018-05-04)
++++++++++++++++++++

**Data Migration**

* Update full csv data from DB2 Production server

**Build**

* Disable automatic launch of inventory in final_update mode
* May the 4th be with you


10.19.3 (2018-04-28)
++++++++++++++++++++

**Bugfixes**

* Fix environment variable DB2IMPORT_10CLI validity check, it was never valid due
  to wrong boolean operators in test.

10.19.2 (2018-04-28)
++++++++++++++++++++

**Build**

* Release for a fresh start with fixes from 10.19.1


10.19.1 (2018-04-28)
++++++++++++++++++++

This release can only be applied on top of a failed release 10.19.0, use the 10.19.2 instead.


**Bugfixes**

* Replace hardcoded db host by env var in migration steps on copy tables.

**Build**

* Add environment variable validity checks on start of build in order to avoid
  failure at end of build only when environment variables are not set properly.
* Delay tests of specific_sale to avoid random failure depending on the order
  of module loading.


10.19.0 (2018-04-26)
++++++++++++++++++++

**Data Migration**

* ALCN-1036: import supplier raw price instead of net price in supplierinfo
* ALCN-1036: invert import mapping of discount_global and promotion_supplier
* ALCN-1036: set purchase picking date from DB2 header instead of line
* ALCN-1066: Set APB tax on product in categories "Médicament vétérinaire belge" et "Cascade importation"
* ALCN-1070: Set purchase discount on supplier info, take the same value as sale discount for migration
* ALCN-1102: import supplier global discount from DB2
* ALCN-1222: Import customer relation to master customer
* ALCN-1223: Load and Migrate Suppliers Payment Terms. Modify Client Payment Term 'Immediate Payment' to '7 days' during migration.
  ALCN-1223: Load and Migrate Suppliers Payment Modes.
* ALCN-1224: set fiscal position to "Wholesaler without APB" to customer in category "Grossistes vétérinaires et Callcenter"
* ALCN-1233: Set fiscal position on suppliers
* ALCN-1256: Change import customer, some Alcyon category become a Tags on customer
* ALCN-1266: all operations created by in progress pickings now goes to a specific location
  called "[MIGRATION] Réception des achats"
* ALCN-1274: Skip order lines with no product ref as those lines are replaced products
* ALCN-1286: Set purchase with uom from dcfunv with value "1" as "Pièces" for the few cases that were failing

**Features and Improvements**

* ALCN-1187: Add warning (in description and colored line) on sale order line when product out of stock at the supplier
* ALCN-1198: Delay jobs to reserve stock when the daily delivery plan is created
* ALCN-1222: Display master customer on partner form
* ALCN-1271: NL tranlation of warning message of category human drug products.
* ALCN-1288: Compute fiscal position based on country
* Accounting: Do not use refund journals in odoo v10. Drop Wage journal. Fix type of cash journal.
* Allow to send to scrap location at reception
* Align customer return process to reception process. Removed fixme in data setup.

**Bugfixes**

* ALCN-1298: Fix sale order state and confirmation date on creation by web service.
* Fix Belgium Chart of taxes. Code and name have been inverted in v10.

**Build**

* ALCN-1297: db2_import: Add environment variables DB2IMPORT_* to control the db2 importer setup
* db2_import: get sale/purchase history from pre-generated csv files to limit number of querries to DB2

**Documentation**

* ALCN-1297: Document DB2IMPORT_* environment variables


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
  as of 19.01.18 customer wanted this webservice
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
