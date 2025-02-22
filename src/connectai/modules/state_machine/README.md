# State Machine: Conversation Flow Management System

## Overview

This system is designed to manage and navigate through conversation states in a highly modular and dynamic manner. It leverages a finite state machine (FSM) model to handle transitions between different states based on the context of the conversation, user input, and predefined rules. The core functionality revolves around processing prompts, executing actions based on those prompts, and determining the next state of the conversation.

## Key Components

- **Prompt Management (`prompt.py`):** Handles the creation and management of prompts, which are the basic units of conversation. Each prompt is associated with a template, type, and expected output, and is capable of executing within a given context.

- **State Management (`state.py`):** Defines and manages states within the conversation. Each state contains prompts that can be executed, along with a description, next goals, and rules for transitioning to other states.

- **Flow State Management (`flow_state.py`):** Specializes in managing the flow between states, including the next possible states that can be transitioned to from the current state.

- **Flow Management (`flow.py`):** Central to the FSM, this component manages the current state of the conversation, transitions between states, and the overall flow configuration.

- **Flow Configuration (`flow_config.py`):** Provides configuration for the conversation flow, including the start node, flow graph, and other settings necessary to tailor the conversation experience.

- **Flow Supervisor** (`flow_supervisor/flow_supervisor.py`): Monitors the flow of the state machine. At the moment it is configured to keep track of unrelated conversations and end the conversation if we encounter unrelated conversations multiple times.

## How to Use

The state machine is designed to be flexible and easy to configure with YAML files. To set up and use custom conversation flows, follow these steps:

### Step 1: Define Your YAML Files


1. **Flow Configuration**: Define your base configuration, LLM prompts configuration, static, and dynamic context information in separate YAML files within your specified flow directory.

2. **States and Prompts**: Specify the available conversation states and associated prompts in the states YAML file. This includes defining the flow between states, utility prompts, and any custom logic needed for your application.

3. **Utility Prompts**: Define common utility prompts used across various states in a utility prompts YAML file located in the shared directory. This includes classifiers, tone analyzers, sentiment analysis, and other utility functions.

**N.B:** You may refer to the `connectai/seed` directory and check for example YAML files.


### Creating the YAML files

To create your YAML files please refer to the [Flow Definition README](FLOW_DEFINITION.md).

### Step 2: Initialize Loaders

Utilize the provided loader classes to read and interpret your YAML configuration files. These include:

- `BaseYAMLLoader` for basic YAML file loading.
- `StatesLoader` for loading state definitions.
- `StateMachineLoader` for constructing the state machine flow based on the states.
- `UtilityPromptsLoader` for loading common utility prompts.

### Step 3: Use the Flow Factory to Create Your Flow

The `FlowFactory` class serves as a centralized point for initializing and assembling your conversation flow system. Customize the `FlowFactory` initialization parameters to point to your YAML configuration files' directory. Then, call `create_flow()` to construct the flow based on your configurations.

### Example Usage

```python
from connectai.modules.state_machine.loaders.flow_factory import FlowFactory

# Initialize the flow factory with the path to your YAML configuration
flow_factory = FlowFactory(
    base_path="path/to/your/configuration", flow_type="your_flow_type"
)

# Create the flow
flow = flow_factory.create_flow()

# Now, you can use `flow.run(runtime_context)` to process conversation based on your configured states and transitions
```
