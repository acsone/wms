=========================
Specific datas for Alcyon
=========================

This module acts as a base module for specific datas required by other specific
modules.

Should specific datas be referenced in a specific module, these datas have to
be loaded here instead of anthem songs or any CSV importation to ensure they
are available at the specific module's installation.

This module shall be added as a dependency in the file __manifest__.py of the
specific module requiring any data it contains.
