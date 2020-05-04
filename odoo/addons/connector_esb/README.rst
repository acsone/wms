.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Connector ESB
=============

Existing synchronizations:

* Export pharmacies to the ESB (differential, once a day)
* Export products to the ESB (differential, once a day)
* Export customers to the ESB (differential, twice a day)
* Export customers addresses to the ESB (differential, twice a day)
* Export promotion alcyon to the ESB (differential, once a day)
* Export products price to the ESB (differential, once a day)
* Export stock to the ESB (differential, once a day)
* Export special promotions to the ESB (differential, once a day)
* Export buy x get y to the ESB (differential, once a day)
* Export documents zip to the ESB (differential, once a day)

Webservices:

 * ``/connector_esb/product/stock``: return stock levels of products
 * ``/connector_esb/product/stock/cnk``: return stock levels of all products or for some specific products with CNK code
 * ``/connector_esb/product/stock/sku``: return stock levels of all products or for some specific products with SKU code
 * ``/connector_esb/statistics/form``: return statistics from
   parameters sent using a form
 * ``/connector_esb/statistics/product/<sku>/<customer_ref>`` :
        return for a product a customer yearly purchase statistics
 * ``/connector_esb/statistics/customer/<ref>``: return customer yearly statisctics
 * ``/connector_esb/sales_order/create``: create a new sale order
 * ``/connector_esb/totalorder/customer/<customer_ref>``:
        return total of ongoing orders and a flag if the customer must pay
        delivery fees

A detailed documentation of the XML export and the web services is on Confluence

`<https://confluence.camptocamp.com/confluence/display/ALCO/Interfaces+ESB>`_

Some more information on how to tests with Magento

`<https://confluence.camptocamp.com/confluence/pages/viewpage.action?pageId=721768>`_

Configuration
=============

The configuration of the sFTP must be set in environment variables:
* host: ``ODOO_ESB_SFTP_HOST``
* port: ``ODOO_ESB_SFTP_PORT`` (default 22)
* user: ``ODOO_ESB_SFTP_USER``
* private key: ``ODOO_ESB_SFTP_PRIVATE_KEY``

Manual SFTP Test
================

If you want to do manual testing with a local sftp server, you should:

* Be sure to have this container in ``docker-compose.override.yml``::

    esbsftp:
      image: atmoz/sftp
      # 1033 is the id of my user (id -u), so I own the files created
      command: "foo::1033"
      volumes:
        - "./sftp/share:/home/foo/share"
      - "./sftp/id_rsa.pub:/home/foo/.ssh/keys/id_rsa.pub:ro"

* Configure the ``connector_esb`` module in ``docker-compose.override.yml``::

    ODOO_ESB_SFTP_HOST: esbsftp
    ODOO_ESB_SFTP_USER: foo
    # test key from sftp/id_rsa
    ODOO_ESB_SFTP_PRIVATE_KEY: |
        -----BEGIN RSA PRIVATE KEY-----
        MIICXQIBAAKBgQDNc0wBK+/GRNVgzutyNKbbVkCdGIsHLBc4atuLwZzka58l1UHR
        9Py3tvNymcxX6oj9AXGDNkyMYg514VbxJlwxkU+zN5gUy/Oc18TahKaLFvcRySeP
        KrXeQEzDBIqDhEUCX9ntteL8L+bYE55+AsvxS/oDmgn68mVrS2uo0Oh4GQIDAQAB
        AoGATDpHLPgcUrgfY3fiq9EVR7RM7Py6OMMHKoubQdNoXuf/eI4Tic8YJSHgWdju
        lIAUq6rpbwGqjTukmeAt3fOZqLARbE61XBMOvEy9sEYkwafC2WIzoSyfUxAvmAYj
        9Gvx/L345J1uFx53+HxMZeVNZYf+d+/Q+2EB5OLLYZPzNAECQQDx1vsN0AhnhQIc
        vgLym1IyUs9RvUQuRJbcvdnW/3splQwg9a3krtm1WdBrshFomw+AeRzxoRBHfuTU
        PijhtJehAkEA2Xrc98bXCCJ464TfiA1qCFjzc/OLCT1GC+UR92MVU2svef/5VswR
        1qjrT8X+q+15AVKpnPzdgfQ74Kp8G/WteQJAA+4TbFkKGeyOaTspPxoJDupLli92
        MS5KKVIofRbvwHA8nzh+1+2Dei/4dBeTsth6OwM81ixg4FiOjWhpL6nIoQJBAItl
        tDLhcb0WE3mqznhvWLKHCW0eAtVmP/qp1m1CRk4U2vaQ+yoGXbzAwyt71nQvH6uY
        Z31nmzeL68FipXBqdckCQQCCURUp8lWdC5UPwArD5P22Mame0XdlAkbH3vOuFCav
        5Dx0Zwm6sBJUrY64Qt/OvEk0nD+ttP7D+O65+IJ6gmCO
        -----END RSA PRIVATE KEY-----

* Start the sftp container::

    docker-compose up -d esbsftp

* Start Odoo::

    docker-compose run --rm -p 80:8069 odoo odoo --workers=0

* In Odoo > Connectors > ESB > Backend, in the Exports, configure the exports
  with the sFTP writer, set ``share`` in the path
* Click on export! In your local directory ``sftp/share/``, you should find the
  exported file


Credits
=======

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Thierry Ducrest <thierry.ducrest@camptocamp.com>
