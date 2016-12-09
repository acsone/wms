.. :changelog:

Release History
---------------

Unreleased
++++++++++

**Data Migration**

* [ALCN-674] Data - Import VAT on customers
* [ALCN-675] Product vat
* [ALCN-676] Don't remove archived product in full data

**Features and Improvements**

* Change default config for default invoice

**Bugfixes**

**Build**

* Use camptocamp/odoo-project:9.0-1.7.1
* Rancher stacks: nginx sidekicks, letsencrypt, db_maxconn

**Documentation**


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
