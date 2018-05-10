# Number Service

## System requirements
- [Pipenv](https://github.com/pypa/pipenv)
- [Python 3](https://docs.python.org/3/)
- [Postgresql database](https://www.postgresql.org/download/) v10.3
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

## Initial Setup

1. `$ heroku login`
1. `$ heroku create`

### Postgres database (Local)

1. Open a `psql` prompt `#`

1. Create a new database

   `# CREATE DATABASE your_db_name;`

1. Create a new user

   `# CREATE USER your_user_name WITH PASSWORD 'your_user_password';`

1. Change the owner of the new database to the new user

   `# ALTER DATABASE your_db_name OWNER TO your_user_name;`

1. Open a terminal prompt `$`

1. Set the `DATABASE_URL` environment variable to store the database connection information (note: this includes credentials).

   `$ export DATABASE_URL="host=localhost dbname=your_db_name user=your_user_name password=your_user_password"`

### Postgres database (Cloud)

1. Provision the [Heroku Postgres add-on](https://elements.heroku.com/addons/heroku-postgresql), this will set the `DATABASE_URL` environment variable.

   `$ heroku addons:create heroku-postgresql:hobby-dev` 

## Running

### Local

1. `$ pipenv install` install dependency graph
1. `$ pipenv shell` activate project's virtualenv
1. `$ make local` run web app locally

### Cloud

- `$ make deploy` git push branch `master` to remote `heroku`
- `$ make start` start service
- `$ make stop` stop service
- `$ heroku logs --tail` view logs

## Usage

### Quick happy path

1. Initialize the service `/init`. One admin user is created with user id `admin` and password `password`.
1. Change the default admin password `/user/password/change`
1. Refresh admin auth token `/user/auth_token/refresh`
1. Add a user `/user/add`
1. Add a number `/number/add`
1. Add the user to the number `/number/user/add`
1. Get next number `/number/next`

See [Postman collection](docs/NumberServer.postman_collection.json) for more detail and complete list of endpoints.

## Testing

Set the `TEST_DATABASE_URL` environment variable to store the database connection information (note: this includes credentials).

- `$ make test` run tests
- `$ make testcov` run tests and generate coverage report

## License
Apache License 2.0
