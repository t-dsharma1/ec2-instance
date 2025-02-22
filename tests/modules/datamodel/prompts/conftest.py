import pytest

from connectai.modules.datamodel import LlmPrompt, PromptMessage, Role


@pytest.fixture(scope="class")
def no_history_conversation() -> LlmPrompt:
    instructions = "You are a helpful assistant."
    user_input = "What is the capital of Japan?"
    conversation_history = []
    return LlmPrompt(instructions=instructions, user_command=user_input, history=conversation_history)


@pytest.fixture(scope="class")
def no_history_conversation_as_request() -> list[dict[str, str]]:
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of Japan?"},
    ]
    return conversation


@pytest.fixture(scope="class")
def no_history_conversation_as_llama2() -> str:
    prompt = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\nWhat is the capital of Japan? [/INST]"
    return prompt


@pytest.fixture(scope="class")
def no_history_conversation_as_llama3() -> str:
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>You are a helpful assistant.\nWhat is the capital of Japan?<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    return prompt


@pytest.fixture(scope="class")
def user_start_conversation() -> LlmPrompt:
    instructions = "You are a helpful assistant."
    user_input = "What is the capital of Japan?"
    conversation_history = [
        PromptMessage(role=Role.USER, content="What is the capital of France?"),
        PromptMessage(role=Role.ASSISTANT, content="Paris"),
    ]
    return LlmPrompt(instructions=instructions, user_command=user_input, history=conversation_history)


@pytest.fixture(scope="class")
def user_start_conversation_as_request() -> list[dict[str, str]]:
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "Paris"},
        {"role": "user", "content": "What is the capital of Japan?"},
    ]
    return conversation


@pytest.fixture(scope="class")
def user_start_conversation_as_llama2() -> str:
    prompt = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\nWhat is the capital of France? [/INST] Paris </s><s>[INST] What is the capital of Japan? [/INST]"
    return prompt


@pytest.fixture(scope="class")
def user_start_conversation_as_llama3() -> str:
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>You are a helpful assistant.\n--- CONVERSATION ---\nUser: What is the capital of France?\nAssistant: Paris\n---\nWhat is the capital of Japan?<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    return prompt


@pytest.fixture(scope="class")
def assistant_start_conversation() -> LlmPrompt:
    instructions = "You are a helpful assistant."
    user_input = "What is the capital of France?"
    conversation_history = [PromptMessage(role=Role.ASSISTANT, content="Hey! How can I help you today?")]
    return LlmPrompt(instructions=instructions, user_command=user_input, history=conversation_history)


@pytest.fixture(scope="class")
def assistant_start_conversation_as_request() -> list[dict[str, str]]:
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant", "content": "Hey! How can I help you today?"},
        {"role": "user", "content": "What is the capital of France?"},
    ]
    return conversation


@pytest.fixture(scope="class")
def assistant_start_conversation_as_llama2() -> str:
    prompt = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\n [/INST] Hey! How can I help you today? </s><s>[INST] What is the capital of France? [/INST]"
    return prompt


@pytest.fixture(scope="class")
def assistant_start_conversation_as_llama3() -> str:
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>You are a helpful assistant.\n--- CONVERSATION ---\nAssistant: Hey! How can I help you today?\n---\nWhat is the capital of France?<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    return prompt


@pytest.fixture(scope="class")
def user_start_conversation_double() -> LlmPrompt:
    instructions = "You are a helpful assistant."
    user_input = "Always reply in the format Capital: ```Capital```"
    conversation_history = [
        PromptMessage(role=Role.USER, content="What is the capital of France?"),
        PromptMessage(role=Role.ASSISTANT, content="Paris"),
        PromptMessage(role=Role.USER, content="What is the capital of Japan?"),
    ]
    return LlmPrompt(instructions=instructions, user_command=user_input, history=conversation_history)


@pytest.fixture(scope="class")
def user_start_conversation_double_as_request() -> list[dict[str, str]]:
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "Paris"},
        {"role": "user", "content": "What is the capital of Japan?"},
        {"role": "user", "content": "Always reply in the format Capital: ```Capital```"},
    ]
    return conversation


@pytest.fixture(scope="class")
def user_start_conversation_double_as_llama2() -> str:
    prompt = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\nWhat is the capital of France? [/INST] Paris </s><s>[INST] What is the capital of Japan? [/INST] [INST] Always reply in the format Capital: ```Capital``` [/INST]"
    return prompt


@pytest.fixture(scope="class")
def user_start_conversation_double_as_llama3() -> str:
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>You are a helpful assistant.\n--- CONVERSATION ---\nUser: What is the capital of France?\nAssistant: Paris\nUser: What is the capital of Japan?\n---\nAlways reply in the format Capital: ```Capital```<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    return prompt


@pytest.fixture(scope="class")
def assistant_start_conversation_double() -> LlmPrompt:
    instructions = "You are a helpful assistant."
    user_input = "Always reply in the format Capital: ```Capital```"
    conversation_history = [
        PromptMessage(role=Role.ASSISTANT, content="Hey! How can I help you today?"),
        PromptMessage(role=Role.USER, content="What is the capital of France?"),
    ]
    return LlmPrompt(instructions=instructions, user_command=user_input, history=conversation_history)


@pytest.fixture(scope="class")
def assistant_start_conversation_double_as_request() -> list[dict[str, str]]:
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant", "content": "Hey! How can I help you today?"},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "user", "content": "Always reply in the format Capital: ```Capital```"},
    ]
    return conversation


@pytest.fixture(scope="class")
def assistant_start_conversation_double_as_llama2() -> str:
    prompt = "<s>[INST] <<SYS>>\nYou are a helpful assistant.\n<</SYS>>\n\n [/INST] Hey! How can I help you today? </s><s>[INST] What is the capital of France? [/INST] [INST] Always reply in the format Capital: ```Capital``` [/INST]"
    return prompt


@pytest.fixture(scope="class")
def assistant_start_conversation_double_as_llama3() -> str:
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>You are a helpful assistant.\n--- CONVERSATION ---\nAssistant: Hey! How can I help you today?\nUser: What is the capital of France?\n---\nAlways reply in the format Capital: ```Capital```<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    return prompt
