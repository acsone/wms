# -*- coding: utf-8 -*-
@alcyon @import

Feature: import master data

  @default_value_product
  Scenario: Default product value
    Given I need a "ir.values" with oid: scenario.product_template_value
     And having:
     | key            | value            |
     | name           | type             |
     | model          | product.template |
     | value_unpickle | product          |
     | key            | default          |
     | key2           |                  |
     | company_id     | by oid: base.main_company_alcyon |     

  @csv @suppliers_import
  Scenario: import specific suppliers
    Given "res.partner" is imported from CSV "setup/suppliers.csv" using delimiter ","

  @csv @product_import
  Scenario: import specific product
    Given "product.template" is imported from CSV "setup/product.template.csv" using delimiter ","