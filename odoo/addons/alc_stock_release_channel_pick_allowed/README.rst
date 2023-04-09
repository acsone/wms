.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Alc Stock Release Channel Pick Allowed
==========================

This module allows users to signal their readiness to make picks for a release
channel, either for the entire channel or for a specific type of pick.
The system can also handle this process automatically.

Ho to test?
-----------

To test this module you will need to install `alc_stock_release_channel_dashboard`

- In the operation types (picking types), set to True the checkbox
  `User can allow picking preparation on release channels?` for the outgoing
  types.
- In the release channel menu, you can now see the `speakers` icons that you can
  use to allow or disallow picking.
- If you set to True `Disallow picking automatically`, the system will disallow
  picking for the picking type with the start of the first picking of this type.
  But If you set to sleep the channel, the picking is disallowed for all types.
- If you set to True `Allow picking automatically`, you will need to set
  `Duration before shipment leave to allow picking automatically` so this system
  can compute the when it should allow picking automatically.
  A job for this purpose will be planned at the computed date if the channel is
  set to wakeup.
  If this job is planned, and you change one of the fields that leads to compute
  of `Allow picking automatically at`, the planned job will be set to done with a
  a note and a new one will be planned for the new date.