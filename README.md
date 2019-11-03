<img src="https://res.cloudinary.com/dw675k0f5/image/upload/v1571867673/storo/Screenshot_from_2019-10-24_00-54-05.png"/>

### Stacks used
1. Postgres, Redis, Celery
2. Django, API, graphene, graphql
3. Mpesa and PayPal payment gateways
4. GCP compute engine

## How to test


1. Clone the Repo. Ensure you have python 3.7
2. Create a virtualenv
```
virtualenv -p python3 env
```
3. Once the virtual environment has been setup, activate it and install the packages required by the project, these are contained in the file named requirements.txt
```
source env/bin/activate

pip install -r requirements.txt
```
4. Ensure PostgreSQL is installed and is running psql, follow these steps to create a new user and a database which will be used in the application.
    1. Start the postgres database server using the command:
    ```
    pg_ctl -D /usr/local/var/postgres start
    ```
    2. Run psql interactive terminal
    ```
    psql postgres
    ```
    3. Create a new user:
    ```
    CREATE USER sample_username WITH PASSWORD 'sample_password';
    ```
    4. Grant privileges to the user:
    ```
    ALTER USER sample_username CREATEDB;
    ```
    5. Create a database:
    ```
    CREATE DATABASE sample_database_name WITH OWNER sample_username;
    ```
    6. Create a .env as guided by the .env_example and add the following configuration variables
    ```
    source env/bin/activate
    export DB_NAME="sample_db_name"
    export DB_USER="sample_db_user"
    export DB_PASS="sample_db_password"
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export TIME_DELTA="30"
    export EMAIL_HOST="smtp.gmail.com"
    export EMAIL_HOST_USER="sample_email"
    export EMAIL_HOST_PASSWORD="sample_password"
    export EMAIL_PORT=587
    export EMAIL_USE_TLS=True
    export SECRET_KEY="sample_secret_key"
    export SOCIAL_AUTH_FACEBOOK_KEY="sample_fb_auth_key"
    export SOCIAL_AUTH_FACEBOOK_SECRET="sample_fb_auth_secret"
    export MPESA_CONSUMER_KEY="sample_mpesa_auth_key"
    export MPESA_CONSUMER_SECRET="sample_mpesa_key"
    export MPESA_API_URL="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    export MPESA_SHORT_CODE="sample_paybill_number eg. 174379"
    export MPESA_PASSKEY="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    ```
    7. Source .env to set the configuration variables:
    ```
    source .env
    ```
    8. Run migrations to create the tables in the database:
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
    9. Run the server
    ```
    python3 manage.py runserver
    ```
    9. Access the route /graphql and tryout different queries and mutations as shown in the documentation
    
