=======================================
Alc Sale Exception Product Availability
=======================================

Adds the sale exceptions specific to product availability.

Configuration
_____________

Please refer to sale_exception README to configure your user as
exception manager and be sure to be in developer mode to access the menu item
in *Settings - Technical - Exception Rules*.

Test
----
Activate the exception rule(s) you want to test and create sale order
accordingly. Here is the example of "Warning provision on order":

 * Go to *Inventory-Configuration-Warehouses* and open "YourCompany" warehouse
 * Click Routes button and select Archived in filters
 * Clic the "Replenish on Order (MTO)" route and then *Action-Unarchive*
 * Go to *Settings - Technical - Exception Rules* and activate the rule
   "Warning provision on order".
 * Create a storable product with "Replenish on Order (MTO)" checked in its routes
 * Create a sale order
 * Add the product you created and confirm the sale order
