# -*- coding: utf-8 -*-
@alcyon @setup

Feature: Parameter the new database
  In order to have a coherent installation
  I've automated the manual steps.

  @no_login
  Scenario: CREATE DATABASE
    Given I find or create database from config file

  @lang
  Scenario: install lang
   Given I install the following language :
      | lang  |
      | fr_BE |
      | nl_BE |
    Then the language should be available

    Given I find a "res.lang" with code: en_US
    And having:
      | key         | value    |
      | grouping    | [3,0]    |
      | date_format | %d/%m/%Y |

    Given I find a "res.lang" with code: fr_BE
    And having:
      | key         | value    |
      | grouping    | [3,0]    |
      | date_format | %d/%m/%Y |

    Given I find a "res.lang" with code: nl_BE
    And having:
      | key         | value    |
      | grouping    | [3,0]    |
      | date_format | %d/%m/%Y |


  @company
  Scenario: SETUP company informations
    Given I need a "res.company" with oid: base.main_company
    And having
       | key                | value                       |
       | name               | Alcyon Belux SA             |
       | street             | Rue le Marais 17            |
       | street2            |                             |
       | zip                | 4530                        |
       | city               | Villers-le-Bouillet         |
       | country_id         | by code: BE                 |
       | phone              | 04/3383490                  |
       | fax                | 04/3382783                  |
       | email              | secretariat@alcyonbelux.be  |
       | website            | www.alcyonbelux.be          |
       | vat                | BE 0421.801.233             |
       | company_registry   |                             |
       | rml_header1        |                             |
    Given the company has the "images/logo-alcyon.png" logo


  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                    |
        # oca/ocb
        | document                |
        | account                 |
        | sale                    |
        | sale_stock              |
        | stock                   |
        | purchase                |
        # OCA/server-tools
        #| disable_openerp_online  |
        # local-src
        | delivery_rounds         |
        | stock_picking_subcode   |
        | product_price_category  |

