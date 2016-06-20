# -*- coding: utf-8 -*-
@alcyon @setup @stock

Feature: Configure stock

  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                    |
        | product_expiry          |

  @activate
  Scenario: activate options in settings
    Given I set "Lots and Serial Numbers" to "Track lots or serial numbers" in "Inventory" settings menu
    Given I set "Multi Locations" to "Manage several locations per warehouse" in "Inventory" settings menu
    Given I set "Routes" to "Advanced routing of products using rules" in "Inventory" settings menu

  @warehouse
  Scenario: delivery pick-ship
    Given I find a "stock.warehouse" with oid: stock.warehouse0
    And having:
      | key            | value        |
      | delivery_steps | pick_ship    |


  @location
  Scenario: location
    Given I need a "stock.location" with oid: __init.stock_location_materiel
    And having:
      | key            | value                              |
      | name           | Materiel                           |
      | location_id    | by oid: stock.stock_location_stock |

    Given I need a "stock.location" with oid: __init.stock_location_ali
    And having:
      | key            | value                              |
      | name           | Aliments                           |
      | location_id    | by oid: stock.stock_location_stock |

    Given I need a "stock.location" with oid: __init.stock_location_medoc
    And having:
      | key            | value                              |
      | name           | Medicaments                        |
      | location_id    | by oid: stock.stock_location_stock |

    Given I need a "stock.location" with oid: __init.stock_location_froid
    And having:
      | key            | value                              |
      | name           | Froid                              |
      | location_id    | by oid: stock.stock_location_stock |

    Given I need a "stock.location" with oid: __init.stock_location_frigo
    And having:
      | key            | value                              |
      | name           | Frigo                              |
      | location_id    | by oid: __init.stock_location_froid|

    # Given I need a "stock.location" with oid: __init.stock_location_congel
    # And having:
    #   | key            | value                              |
    #   | name           | Congel -12                         |
    #   | location_id    | by oid: __init.stock_location_froid|


  @pickingtype
    Scenario: picking type
    Given I need a "stock.picking.type" with oid: __init.stock_picking_type_materiel
    And having:
      | key                     | value                                     |
      | name                    | Pick Materiel                             |
      | code                    | internal                                  |
      | sequence_id             | by name: Alcyon Belux SA Sequence picking |
      | default_location_src_id | by oid: __init.stock_location_materiel    |
      | default_location_dest_id | by oid: stock.stock_location_output      |
      | use_create_lots         | False                                     |

    Given I need a "stock.picking.type" with oid: __init.stock_picking_type_ali
    And having:
      | key                     | value                                     |
      | name                    | Pick Aliments                             |
      | code                    | internal                                  |
      | sequence_id             | by name: Alcyon Belux SA Sequence picking |
      | default_location_src_id | by oid: __init.stock_location_ali         |
      | default_location_dest_id | by oid: stock.stock_location_output      |
      | use_create_lots         | False                                     |

    Given I need a "stock.picking.type" with oid: __init.stock_picking_type_medoc
    And having:
      | key                     | value                                     |
      | name                    | Pick Medicaments                          |
      | code                    | internal                                  |
      | sequence_id             | by name: Alcyon Belux SA Sequence picking |
      | default_location_src_id | by oid: __init.stock_location_medoc       |
      | default_location_dest_id | by oid: stock.stock_location_output      |
      | use_create_lots         | False                                     |

    Given I need a "stock.picking.type" with oid: __init.stock_picking_type_froid
    And having:
      | key                     | value                                     |
      | name                    | Pick Frigo                                |
      | code                    | internal                                  |
      | sequence_id             | by name: Alcyon Belux SA Sequence picking |
      | default_location_src_id | by oid: __init.stock_location_froid       |
      | default_location_dest_id | by oid: stock.stock_location_output      |
      | use_create_lots         | False                                     |


  @procurementrule
    Scenario: procurement rule
    Given I need a "procurement.rule" with oid: __init.procurement_rule_materiel
    And having:
      | key                      | value                                    |
      | name                     | WH: Stock -> Output (MAT)                |
      | action                   | move                                     |
      | location_id              | by oid: stock.stock_location_output      |
      | warehouse_id             | by oid: stock.warehouse0                 |
      | location_src_id          | by oid: __init.stock_location_materiel   |
      | procure_method           | make_to_stock                            |
      | picking_type_id          | by oid: __init.stock_picking_type_materiel |
      | group_propagation_option | propagate                                |

    Given I need a "procurement.rule" with oid: __init.procurement_rule_ali
    And having:
      | key                      | value                                    |
      | name                     | WH: Stock -> Output (ALI)                |
      | action                   | move                                     |
      | location_id              | by oid: stock.stock_location_output      |
      | warehouse_id             | by oid: stock.warehouse0                 |
      | location_src_id          | by oid: __init.stock_location_ali        |
      | procure_method           | make_to_stock                            |
      | picking_type_id          | by oid: __init.stock_picking_type_ali    |
      | group_propagation_option | propagate                                |

    Given I need a "procurement.rule" with oid: __init.procurement_rule_medoc
    And having:
      | key                      | value                                    |
      | name                     | WH: Stock -> Output (MED)                |
      | action                   | move                                     |
      | location_id              | by oid: stock.stock_location_output      |
      | warehouse_id             | by oid: stock.warehouse0                 |
      | location_src_id          | by oid: __init.stock_location_medoc      |
      | procure_method           | make_to_stock                            |
      | picking_type_id          | by oid: __init.stock_picking_type_medoc  |
      | group_propagation_option | propagate                                |

    Given I need a "procurement.rule" with oid: __init.procurement_rule_froid
    And having:
      | key                      | value                                    |
      | name                     | WH: Stock -> Output (FRIGO)              |
      | action                   | move                                     |
      | location_id              | by oid: stock.stock_location_output      |
      | warehouse_id             | by oid: stock.warehouse0                 |
      | location_src_id          | by oid: __init.stock_location_froid      |
      | procure_method           | make_to_stock                            |
      | picking_type_id          | by oid: __init.stock_picking_type_froid  |
      | group_propagation_option | propagate                                |


  @route
    Scenario: route
    Given I need a "stock.location.route" with oid: __init.stock_location_route_pick_materiel
    And having:
      | key                      | value                                    |
      | name                     | Alcyon Belux SA: Pick (MAT)              |
      | product_categ_selectable | True                                     |
      | product_selectable       | False                                    |
      | pull_ids                 | by oid: __init.procurement_rule_materiel |

    Given I need a "stock.location.route" with oid: __init.stock_location_route_pick_ali
    And having:
      | key                      | value                                    |
      | name                     | Alcyon Belux SA: Pick (ALI)              |
      | product_categ_selectable | True                                     |
      | product_selectable       | False                                    |
      | pull_ids                 | by oid: __init.procurement_rule_ali      |

    Given I need a "stock.location.route" with oid: __init.stock_location_route_pick_medoc
    And having:
      | key                      | value                                    |
      | name                     | Alcyon Belux SA: Pick (MED)              |
      | product_categ_selectable | True                                     |
      | product_selectable       | False                                    |
      | pull_ids                 | by oid: __init.procurement_rule_medoc    |

    Given I need a "stock.location.route" with oid: __init.stock_location_route_pick_froid
    And having:
      | key                      | value                                    |
      | name                     | Alcyon Belux SA: Pick (FROID)            |
      | product_categ_selectable | True                                     |
      | product_selectable       | False                                    |
      | pull_ids                 | by oid: __init.procurement_rule_froid    |

  @route_category
  Scenario: Assign route on product categories
    Given I find a "product.category" with oid: __init.product_categ_materiel
    And having:
      | key            | value        |
      | route_ids      | by oid: __init.stock_location_route_pick_materiel     |

    Given I find a "product.category" with oid: __init.product_categ_ali
    And having:
      | key            | value        |
      | route_ids      | by oid: __init.stock_location_route_pick_ali     |

    Given I find a "product.category" with oid: __init.product_categ_medoc
    And having:
      | key            | value        |
      | route_ids      | by oid: __init.stock_location_route_pick_medoc   |

    Given I find a "product.category" with oid: __init.product_categ_frigo
    And having:
      | key            | value        |
      | route_ids      | by oid: __init.stock_location_route_pick_froid     |

    # Given I find a "product.category" with oid: __init.product_categ_congel
    # And having:
    #   | key            | value        |
    #   | route_ids      | by oid: __init.stock_location_route_pick_froid     |
