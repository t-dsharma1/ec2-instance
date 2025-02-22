from connectai.modules.datamodel import PromptTemplate
from genie_dao.datamodel.chatbot_db_model.models import FlowStateUtilityPrompt


class UtilityPromptsLoader:
    """Loads utility prompts from a yaml file."""

    def __init__(self, utility_prompts: dict[str, FlowStateUtilityPrompt]):
        self.prompts = utility_prompts
        self.STATE_CLASSIFIER = PromptTemplate(instructions="", user_command="")
        self.DATA_NEEDS = PromptTemplate(instructions="", user_command="")
        self.PLAN_TYPE = PromptTemplate(instructions="", user_command="")
        self.NUMBER_OF_LINES = PromptTemplate(instructions="", user_command="")
        self.OTTS = PromptTemplate(instructions="", user_command="")
        self.PIN_CODE = PromptTemplate(instructions="", user_command="")
        self.EXISTING_SERVICES = PromptTemplate(instructions="", user_command="")
        self.DISCUSSED_PLANS = PromptTemplate(instructions="", user_command="")
        self.OTHER_NEEDS = PromptTemplate(instructions="", user_command="")
        self.TONE = PromptTemplate(instructions="", example=None, user_command="")
        self.SENTIMENT = PromptTemplate(instructions="", user_command="")
        self.SUMMARY = PromptTemplate(instructions="", user_command="")

    def load(self):
        # create objects
        self.STATE_CLASSIFIER = PromptTemplate.from_utility_prompt(self.prompts["STATE_CLASSIFIER"])
        self.DATA_NEEDS = PromptTemplate.from_utility_prompt(self.prompts["DATA_NEEDS"])
        self.PLAN_TYPE = PromptTemplate.from_utility_prompt(self.prompts["PLAN_TYPE"])
        self.NUMBER_OF_LINES = PromptTemplate.from_utility_prompt(self.prompts["NUMBER_OF_LINES"])
        self.OTTS = PromptTemplate.from_utility_prompt(self.prompts["OTTS"])
        self.PIN_CODE = PromptTemplate.from_utility_prompt(self.prompts["PIN_CODE"])
        self.EXISTING_SERVICES = PromptTemplate.from_utility_prompt(self.prompts["EXISTING_SERVICES"])
        self.DISCUSSED_PLANS = PromptTemplate.from_utility_prompt(self.prompts["DISCUSSED_PLANS"])
        self.OTHER_NEEDS = PromptTemplate.from_utility_prompt(self.prompts["OTHER_NEEDS"])
        self.TONE = PromptTemplate.from_utility_prompt(self.prompts["TONE"])
        self.SENTIMENT = PromptTemplate.from_utility_prompt(self.prompts["SENTIMENT"])
        self.SUMMARY = PromptTemplate.from_utility_prompt(self.prompts["SUMMARY"])
