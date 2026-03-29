FROM node:16.15.0 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Install AWS CLI and jq for secrets fetching (using Debian archive since Buster is EOL)
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until \"false\";" > /etc/apt/apt.conf.d/10no--check-valid-until && \
    apt-get update && \
    apt-get install -y awscli jq && \
    rm -rf /var/lib/apt/lists/*

# Arguments for passing AWS keys via Jenkins
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION=ap-south-1
ARG SECRET_NAME=trade/in/prod

# Generate .env file dynamically by fetching the secret from AWS
RUN aws secretsmanager get-secret-value \
    --region ${AWS_REGION} \
    --secret-id ${SECRET_NAME} \
    --query SecretString \
    --output text | jq -r 'to_entries | map("\(.key)=\(.value)") | .[]' > .env

RUN npm run build

FROM nginx:1.17

WORKDIR /usr/share/nginx/html

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build /app/build .

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx/nginx.conf /etc/nginx/conf.d

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
