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
    export DB_NAME="database_name"
    export DB_USER="sample_username"
    export DB_PASS="sample_password"
    export DB_HOST="host_name_eg_localhost"
    export DB_PORT="port_number_eg_5432"
    export TIME_DELTA="30"
    export EMAIL_HOST="smtp.gmail.com"
    export EMAIL_HOST_USER="testmail@mail.com"
    export EMAIL_HOST_PASSWORD="pass21234"
    export EMAIL_PORT=587
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
    