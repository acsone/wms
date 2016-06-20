# -*- coding: utf-8 -*-
@alcyon @setup @product

Feature: Configure products

  @category
  Scenario: product categories
    Given I need a "product.category" with oid: __init.product_categ_materiel
    And having:
      | key            | value        |
      | name           | materiel     |

    Given I need a "product.category" with oid: __init.product_categ_ali
    And having:
      | key            | value        |
      | name           | aliments     |

    Given I need a "product.category" with oid: __init.product_categ_medoc
    And having:
      | key            | value        |
      | name           | medicaments  |

    Given I need a "product.category" with oid: __init.product_categ_frigo
    And having:
      | key            | value        |
      | name           | frigo        |

    # Given I need a "product.category" with oid: __init.product_categ_congel
    # And having:
    #  | key            | value        |
    #  | name           | congel -12   |
