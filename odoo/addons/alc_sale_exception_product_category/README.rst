===================================
Alc Sale Exception Product Category
===================================

Adds the sale exceptions specific to product category.

Configuration
_____________

Please refer to sale_exception README to configure your user as
exception manager and be sure to be in developer mode to access the menu item
in *Settings - Technical - Exception Rules*.

Test
----
Activate the exception rule(s) you want to test and create sale order
accordingly. Here is the example of "No psychotropic ordered by phone":

 * Go to *Settings - Technical - Exception Rules* and activate the rule
   "No psychotropic ordered by phone".
 * Create a storable product with category "Psychotropes Annexe III"
 * Create a sale order and set the Sale Channel to Phone
 * Add the product you created and confirm the sale order
