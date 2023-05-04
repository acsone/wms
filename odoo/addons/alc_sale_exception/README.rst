==================
Alc Sale Exception
==================

Base module for specific sale exceptions.

Configuration
_____________

Please refer to sale_exception README to configure your user as
Exception manager and be sure to be in developer mode to access the menu item
in *Sales - Configuration - Sale Exception Rules*.

Install also the sale_management addon.

Go to *Settings - Sales - Quotations & Orders* and check the
'Sale Exception Check Enabled'.

Test
----

 * Go to *Sales - Configuration - Sale Exception Rules*
 * Enable the rule "No line under 0"
 * Create a sale order
 * Add a product and set its price < 0
 * Confirm the sale order

You can do something similar for the exception rules "Pas de ligne à zéro" and
"Montant minimum à 100 euros".

