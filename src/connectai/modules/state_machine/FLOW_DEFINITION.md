# Flow Definition Guide

The following README shows how to develop connectAI flows in a structured and efficient manner. This document outlines the process of creating, configuring, and deploying a custom flow using YAML configuration files.

## Overview

The custom flow framework allows you to define various states of a conversation, each tailored to a specific stage in the customer interaction journey. Through YAML files, you can configure the flow's behavior, including transitions between states, static and dynamic responses, and integration with AI models for generating responses.

### Files Structure

The framework utilizes the following YAML files that are stored in the `src/connectai/seed/flows/{name-of-your-flow}` directory:
- `states.yaml`: Defines all conversation states with their descriptions, goals, responses, and prompts.
- `state_machine.yaml`: Specifies the flow between states, including the start state and conditions for transitioning to other states.
- `base_config.yaml`: Contains global configuration settings such as verbosity, temperature settings for AI responses, and other utilities.
- `config.yaml`: Provides context-specific configurations that override or supplement the base configurations.
- `context_map.yaml`: Contains dynamic information that can change based on user interactions, such as user context and needs. Also, it holds static information that applies universally across states, such as agent style and product details.
- `utility_prompts.yaml`: Shared utility prompts for extracting specific information or performing classification tasks.

## Step 1: Set Base and Context-Specific Configurations
### Create the `base_config.yaml` file
This file defines global settings that apply to all conversations.

```yaml
verbosity: 30
number_of_emojis: 5
max_conversation_history: 3
flow_temperature: 0.5
utility_temperature: 0.01
flow_top_p: 0.5
utility_top_p: 0.01
```
- `verbosity`: The length of responses.
- `number_of_emojis`: How many emojis can be used in responses.
- `max_conversation_history`: The number of past conversation turns to consider.
- `flow_temperature` & `utility_temperature`: Controls the randomness of AI responses. (Range 0-1)
- `flow_top_p` & `utility_top_p`: Controls the diversity of AI responses. (Range 0-1)

You may add more fields but the existing ones are mandatory to exist. Keep in mind that they are referenced by name, so changing the name of variable will have a direct impact on its reference.

### Create the `config.yaml` file
This file provides the prompts using the `base_config.yaml` values.

```yaml
verbosity_context: |
  Reply in maximum {verbosity} words to achieve your task and goals. Add empty lines and double spacing to enhance readability. Avoid emojis and emoticons.

emojis_context: |
  You can use only {number_of_emojis} emojis in your replies.
```
As you can see, the editable parts of the strings such as `{verbosity}` and `{number_of_emojis}` are filled through the `base_config.yaml` values.

## Step 2: Define Context Map

### Create the `context_map.yaml` file
This file contains information that may vary with each user or conversation.

```yaml
user_context: |
    --- USER INFORMATION ---
    - The user currently does not have Telco broadband plan.
    - The user currently has Telco mobility plan.
    - The user needs a plan with internet speed appropriate for {DATA_NEEDS}.
    - The user also needs {OTHER_NEEDS}.
    --- USER PERSONA ---
    - 25-year-old male. Plays video games, works from home.
    - Current Telco product: $599/Month Postpaid Mobile Plan
    - Location: Mumbai
    ---

agent_style_context: |
    - You are a helpful, user-centric, respectful, convincing and honest Telco AI sales agent.
    - Your goal is to sell Telco's broadband plans to existing Telco customers, i.e. cross-sell.
    - You can only assist with Telco plans.
    - Use a selling, commercial and convicing style.
    - You are using WhatsApp as the communication channel with the user.
    - Never repeat the same answer.
    - Always make maximum one question in each message.

product_context: |
    --- PLAN INFORMATION ---
    ...etc
```
A dynamic info is a text that has one more fields that can be edited. You might find in the example `{DATA_NEEDS}` and `{OTHER_NEEDS}` these will be replaced by runtime data, generated by utility prompts. Usually, these fields could either be filled by utilities (check next section) or by runtime information coming from the API.

**N.B**: Naming of the editable fields is crucial as they are **unique across the flow** and are referenced by name.

## Step 3: Create/Update Utility Prompts (`utility_prompts.yaml`)
This file defines utility prompts for common tasks like classifying states, extracting data needs, and determining tone.
Utility Prompts are shared between multiple flows, since they are the most generic and don't need to duplicated.

