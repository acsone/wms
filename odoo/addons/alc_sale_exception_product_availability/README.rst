=======================================
Alc Sale Exception Product Availability
=======================================

Adds the sale exceptions specific to product availability.

Configuration
_____________

Please refer to alc_sale_exception README for the needed configuration.

Test
----
Activate the exception rule(s) you want to test and create sale order
accordingly. Here is the example of "Warning provision on order":

 * Go to *Inventory-Configuration-Warehouses* and open "YourCompany" warehouse
 * Click Routes button and select Archived in filters
 * Clic the "Replenish on Order (MTO)" route and then *Action-Unarchive*
 * Go to *Sales - Configuration - Sale Exception Rules* and activate the rule
   "Warning provision on order".
 * Create a storable product with "Replenish on Order (MTO)" checked in its routes
 * Create a sale order
 * Add the product you created and confirm the sale order
