# ConnectAI Modules

Modules offer a high level implementation for multiple concepts including data model, db services and state machine definition.

## Data Model

Our Data Model is subdivided into two categories:
- Raw Data: Handles all internal data types (files are prefixed with _ ex: `_conversations.py`) and holds the data structured that are used within the codebase. Raw data is used as an intermediary structure for reading the data from the database to serving it back to the user through the API.
- Storage Data: Handles all data that is stored on the database, such as tables and their attributes. We use dataclass models for the table attributes (check `modules/datamodel/storage/chatbot_db_model/models.py`) to explicitly declare and categorize the model items.

## DB Services

Holds all types of services such as:
- Translation service: A modular service that uses a third party provider to translate LLM and user responses
- Chatbot Table Service: Holds business logic database interactions, such as store/load conversations, messages, etc..

## State Machine

Holds the definition of the core connectAI logic, please refer to the corresponding README in the directory.