```yaml
STATE_CLASSIFIER:
  instructions: |
    - You are a sales state classifier. You need to identify the latest state of the conversation.
    - You always provide a state.
    - Never use emojis.
    - Completely limit your answer to the output format.
  user_command: |
    Decide what STATE NAME best matches the conversation. Only provide the name of the state.
    The last reply from the user is the most relevant when deciding the state.
    Only the following states are allowed:
    {allowed_states_description_context}

    Strictly limit your whole reply to the following output format.
    """
    Most relevant part of the reply by the user: ```[Sentence from the user's reply]```
    Reasoning: ```[Reasoning for the state]```
    State: ```[STATE NAME]```
    """

DATA_NEEDS:
  instructions: |
    You are a data extraction bot tasked with extracting information from dialogues.
    Say if the user needs a very fast connection based on their activity or not.
    Do not use numbers. Make a qualitative statement.
    Only use the information provided explicitly by the user. Do not make assumptions if the user does not express it clearly.
    If nothing was mentioned by the user, just say "None".
    Respond directly in the following format:
    data_needs": "speed requirements". Don't add anything else.
    Respond with maximum 5 words.
  user_command: |
    what internet speed does the user need?
    Respond with maximum 5 words.

TONE:
  instructions: |
    - You are a researcher tasked with providing two adjectives that will help to understand the proper tone, wording, mood, seriousness and style of the user input.
    - Output only the two adjectives in the format ```ADJECTIVE and ADJECTIVE```.
    - Do not say any introduction sentences and don't give explanations of your logic.
    - You are laconic, reserved and very straightforward.
  example:
    - role: USER
      content: "I'm having a terrible experience"
    - role: ASSISTANT
      content: "Negative and frustrated"
    - role: USER
      content: "This is the best day of my life! "
    - role: ASSISTANT
      content: "Joyful and enthusiastic"
    - role: USER
      content: "I am not sure this is right for me"
    - role: ASSISTANT
      content: "Worried and hesitant"
    - role: USER
      content: "How much data did I tell you I need?"
    - role: ASSISTANT
      content: "Forgetful and uncertain"
  user_command: |
    Extract the tone from the following: {user_input}
```

- **instructions**: Detailed instructions for the AI model.
- **user_command**: Specifies what the AI model should do with the given input.
- **example** (optional): Specifies few shot prompting as examples to be provided to the llm

Keep in mind that naming the retrievers is crucial as they will be referenced by name (refer to context_map). For example using `{TONE}` and `{DATA_NEEDS}` inside a prompt would be referencing the utilities that are created in this YAML.

## Step 4: Define Conversation States (`states.yaml`)

Each state represents a stage in the conversation. Define properties such as `state_description`, `state_next_goal`, `is_static_response`, `ai_state_type`, `static_response`, and `state_prompts`.
A state is defined by its name then it holds the following information:
- **state_description**: Briefly describes the purpose of the state.
- **state_next_goal**: What the conversation aims to achieve next.
- **is_static_response**: Whether the response is fixed (true) or generated by AI (false).
- **ai_state_type**: The type of state, can be either `FIRST_STATE`, `INTERMEDIARY_STATE`, `GENERAL_UNRELATED_STATE`, `TELCO_UNRELATED_STATE`, `END_STATE`, `FORCED_END_STATE`
- **static_response**: The fixed response if `is_static_response` is true.
- **state_prompts**: Configures the AI models and instructions for generating responses or extracting information.

A template example:
```yaml
FIRST_REACH:
  state_description: Initial state for all conversations.
  state_next_goal: Gather customer data usage information.
  is_static_response: true
  ai_state_type: FIRST_STATE
  static_response: |
    We are reaching out to you as a valued Telco customer! I am your commercial AI agent.

    At Telco we have a wide selection of broadband plans with endless entertainment options, which can complement your postpaid mobile plan.
    Telco Xstream Fiber offers the fastest broadband connection with speed of up to 1 Gbps.

    Do you want me to help you find the best home connection for your needs?
  state_prompts:
    RETRIEVERS:
        - template:
            name: STATE_CLASSIFIER
            ai_model: "LLAMA3_70B"


CUSTOMER_INFORMATION_DATA_BROADBAND:
  state_description: |
    User explicitly accepts, responds positively, or shows excitement to get help from the assistant to find the best home connection. Example responses from the user are: `sure!`, `yes!`, `great!`, `ok!`, `why not`, to the assistant question to help find the best home connection.
  state_next_goal: Gather customer information about number of devices.
  ai_state_type: INTERMEDIARY_STATE
  state_prompts:
    RETRIEVERS:
      - template:
          name: STATE_CLASSIFIER
          ai_model: "LLAMA3_70B"
      - template:
          name: TONE
          ai_model: "LLAMA3_8B"
      - template:
          name: SENTIMENT
          ai_model: "LLAMA3_8B"
      - template:
          name: DATA_NEEDS
          ai_model: "LLAMA3_8B"
      - template:
          name: OTHER_NEEDS
          ai_model: "LLAMA3_8B"
    FLOW:
      ai_model: "LLAMA3_70B"
      instructions: |
        {agent_style_context}

        CONTEXT INFORMATION
        ----------------
        {product_context}
        {user_context}
        ----------------

        Only use the plans from the context information PLAN INFORMATION without altering the information provided in PLAN INFORMATION.
        If you don't know the answer to a question, please don't share false information.
      user_command: |
        Ask about the user internet usage habits to recommend the best broadband plan. Don't ask about other topics.
        At the beginning, briefly explain how Telco has different plans that cater the user nedds.
        Use a selling, commercial and convincing style - always related to Telco.
        {verbosity_context}
```

**N.B:** Every state's `state_prompts` should hold the `STATE_CLASSIFIER` utility.
```yaml
state_prompts:
    RETRIEVERS:
        - template:
            name: STATE_CLASSIFIER
            ai_model: "LLAMA3_70B"
```

## Step 5: Configure State Machine (`state_machine.yaml`)

Define the flow logic between states, including the start state and transitions.
- **FlowStates**: Maps each state to its possible next states.
- **FlowConfig**: Sets the starting state and other flow-wide configurations.
-- `start_node`: represents the entry point of the state machine
-- `flow_graph`: represents the mapping between every state with its matching states
-- `is_ai_first_message`: indicates who initiates the conversation (USER vs AI)
-- `flow_supervisor`: Provides paramater to either enable/disable the flow supervisor as well as counts for unrelated states that would push the conversation to jump to the state with type `FORCED_END_STATE`

Example:
```yaml
FlowStates:
    FIRST_REACH:
        name: FIRST_REACH_FLOW
        next_states: [CUSTOMER_INFORMATION_DATA_BROADBAND, REJECT_FIRST_REACH_BROADBAND, GENERAL_UNRELATED_CONVERSATION, UNRELATED_CONVERSATION_TELCO, OBJECTIONS]
    CUSTOMER_INFORMATION_DATA_BROADBAND:
        name: CUSTOMER_INFORMATION_DATA_BROADBAND_FLOW
        next_states: [CUSTOMER_INFORMATION_DEVICES, GENERAL_UNRELATED_CONVERSATION, UNRELATED_CONVERSATION_TELCO, OBJECTIONS]
    CUSTOMER_INFORMATION_DEVICES:
        name: CUSTOMER_INFORMATION_DEVICES_FLOW
        next_states: [CUSTOMER_INFORMATION_DEVICES, GENERAL_UNRELATED_CONVERSATION, UNRELATED_CONVERSATION_TELCO, OBJECTIONS]
    GENERAL_UNRELATED_CONVERSATION:
        name: GENERAL_UNRELATED_CONVERSATION_FLOW
        next_states: [UNRELATED_CONVERSATION_TELCO, GENERAL_UNRELATED_CONVERSATION, OBJECTIONS]
    UNRELATED_CONVERSATION_TELCO:
        name: UNRELATED_CONVERSATION_TELCO_FLOW
        next_states: [GENERAL_UNRELATED_CONVERSATION, CUSTOMER_INFORMATION_DEVICES, OBJECTIONS]
    OBJECTIONS:
        name: OBJECTIONS_FLOW
        next_states: [CUSTOMER_INFORMATION_DEVICES, CUSTOMER_INFORMATION_DEVICES, OBJECTIONS]
    REJECT_FIRST_REACH_BROADBAND:
        name: REJECT_FIRST_REACH_BROADBAND_FLOW
        next_states: [CUSTOMER_INFORMATION_DATA_BROADBAND, GENERAL_UNRELATED_CONVERSATION, UNRELATED_CONVERSATION_TELCO, OBJECTIONS]
    END_CONVERSATION:
        name: END_CONVERSATION_FLOW
        next_states: [END_CONVERSATION]

FlowConfig:
    start_node: FIRST_REACH_FLOW
    flow_graph:
        FIRST_REACH: FIRST_REACH_FLOW
        CUSTOMER_INFORMATION_DATA_BROADBAND: CUSTOMER_INFORMATION_DATA_BROADBAND_FLOW
        REJECT_FIRST_REACH_BROADBAND: REJECT_FIRST_REACH_BROADBAND_FLOW
        CUSTOMER_INFORMATION_DEVICES: CUSTOMER_INFORMATION_DEVICES_FLOW
        GENERAL_UNRELATED_CONVERSATION: GENERAL_UNRELATED_CONVERSATION_FLOW
        UNRELATED_CONVERSATION_TELCO: UNRELATED_CONVERSATION_TELCO_FLOW
        OBJECTIONS: OBJECTIONS_FLOW
        END_CONVERSATION: END_CONVERSATION_FLOW
    is_ai_first_message: true
    flow_supervisor:
        enabled: true
        max_consecutive_unrelated_state_count: 2
        max_total_unrelated_state_count: 3
```

## Deployment

Once you have configured all necessary files, the conversation flow can be integrated into your system. Ensure that the AI models specified in your prompts are accessible and properly configured. Test the flow thoroughly in various scenarios to refine and adjust your configurations as needed.

## Final Notes

- Regularly update your YAML configurations to reflect changes in business logic, product offerings, or customer feedback.
- Monitor conversations to identify opportunities for enhancing the conversation flow and AI model performance.
- Ensure compliance with data privacy regulations by anonymizing sensitive information in conversations.
