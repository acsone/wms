# -*- coding: utf-8 -*-
@alcyon @setup @product

Feature: Configure products

  @category
  Scenario: product categories
    Given I need a "product.category" with oid: __init.product_categ_materiel
    And having:
      | key            | value        |
      | name           | Materiel     |

    Given I need a "product.category" with oid: __init.product_categ_ali
    And having:
      | key            | value        |
      | name           | Aliments     |

    Given I need a "product.category" with oid: __init.product_categ_medoc
    And having:
      | key            | value        |
      | name           | Medicaments  |

    Given I need a "product.category" with oid: __init.product_categ_frigo
    And having:
      | key            | value        |
      | name           | Frigo        |

    # Given I need a "product.category" with oid: __init.product_categ_congel
    # And having:
    #  | key            | value        |
    #  | name           | congel -12   |
