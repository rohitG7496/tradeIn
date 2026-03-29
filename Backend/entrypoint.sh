#!/bin/bash
set -e

echo "Fetching configuration from AWS Secrets Manager..."

# We expect AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to be available in the environment from Jenkins
# Ensure Region and Secret Name defaults are set properly
AWS_REGION="${AWS_REGION:-ap-south-1}"
SECRET_NAME="${SECRET_NAME:-trade/in/prod}"

# Generate .env file dynamically by fetching the secret from AWS
aws secretsmanager get-secret-value \
    --region ${AWS_REGION} \
    --secret-id ${SECRET_NAME} \
    --query SecretString \
    --output text | jq -r 'to_entries | map("\(.key)=\(.value)") | .[]' > .env

echo "Successfully loaded variables into .env"

# Execute the CMD instruction passed by Dockerfile
exec "$@"
