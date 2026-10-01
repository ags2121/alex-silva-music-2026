#!/bin/sh
set -e
cd "$(dirname "$0")"
aws cloudformation deploy --stack-name site-embed-check --template-file infra.yaml --capabilities CAPABILITY_IAM
rm -f /tmp/site-embed-check.zip && zip -j /tmp/site-embed-check.zip check.py
aws lambda update-function-code --function-name site-embed-check --zip-file fileb:///tmp/site-embed-check.zip >/dev/null
echo "Deployed. Confirm the SNS subscription email if this is the first deploy."
