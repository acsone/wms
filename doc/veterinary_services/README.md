# Alcyon Veterinary Services: Developer Guide

The Alcyon Veterinary services are a collection of services to access the catalog,
discounts, sales and deliveries for a user account. They follow standard REST patterns,
with an accessible OpenAPI documentation. Moreover, it is possible to access a sandbox
version of these services for testing purposes.

There is a legacy version of these services based on XML and using basic authentication.
These legacy services are deprecated and will be removed within the year.

## Getting (Sandbox) Credentials

If you have an account on the main webshop `https://www.alcyonbelux.be/`, these
credentials are valid for the veterinary services endpoints. These credentials should be
valid on the sandbox instances; if they aren't, contact TODO to be granted access.

There is a sandbox available at TODO: UAT needs to open endpoints, PP, K8s? Data is
regularly synchronized with production, however there might be a delay of at most a
month.

## Authentication:

Authentication is through 

### JWT tokens managed by `Keycloak` using OIDC (Open ID Connect).
The entrypoint is at:
[TODO](https://account.alcyonbelux.be/auth/realms/alcyon/protocol/openid-connect/auth?protocol=oauth2&response_type=code&access_type&client_id=shopinvader)

TODO: correct link, audience name?

[Basics of OIDC](https://connect2id.com/learn/openid-connect)

### API key
Use of an API key supplied by Alcyon.
This connection mode is immediately available and operational, but will become obsolete in a few months.

## Navigating the main endpoints and their documentation

All services are paginated, returning the total number of records with the results from
the given page.

The main page for documentation is at:
[Documentation](https://erp.alcyonbelux.be/api-docs) TODO: open up this link!

### Catalog

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader_jwt%3A%20catalog)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader%3A%20catalog)

This service offers a `/` endpoint that returns the paginated catalog, and can be
filtered by AMM code, name or reference. By passing any of these fields with `__ilike`
it is possible to search on a substring.

### Discounts

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader_jwt%3A%20discounts)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader%3A%20discounts)

This service offers a `/` endpoint that returns all the current and planned discounts.
It is possible to look up discounts for a given product by passing the product
reference. There are two types of discounts: sale discounts, which give a percentage
over the base price (e.g. 10%), or promotions, which give additional products when
buying a certain number (e.g. buy 2 get 1 free).

### Cart

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?debug=1&urls.primaryName=shopinvader_jwt%2Fv2%3A%20cart)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?debug=1&urls.primaryName=shopinvader%2Fv2%3A%20cart)

This service offers different endpoints to interact with the current cart. There can be
only one cart at a given time. The `/` endpoint returns the current cart, or nothing is
there is none. The `/sync` endpoint accepts a `uuid` parameter for each transaction,
allowing for safe retries of requests. Note that the product quantities can be negative,
allowing to remove items. It is possible to modify the cart metadata, such has its
tracking information:

The `/csv` is more anachronistic as it is there for backwards compatibility. It also
allows to give the binary content of a `.csv` file to add products to the cart. In that
case there is no uuid for safe retries, and it is not possible to remove quantities.

### Orders

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader_jwt%3A%20orders)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader%3A%20orders)

This service offers a `/` endpoint that returns the orders. It is possible to filter
them by date, channel (phone, mail, fax, web).

### Deliveries

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader_jwt%3A%20pickings)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader%3A%20pickings)

This service offers two endpoints of interest:

- `/done` returns delivered quantities
- `/canceled` returns canceled deliveries

### Sale Statistics

[Documentation if authentication mode uses JWT tokens](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader_jwt%3A%20sale_statistics)
[Documentation if authentication mode uses API keys](https://erp.alcyonbelux.be/api-docs?urls.primaryName=shopinvader%3A%20sale_statistics)

This service offers one main endpoint of interest, `/top_ordered`, which returns the
most ordered product along the last 12 months.

## Migrating from legacy services

- catalog: catalog
- catalog/discounts: discounts
- quote: cart
- quote-csv: cart/csv
- price-list: sale_statistics
- cancelled_backorder: pickings/canceled
- packing-slip: pickings/done
- sales_order: orders
