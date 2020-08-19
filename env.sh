#!/bin/bash

# export variables for latest versions
export ES_5_LATEST=5.6.10
export ES_6_LATEST=6.8.12
export ES_7_LATEST=7.9.0
export PSQL_9_LATEST=9.6.19
export PSQL_10_LATEST=10.14
export PSQL_11_LATEST=11.9
export MYSQL_5_LATEST=5.7.31
export MYSQL_8_LATEST=8.0.21
export REDIS_6_LATEST=6.0.6
export MEMCACHED_LATEST=1.6.6
export RABBITMQ_3_LATEST=3.8.7


# export default servces
export DB=psql
export ES=es
export CACHE=redis

# Elasticsearch
export ES_VERSION=123
# to override ES_VERSION with latest version, run in terminal: ES_VERSION=$ES_LATEST_VERSION

# PostrgreSQL
export PSQL_VERSION=9.6
export PSQL_USER=invenio
export PSQL_PASSWORD=invenio
export PSQL_DB=invenio

# MySQL
export MYSQL_USER=invenio
export MYSQL_PASSWORD=invenio
export MYSQL_DB=invenio
export MYSQL_ROOT_PASSWORD=invenio