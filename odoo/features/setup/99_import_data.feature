# -*- coding: utf-8 -*-
@alcyon @setup @import

Feature: import master data

  @default_value_product
  Scenario: Default product value
    Given I need a "ir.values" with oid: scenario.ir_values_default_product_template_type
     And having:
     | key            | value                     |
     | name           | type                      |
     | model          | product.template          |
     | value_unpickle | product                   |
     | key            | default                   |
     | key2           |                           |
     | company_id     | by oid: base.main_company |
    Given  I execute the SQL commands
    """
    UPDATE ir_values
    SET key2 = NULL  -- key2 must be NULL otherwise the default is not used
    WHERE id in (SELECT res_id FROM ir_model_data WHERE module = 'scenario' AND name = 'ir_values_default_product_template_type')
    """

  @csv @partner_import
  Scenario: import specific clients
    Given "res.partner" is imported from CSV "setup/customer.csv" using delimiter ","

  @csv @partner_import
  Scenario: import specific clients
    Given "res.partner" is imported from CSV "setup/supplier.csv" using delimiter ","

  @csv @stock_bin_import
  Scenario: import locators (stock bin)
    Given "stock.location" is imported from CSV "setup/locators_subset.csv" using delimiter ","

  @csv @stock_output_import
  Scenario: import output locations
    Given "stock.location" is imported from CSV "setup/chariots.csv" using delimiter ","

  @csv @product_import @price_category
  Scenario: import specific product
    Given "product.price.category" is imported from CSV "setup/product.price.category.csv" using delimiter ","

  @csv @product_import @stock
  Scenario: import specific product
    Given "product.product" is imported from CSV "setup/product.csv" using delimiter ","
    Given  I execute the SQL commands
    """
    UPDATE product_template SET active=False WHERE id IN (SELECT product_tmpl_id FROM product_product WHERE not active);
    """

  @csv @product_import @supplierinfo
  Scenario: import specific product supplierinfo
    Given "product.supplierinfo" is imported from CSV "setup/supplierinfo.csv" using delimiter ","

  @csv @product_import @pricelist
  Scenario: import specific product
    Given "product.pricelist" is imported from CSV "setup/product.pricelist.csv" using delimiter ","
