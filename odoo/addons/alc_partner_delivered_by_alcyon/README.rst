===============================
alc_partner_delivered_by_alcyon
===============================

Adds the field is_delivered_by_alcyon on res.partner. The goal is to just
add the field as simple boolean to have it in alc_reception_pharmacy without
any dependance on the geoengine stuff.
Another glue module will make this field compute linked on
stock_release_channel_geoengine.

