@alcyon @setup @user

Feature: Manage users

  @admin_language
  Scenario: Change admin language
    Given I find an "res.users" with name: Administrator
    And having:
      | key        | value             |
      | lang       | fr_BE             |