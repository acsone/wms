====================================
Alc Partner Force Re-Geolocalization
====================================

With this module it is made clear to the user when the coordinates of a customer
need to be recomputed, i.e. when their address changed since the last geolocalization.

Testing
=======

- Go to or create a customer (no b2c). Customer rank is computed, so a customer is any contact who was a customer on a SO;
- Give them an address and geolocalize it in the Partner Assignment tab;
- Change the address: the coordinates will go back to 0 and a warning should appear on top of the contact form indicating you should geolocalize the contact again;