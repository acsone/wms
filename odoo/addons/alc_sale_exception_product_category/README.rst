===================================
Alc Sale Exception Product Category
===================================

Adds the sale exceptions specific to product category.

Configuration
_____________

Please refer to alc_sale_exception README for the needed configuration.

Test
----
Activate the exception rule(s) you want to test and create sale order
accordingly. Here is the example of "No psychotropic ordered by phone":

 * Go to *Sales - Configuration - Sale Exception Rules* and activate the rule
   "No psychotropic ordered by phone".
 * Create a storable product with category "Psychotropes Annexe III"
 * Create a sale order and set the Sale Channel to Phone
 * Add the product you created and confirm the sale order
