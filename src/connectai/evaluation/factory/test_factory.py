import json
import uuid
from dataclasses import dataclass

import yaml

from connectai.evaluation import (
    CONTEXT_DIR,
    DATA_DIR,
    FLOW_SUBDIR,
    FLOW_VERSION,
    FLOWS_DIR,
    ROOT_DIR,
    TEST_CASE_PATH,
    USER_MESSAGE_SUBDIR,
)
from connectai.modules.datamodel import (
    Conversation,
    CustomerFeatures,
    InputMessage,
    OutputMessage,
)

FLOW_DIR = ROOT_DIR / DATA_DIR / FLOW_SUBDIR
USER_MESSAGE_DIR = ROOT_DIR / DATA_DIR / USER_MESSAGE_SUBDIR


@dataclass
class TestCase:
    name: str | uuid.UUID
    flow: str | None
    conversation_history: Conversation
    user_input: InputMessage
    from_state_name: str | None
    ground_truth_state_name: str
    business_logic: str | None
    context: str | None
    customer_features: CustomerFeatures


class TestFactory:
    def __init__(self):
        self.user_messages = self.fetch_user_messages()
        self.flows = self.fetch_flows()
        self.test_cases = self.fetch_test_cases()

    def fetch_user_messages(self, file_extension: str = "json") -> dict[list[str]]:
        user_messages = {}
        for file_path in USER_MESSAGE_DIR.glob("*." + file_extension):
            with open(file_path) as file:
                user_messages[file_path.stem] = json.load(file)
        return user_messages

    def fetch_flows(self, file_extension: str = "json") -> dict[list[dict[str]]]:
        flows = {}
        for file_path in FLOW_DIR.rglob("*." + file_extension):
            with open(file_path) as file:
                tmp = json.load(file)
                flows[f"{tmp['id']}_{tmp['flow']}"] = tmp["conversation"]
        return flows

    def fetch_test_cases(self, file_extension: str = "json") -> dict[dict[str]]:
        test_cases = {}
        for file_path in ROOT_DIR.rglob("*." + file_extension):
            if TEST_CASE_PATH in file_path.as_posix():
                with open(file_path) as file:
                    tmp = json.load(file)
                    test_cases[file_path.parent.name] = tmp
        return test_cases

    def fetch_conversation(self, id: str, checkpoint: int, file_extension: str = "json") -> Conversation:
        for file_path in FLOW_DIR.rglob("*." + file_extension):
            with open(file_path) as file:
                conversation = json.load(file)
                if conversation["id"] == id:
                    history = []
                    customer_features = CustomerFeatures()
                    flow_type = conversation["flow"]
                    for i in conversation["conversation"]:
                        if i["interaction"] <= checkpoint:
                            if "user" in i:
                                user_message = InputMessage(content=i["user"])
                                history.append(user_message)
                            assistant_message = OutputMessage(content=i["assistant"])
                            history.append(assistant_message)
                            if "customer_features" in i:
                                customer_features = CustomerFeatures(**i["customer_features"])
                    return (
                        Conversation(conversation_uid=conversation["id"], history=history),
                        customer_features,
                        flow_type,
                    )

    def fetch_context(self, flow: str, file_extension: str = "yaml") -> str:
        context_dir = FLOWS_DIR / flow / FLOW_VERSION / CONTEXT_DIR
        for file_path in context_dir.rglob("*." + file_extension):
            return "".join(value["value"] for value in yaml.safe_load(open(file_path)).values())

    def build(
        self,
        *,
        conversation_id: str = None,
        checkpoint: int = None,
        flow=str | None,
        user_input: str,
        from_state_name: str,
        ground_truth_state_name: str = None,
        business_logic: str = None,
        name: str = None,
    ) -> TestCase:
        test_cases = []

        if name is None:
            name = uuid.uuid4()

        if conversation_id is None or checkpoint is None or flow is None:
            conversation = Conversation(conversation_uid="1")
            customer_features = CustomerFeatures()
        else:
            conversation, customer_features, flow = self.fetch_conversation(id=conversation_id, checkpoint=checkpoint)

        context = self.fetch_context(flow)

        for message in self.user_messages[user_input]:
            test_cases.append(
                TestCase(
                    name=name,
                    flow=flow,
                    conversation_history=conversation,
                    user_input=InputMessage(content=message),
                    from_state_name=from_state_name,
                    ground_truth_state_name=ground_truth_state_name,
                    business_logic=business_logic,
                    context=context,
                    customer_features=customer_features,
                )
            )
        return test_cases
