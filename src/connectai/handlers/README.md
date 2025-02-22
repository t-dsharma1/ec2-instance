# ConnectAI Handlers

Handlers offer low level implementation for multiple concepts including API, DynamoDB storage, LLM calls and other utils (logging, env, etc..)

## API

- `main.py` is the entry point for the connectAI API, its main functions are:
    - Registering routers for the telcoAPI
    - Bootstrap the DB tables
    - Seed the pre-loaded States and StateMachines into the DB

## LLM

Holds the main function for performing LLM API calls

## Storage

Holds the definition for DynamoDB data types and operations (querying + scanning tables)

## Whatsapp

Holds helper functions to send and receive Whatsapp messages, on demand
