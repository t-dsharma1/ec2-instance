# ConnectAI

ConnectAI, a GenAI-powered platform to create sales experiences

## Codebase structure

You may find the different code components in the `src/connectai/` directory:

- `cli/`: Contains the default cli commands for running the connectai services
- `evaluation/`: Contains the evaluation framework that tests LLM flows
- `modules/`: Contains the high level module definition (ex: data model, state machine, database services)
- `handlers/`: Contains the low level module implementaion (ex: api, storage, utils)
- `seed/`: Contains the YAML seed files for creating states, state machines, contexts and configuration

You may jump to individual directories and check their respective README files

## Quickstart

### Project setup

#### Setup the development environment

> _macOS_, _linux_

1. `python3.11 -m venv env`
2. `source env/bin/activate`
3. `pipx install poetry`
5. `poetry install --with dev`
4. `pre-commit install`

**Note**
`pre-commit` is used accross the development as "a framework for managing and maintaining multi-language git pre-commit
hooks."
On the first setup, it's recommended to run `pre-commit run --all-files` one time to have all the environments installed
and check for any errors, which otherwise will be hidden. `pre-commit` is triggered on every git commit

#### Setup the environment variables

```shell
cp .env.example .env
source .env
```

#### [How-To] Populate the env variables

__Optional Vars__

```
- SAGEMAKER_ENDPOINT_NAME: Needed as a fallback model, the name is generated in AWS
- SAGEMAKER_REGION: Defines the region of the Sagemaker AWS instance
```

__Required Vars__

```
- BACKEND_HOST: Points to your BE deployment
- AWS_REGION=: Refers to the AWS Region of the deployed infra
- OPENAI_KEY: Needed if using OpenAI models
- EVALUATION_OPENAI_BASE_URL: Required for running the evaluation framework
- EVALUATION_OPENAI_API_KEY: Required for running the evaluation framework
- EVALUATION_OPENAI_ORGANIZATION: Required for running the evaluation framework
- DATA_ENVIRONMENT: Used as a differentiator between develop and prod environments
- SUPERSET_BASE_URL: To be retrieved from Superset deployment on AWS
- SUPERSET_DASHBOARD_ID: To be retrieved from Superset deployment on AWS
- SUPERSET_USERNAME: To be retrieved from Superset deployment on AWS
- SUPERSET_PASSWORD: To be retrieved from Superset deployment on AWS
- SUPERSET_FIRSTNAME: To be retrieved from Superset deployment on AWS
- SUPERSET_LASTNAME: To be retrieved from Superset deployment on AWS
- BEDROCK_REGION: Location of BEDROCK model deployment
- ADD_TRUSTED_HOSTNAMES: Used to pass trusted hostnames for CORS
- INSTANCE_SUBDOMAIN: Reference to the deployment subdomain
- CHATBOT_QUEUE_NAME: Postfix of the chatbot queue
- KEYCLOAK_SERVER_URL: Location of Keycloak server
- KEYCLOAK_REALM: Can be retrieved on installation (check below for details)
- KEYCLOAK_ADMIN_CLIENT_SECRET: Can be retrieved on installation (check below for details)
- KEYCLOAK_CLIENT_ID: Can be set on installation (check below for details)
- KEYCLOAK_CLIENT_SECRET: Can be set on installation (check below for details)
- KEYCLOAK_CALLBACK_URI: Can be set on installation (check below for details)
- ABLY_API_KEY: API key for PubSub
```

##### ABLY_API_KEY

This key is required for real time pub/sub channels feature.

Each developer should create their own free Ably account using their BCG account. The UI should lead your through the
process. In the end you need to copy the API key with wider permission set (there are two listed).

#### [Optional] Modify Keycloak variables

The source and identity management is done through Keycloak.
Keycloak values are stored in `docker/keycloak/import/realm-localhost.json` file and loaded automatically when running
docker.

Refrain to change the following vars unless you want to modify Keycloak's default behavior:

- `KEYCLOAK_REALM`
- `KEYCLOAK_CLIENT_ID`
- `KEYCLOAK_ADMIN_CLIENT_SECRET`
- `KEYCLOAK_CLIENT_SECRET`

## Run

After setting up your env vars, you are now able to run the codebase
> For deployment and local development (Recommended):

Run `docker compose up --build`

- You can access FastAPI docs on `localhost:8000/docs`
- You can access your database admin app on `localhost:8001`
- You can access Keycloak admin panel on `localhost:8080`

### Create local users in Keycloak

1. Open `localhost:8080` in a browser to access Keycloak's admin panel
2. Enter `admin:admin` credentials (working only on localhost)
3. Select `localhost` from the dropdown of the sidebar
4. Navigate to `Users` page in main navigation
5. Press `Add user` button
6. Fill in all necessary/required details
7. Press `Join Groups` button and select `AdminFullAccess`
8. Press `Create` and you'll be redirected to the user's page
9. Change tab to `Credentials`
10. Press `Set passsword` button
11. Fill in the password form and press `Save` button

You now should be able to use this user to access all API endpoints.

__Congrats!__ The codebase is now up and running!

### [Optional] Keycloak and FastApi Admin Integration

In order to make the authentication work in FastApi admin panel you need to manually add `127.0.0.1 keycloak` record
to `/etc/hosts` file.

## Running Tests :rocket:

In order to run the unit tests in the codebase, make sure that:

1. You installed the libraries locally as instructed in the manual
2. You've populated your `.env` file

Step 1: Make sure you've activated your virtual environment

```shell
source venv/bin/activate
```

Step 2: Source your `.env` locally

```shell
source .env
```

Step 3: Run `pytest` and check the coverage

```shell
pytest --cov=connectai --cov-report=term-missing --cov-report=html
```

## Evaluation Framework

The evaluation framework is a toolkit that evaluates LLM responses. For more info, refer to shared documentation

### State Classification

```shell
python -m src.connectai.evaluation.state_classification.evaluator
```

### Conversation Output Agent

```shell
python -m src.connectai.evaluation.conversation_output_agent.evaluator
```

### Running the dashboard

From the `visualization` directory `evaluation/visualization` launch the streamlit component.

```shell
streamlit run app.py
```

### Exporting evaluation data

You can export all the evaluation test cases and underlying data (flows, user inputs, etc..).

```shell
python -m src.connectai.evaluation.data.export
```

## Deploying code

After merging a feature to `main` branch, you should be able to see a new PR, created automatically by
`release-plase` bot. After mering this new PR, a new Github version, and a new GIT tag is going to be created for you.
When this is done run the following command.

To release to `develop`:

```shell
bash ./scripts/release.sh -e develop -v <tag_name>
```

To release to `prod`:

```shell
bash ./scripts/release.sh -e prod -v <tag_name>
```

It is possible to specify a commit hash instead of a tag name, but we do not recommend this approach.
