To set the delay time you have three options:

1. Go to inventory settings and set a global delay time for all channels.
2. Set a specific delay by warehouse.
3. Set the delay at the release channel.

At shipment advices creation by the release channel, odoo will consider the channel
delay time first. If isn't set, it will take the warehouse delay configuration.
If both aren't given, the global delay is applied.
