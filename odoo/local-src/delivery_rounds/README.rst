.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Delivery rounds
===============

Manage delivery rounds.

Each day, you must make your delivery plan listing all delivery rounds.  In
order to perform this, you must create template of delivery rounds and
instanciate them through the wizard "Generate delivery plan".  You can manage
version of delivery rounds templates to maintain multiple list of templates and
select the one you want to instanciate.

A delivery round template contains an ordered list of itineraries. An itinerary
contains an ordered list of partners. On each partner of the list you can set
tags to filter which partner is included when instanciating the plan from the
wizard.

When a sale order is confirmed, available pickings are inserted in matching
delivery rounds. Either a shipping method is selected on the sale order and it
maps to a round template, then the instance of that template is matched
(special deliveries). Either the customer is already included in an existing
delivery round, then that instance is used. Or we find the first delivery round
having the customer in its itineraries.

In any case, pickings that are not available are not included in a delivery
round. However, when the stock of a product is increased (through reception or
inventory), we retry to reserve all pickings containing that product and
include them in a delivery round.

A delivery round has 3 states. When draft, any new picking can be inserted.
When confirmed, no new clients are added but existing clients that are not yet
picked can add more pickings. When it's done, documents are printed and the
truck leaves.

The generation of the delivery round daily plan can be automated in the
configuration. During the night, a cron job will then automatically generate
the plan and reserve the stock. You can manage exceptions for exact specific
days.

This module will create a cron (automatic job) to create delivery daily plan.
You have to configure delivery day in Delivery configuration

Installation
============

To install this module, you just need to select the module and insure yourself
dependencies are available.

Configuration
=============

You must make itineraries and round templates.
Please configure delivery days in Delivery configuration.


Known issues / Roadmap
======================

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
* Sylvain Van Hoof <sylvain@okia.be>
* Julien Coux <julien.coux@camptocamp.com>
