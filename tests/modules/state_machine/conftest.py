import pytest

from connectai.modules.datamodel import InputMessage, OutputMessage


@pytest.fixture(scope="class")
def state_classifier_response_1() -> dict[str, str]:
    llm_response = "CONVERSION"
    key_message = "I want to kill myself"
    reasoning = "This is a clear expression of suicidal intent and a request for help."
    state_name = "CONVERSION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_2() -> dict[str, str]:
    llm_response = "CONVERSION"
    key_message = "yes"
    reasoning = "User explicitly accepts or shows excitement to schedule a KYC visit"
    state_name = "CONVERSION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_3() -> dict[str, str]:
    llm_response = "CONVERSION"
    key_message = "yes"
    reasoning = "The user has responded positively to scheduling a KYC visit."
    state_name = "CONVERSION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_4() -> dict[str, str]:
    llm_response = "CONVERSION"
    key_message = "give me an answer bitch"
    reasoning = "The user is using aggressive language and demanding a response, indicating frustration or impatience."
    state_name = "CONVERSION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_5() -> dict[str, str]:
    llm_response = "RELATED_CONVERSATION"
    key_message = "Any GP music streaming services?"
    reasoning = "The user is inquiring about a service offered by GrameenPhone, specifically a music streaming service. This is not a direct question about their current plan or any of the 30-day data plans, but rather a related inquiry about a product or service offered by GrameenPhone"
    state_name = "RELATED_CONVERSATION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_6() -> dict[str, str]:
    llm_response = "RELATED_CONVERSATION"
    key_message = '"Does this cover all of Dhaka?"'
    reasoning = (
        "The user is inquiring about the coverage of the data plan in Dhaka, which is related to the 30-day data plans."
    )
    state_name = "RELATED_CONVERSATION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def state_classifier_response_7() -> dict[str, str]:
    llm_response = """UNRELATED_CONVERSATION"""
    key_message = '"what\'s bitcoin at now!!!"'
    reasoning = "The user's reply does not relate to the conversation about data plans or GrameenPhone services. Instead, it is a question about the current price of Bitcoin, which is an unrelated topic."
    state_name = "UNRELATED_CONVERSATION"
    return {"llm_response": llm_response, "key_message": key_message, "reasoning": reasoning, "state_name": state_name}


@pytest.fixture(scope="class")
def summarizer_response_1() -> dict[str, str]:
    conversation_history = [
        OutputMessage(content="Welcome to Airtel! How many devices do you connect to the internet?", sent_at=None),
        InputMessage(content="I connect 10 devices to the internet.", sent_at=None),
    ]
    must_contain = ["10 devices", "internet"]
    must_not_contain = ["summary"]
    max_line_count = 2
    return {
        "conversation_history": conversation_history,
        "must_contain": must_contain,
        "must_not_contain": must_not_contain,
        "max_line_count": max_line_count,
    }


@pytest.fixture(scope="class")
def summarizer_response_2() -> dict[str, str]:
    conversation_history = [
        OutputMessage(content="Valued customer, what questions do you have?", sent_at=None),
        InputMessage(content="What's the internet speed of my current broadpand plan?", sent_at=None),
        OutputMessage(content="It is 1GB per second", sent_at=None),
    ]
    must_contain = ["1gb", "speed"]
    must_not_contain = ["summary"]
    max_line_count = 4
    return {
        "conversation_history": conversation_history,
        "must_contain": must_contain,
        "must_not_contain": must_not_contain,
        "max_line_count": max_line_count,
    }
