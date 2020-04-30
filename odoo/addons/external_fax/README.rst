.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
External Fax
============

This module allows to use an external Fax account from OVH to send an
ir.attachment document to a fax number as email.

It is setup to send sale order confirmation by fax for all sale order whose
sale channel is set to 'fax'.

Configuration
=============

The configuration of the fax service must be set in environment variables:

* email domain : ``OVH_FAX_EMAIL_DOMAIN``
* fax number : ``OVH_FAX_NUMBER``
* fax password : ``OVH_FAX_PASSWORD``

Testing
=======

As in development mode the Mailtrap service is used, to do a test sending a real
fax the smtp configuration must be changed in server_environment_files.

Credits
=======

Contributors
------------

* Thierry Ducrest <thierry.ducrest@camptocamp.com>
