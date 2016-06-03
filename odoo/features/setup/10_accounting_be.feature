# -*- coding: utf-8 -*-
@alcyon @setup @accounting

Feature: Configure accounting

  @csv @banks
  Scenario: import banks
    Given "res.bank" is imported from CSV "setup/res.bank.csv" using delimiter ","

  @company_currency
  Scenario: Configure company currency
  Given I find a "res.company" with oid: base.main_company
    And having:
      | key         | value        |
      | currency_id | by name: EUR |

  @activate_multicurrency
  Scenario: Configure multicurrency
    Given I enable "Allow multi currencies" in "Invoicing" settings menu

  @account_chart
  Scenario: Generate account chart for Alcyon Belux SA
    Given I have the module account installed
    Then accounts should be available for company "Alcyon Belux SA"

  # optionally, delete accounts and journals. We might also want to create new ones
  # or we might import a full chart of account as CSV
  # @banks
  # Scenario: Remove default Bank and Cash accounts
  #   Given I find a "account.account" with name: Bank
  #   And I delete it
  #   Given I find a "account.account" with name: Cash
  #   And I delete it

  # @journal
  # Scenario: Remove default Bank and Cash journals
  #   Given I find a "account.journal" with name: Bank
  #   And I delete it
  #   Given I find a "account.journal" with name: Cash
  #   And I delete it

  @bank_account
  Scenario Outline: Create account for Alcyon Belux SA bank
    Given I need a "account.account" with oid: <account_oid>
    And having:
      | key             | value                 |
      | name            | <account_name>        |
      | code            | <account_code>        |
      | user_type_id    | by name: <user_type>  |

    Examples: Bank Accounts
      | account_oid             | account_name              | account_code   | user_type |
      | scenario.account_1010   | XXX 00-001285-1           | 1010           | Expenses  |
      | scenario.account_1020   | ZZZ BE7400700115500080000 | 1020           | Expenses  |
      | scenario.account_1021   | ZZZ BE2300700115500172222 | 1021           | Expenses  |

  @banks
  Scenario Outline: Create bank account for Alcyon Belux SA
    Given I am configuring the company with ref "base.main_company"
    Given I need a "account.journal" with oid: <journal_oid>
    And having:
      | key                         | value                     |
      | name                        | <journal_name>            |
      | code                        | <journal_code>            |
      | type                        | bank                      |
      | company_id                  | by oid: base.main_company |
      | currency_id                 | <currency>                |
      | default_debit_account_id    | by code: <acc_code>       |
      | default_credit_account_id   | by code: <acc_code>       |
      | update_posted               | True                      |
    Given I need a "res.partner.bank" with oid: <bank_oid>
    And having:
      | key                 | value                     |
      | journal_id          | by oid: <journal_oid>     |
      | partner_id          | by oid: base.main_partner |
      | bank_id             | by oid: <bank_id>         |
      | company_id          | by oid: base.main_company |
      | acc_number          | <account_nr>              |

    Examples: Bank Accounts
      | journal_oid             | journal_code | journal_name | currency | acc_code | bank_oid        | bank_id         | account_nr       |
      | scenario.journal_XXXX   | XXXX         | Poste XXX    | false    | 1010     | scenario.bank_1 | scenario.bank1  | BE2198765430     |
      | scenario.journal_ZZZ1   | ZZZZ         | ZZZ 1        | false    | 1020     | scenario.bank_2 | scenario.bank2  | BE68539007547034 |
      | scenario.journal_ZZZ2   | ZZZZ         | ZZZ 2        | false    | 1021     | scenario.bank_3 | scenario.bank3  | BE11123456748    |

  @journal
  Scenario Outline: create new financial journal
    Given I need a "account.journal" with oid: <journal_oid>
    And having:
      | key                         | value                     |
      | name                        | <journal_name>            |
      | code                        | <journal_code>            |
      | type                        | <journal_type>            |
      | company_id                  | by oid: base.main_company |
      | currency_id                 | <currency>                |
      | update_posted               | True                      |

    Examples: Financial Journals
      | journal_oid             | journal_name  | journal_code  | journal_type  | currency |
      | scenario.expense_journal| Expenses      | EXP           | purchase      | false    |
      | scenario.wage_journal   | Wage          | WAGE          | purchase      | false    |

  # If needed
  # @default_accounts
  # Scenario Outline: Define default accounts via properties
  #   Given I set global property named "<name>" for model "<model>" and field "<name>" for company with ref "base.main_company"
  #   And the property is related to model "account.account" using column "code" and value "<account_code>"

  #   Examples: Defaults accounts for Alcyon Belux SA
  #     | name                                 | model            | account_code |
  #     | property_account_receivable_id       | res.partner      |         4000 |
  #     | property_account_payable_id          | res.partner      |          440 |
  #     | property_account_expense_categ_id    | product.category |          600 |
  #     | property_account_income_categ_id     | product.category |         7010 |
  #     | property_stock_valuation_account_id  | product.category |              |
  #     | property_stock_account_input         | product.template |          654 |
  #     | property_stock_account_output        | product.template |          754 |

  # @account_cancel
  # Scenario Outline: Activate account cancel on all financial journals
  #   Given I need a "account.journal" with code: <journal_code>
  #   And having:
  #     | key                       | value           |
  #     | update_posted             | <update_posted> |

  #   Examples: Journals Accounts
  #     | journal_code    | update_posted |
  #     | INV             | True          |
  #     | BILL            | True          |
  #     | MISC            | True          |
  #     | EXCH            | True          |
  #     | STJ             | True          |
