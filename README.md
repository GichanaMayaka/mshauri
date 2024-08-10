# Mshauri (Mentor) API

This project processes CME and Drill information, provided as an excel document, to generate information about peer coaching and mentorship. The purpose of this API is to transform the data provided into a structured format suitable for database storage and further analyses.

The application is deployed and hosted at [Render](https://mshauri.onrender.com/.checklists). API documentation can be accessed at the [apidocs](https://mshauri.onrender.com/apidocs) endpoint.

**NOTE**: The app is hosted on Render's free tier so it may be scaled down when you access it. Please give it some time to lauch when accessing.

## Endpoints Reference

#### Get the 500 initial activites - Both CME and Drills - according to Specification.

```http
  GET /checklists
```

#### Modify the parser's execution trigger

```http
  POST /schedule
```

| Parameter  | Type     | Description                              |
| :--------- | :------- | :--------------------------------------- |
| `schedule` | `string` | A valid Cron Expression. **(Required)**. |

## Environment Variables

<a href="env"></a>

To run this project, you will need to add the following environment variables as a .env file. An example .env file is provided for your reference (.env.example).

`DEV_POSTGRES_DNS`: DNS for development Postgres DSN.

`DEV_SECRET_KEY`: Secret Key value

`TEST_POSTGRES_DNS`: DSN for test Postgres DSN.

`TEST_SECRET_KEY`: Secret Key value

`PROD_POSTGRES_DNS`: Valid DSN for the Production Posgres DSN.

`PROD_SECRET_KEY`: Secret Key Value

`POSTGRES_USER`: Required when using Docker.

`POSTGRES_PASSWORD`: Required when using Docker

**Please Note that all parameters are required for now.**
Of importance is the **ENV** environment variable which denotes the environment of execution. Possible values include: **Prod**, **Dev** or **Test** for Production, Development, and Testing, respectively. Do note that by default, **Dev**/development is the default value, if no ENV parameter is provided.

## Executing the Application through [Docker:](https://www.docker.com/)

Once you have supplied the information required (as stipulated in the .env.example template), you can run the application using [Docker](https://www.docker.com/) as follows:

```bash
  docker-compose up -d
```

## Executing using Virtualenv/Local Installation without Docker:

**NOTE**: The app was developed using [Poetry](https://python-poetry.org/docs/) as the package manager. Please ensure you have Poetry [installed](https://python-poetry.org/docs/#installation) in-order to proceed.

You can run the application using the Flask CLI in tandem with Poetry - in development mode - in your local virtualenv/environment as follows:

For Linux users

```bash
  export FLASK_APP=mshauri &&
  flask create-db &&
  flask db upgrade &&
  gunicorn "mshauri:create_app()"
```

or

```bash
  export FLASK_APP=mshauri &&
  flask create-db &&
  flask db upgrade &&
  flask run --debug -p 8000
```

For Windows Users (**Note**: These are separate commands, so please make sure to execute them accordingly.)

```bash
  set FLASK_APP=mshauri
  flask create-db
  flask db upgrade
  flask run --debug -p 8000
```

## Testing

The application comes replete with tests to ensure its correct functioning. To execute the test, you can use pytest as follow:

for Windows users:

```bash
  set ENV=test
  pytest
```

For Linux users:

```bash
  export ENV=test
  pytest
```

**NOTE**: Running the tests requires a .env file as elicited in the [.env.example](#environment-variables). The tests create and destroy a test database, so the .env file must reference a valid Postgres database DSN.

## Assumptions

The application was built with some assumtions. Do note that some of these assumtions might be annotated in code comments. They include:

- Each observation has only one mentor associated with it.
- Each observation occurs in/has only one facility associated with it.
- The maximum number of CMEs/Drills can be 2 for each observation. The value 2 implies that each CME/Drill was performed twice.
- Facilities where observations occured are indicated in columns with the "facility" pattern therein.
- For any observation, there can be a maximum of 2 CMEs or 2 Drills. This is not to be confused with the maximum of CMEs/Drills in point 3.
- If no submission date/time is provided, the date and time of the record's generation is used as the submission time for the observation.
