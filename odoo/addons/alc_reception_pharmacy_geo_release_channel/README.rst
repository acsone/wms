==========================================
alc_reception_pharmacy_geo_release_channel
==========================================

Makes the field is_delivered_by_alcyon compute depending on
stock_release_channel_geoengine which introduces geographic release channels
on the partner.

Test
____

* Set the geographical position of a customer in its geoengine map tab.
* Create a shipping method having the company partner as transporter.
* Create a release channel having this shipping method as transporter.
* Restrict this release channel to delivery zone in its selection criteria tab.
* Then draw a zone containing the customer position on the map in the delivery
  zone tab of the release channel.


You can now make an usual pharmacy reception for the selected customer.
