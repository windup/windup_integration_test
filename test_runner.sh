#!/bin/bash

set -x
# eval statement allow us to pass arguments with quoted spaces via
# PYTEST_PARAMS environment variable. e.g: -k 'not sometest'

rm -rf /var/lib/jenkins/xunit
rm -rf windup_integration_test

pipenv run pip install -e .

eval pipenv run mta conf local-env \
  --ftp-host $1 \
  --ftp-username $2 \
  --ftp-password $3

pipenv run mta selenium start
sleep 200s

eval pipenv run pytest mta/tests/ -k $4 --context "ViaWebUI" -vv --junitxml=xunit_output.xml --tb=native
