#!/bin/bash
set -o allexport; source .env; set +o allexport

echo "Retrieving delegate XML..."
python get_xml.py

echo "Parsing delegate XML..."
python read_delegate_xml.py

echo "Pushing csv to S3..."
aws s3 cp csv/delegates_cumulative.csv s3://$S3_URL/csv/delegates_cumulative.csv \
--profile $AWS_PROFILE_NAME \
--acl public-read
