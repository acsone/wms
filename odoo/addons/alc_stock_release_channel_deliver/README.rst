.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Alc Stock Release Channel Deliver
=================================

This module adds an action to the release channel to automate the delivery of
its shippings.

Usage
-----

- A "Deliver" button for locked release channels is added.
- When this new button is clicked:
    - The release channel change its state to "delivering" when the "Deliver".
    - Plan a background task that:
        - Validates the shippings related to the release channel.
        - Creates shipment advices.
        - Processes the shipment advices.
- At the end of the background task:
    - The release channel status pass to "delivered" if no errors are detected.
    - Otherwise, Appropriate error messages are displayed and a button to retry
      is shown to the user.
