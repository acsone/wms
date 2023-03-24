.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Alc GLS Put in Pack
===================

Add a specific wizard for GLS packages.


Tests
=====

- Create a new sale order and confirm it;
- Go to delivery;
- Click the *Put in Pack* button and make sure it is the regular package selection wizard;
- Go to the *Additional Info* tab and choose GLS as carrier;
- Click the *Put in Pack* button again and make sure this time the gls wizard comes up;
- Create a new package from the wizard and click send. In non prod environment this will raise an exception, however the values on the wizard should be set on the newly created package. Go to *inventory/products/package* to make sure it is so;
