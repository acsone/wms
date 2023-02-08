# Keycloak

## local setup

`docker-compose up docker-compose-opensearch.yml`

Elasticsearch-compatible client runs on port 9200, Kibana on port 5601.

## Opensearch configuration

https://opensearch.org/docs/latest/security-plugin/access-control/api/

## python client

As of now, the opensearch client only removes existing features:
https://github.com/opensearch-project/opensearch-py/commit/a41fd13d2d8a9bc8d800a53faedeb8e11d4cccd0

We therefore simply use the REST API for admin operations. Standard index and document
operations are compatible with the standard python connector up to 7.12; afterwards, the
commits listed break compatibility:
https://github.com/opensearch-project/opensearch-py/commit/934ea8cc5ed110f7032aad909ce629a2beb2af1b

## odoo server variables

Your `.odoorc` file should contain the following lines:

[se_backend_elasticsearch.elasticsearch_backend] ssl=False
es_server_host=https://localhost:9200/ es_user=admin es_password=admin
