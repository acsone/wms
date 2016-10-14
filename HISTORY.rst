.. :changelog:

Release History
---------------

Unreleased
++++++++++

**Data Migration**

**Features and Improvements**

**Bugfixes**

**Build**

**Documentation**


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
