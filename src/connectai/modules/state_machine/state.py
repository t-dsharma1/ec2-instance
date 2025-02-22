import asyncio
import pprint

from connectai.handlers import get_or_create_logger
from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PubSubKey
from connectai.modules.datamodel import (
    AIStateType,
    CustomerFeatures,
    DialogueFeatures,
    LLMDelimeters,
    LLMFeatures,
    MessageType,
    OutputKey,
    PromptType,
    Response,
    RuntimeContext,
    TranslationLanguages,
)
from connectai.modules.state_machine.prompt import Prompt
from genie_dao.services import create_ai_state_for_conversation, create_message

_log = get_or_create_logger(logger_name="State")


class State:
    """State with prompts.

    It contains the prompts that can be executed in the state.
    """

    def __init__(
        self,
        state_name: str,
        state_description: str,
        state_next_goal: str,
        state_prompts: list[Prompt],
        ai_state_type: str,
        static_response: str = "",
        is_static_response: bool = False,
    ):
        self.state_name = state_name
        self.state_prompts = state_prompts
        self.state_description = state_description
        self.ai_state_type = ai_state_type
        self.state_next_goal = state_next_goal
        self.state_reasoning = ""  # Filled on runtime
        self.is_static_response = is_static_response
        self.static_response = static_response
        self._state_context = {}
        self.runtime_context: RuntimeContext = None

        # Enrich the state context with the state next goal
        self.enrich({"state_next_goal": state_next_goal})

    async def run(
        self,
        runtime_context: RuntimeContext,
        session_bus: ConversationSessionBus,
        can_db_store: bool = True,
    ) -> Response:
        """Run prompts in the state.

        Steps:
        1 - Store Dynamic Context (ex: User Data, API Data)
        2 - Populate Utility Prompts' Context (ex: Tone Context, Sentiment Context)
        3 - Populate Runtime Context Values (ex: Summary)
        4 - Populate Flow Response Context (ex: State specific prompt)
        5 - Save AI State to the database
        """

        _log.info(f"Running state: {self.state_name}")

        self._populate_dynamic_runtime_context(runtime_context, can_db_store)

        # Breaks the retrievers dependency on the flow response
        await asyncio.gather(
            self._populate_state_context_utility_values(session_bus),
            self._populate_state_context_flow_value(session_bus),
        )

        # Uncomment this and comment the previous lines to add back the retrievers dependency on the flow response
        # await self._populate_state_context_utility_values(session_bus)
        # await self._populate_state_context_flow_value(session_bus)

        response = await self._save_ai_state()
        await session_bus.publish_response_completed(
            conversation_ended_flag=self.ai_state_type == AIStateType.END_STATE.value
        )
        return response

    def _retrieve_prompts_by_type(self, prompt_type: PromptType):
        """Retrieve prompts of a given type."""
        return [prompt for prompt in self.state_prompts if prompt.prompt_type == prompt_type]

    async def _populate_state_context_utility_values(self, session_bus: ConversationSessionBus):
        """Populate values of utility prompts."""
        utility_prompts = self._retrieve_prompts_by_type(PromptType.UTILITY)
        await asyncio.gather(
            *[
                self._run_prompt_and_save(
                    prompt=prompt,
                    pubsub_key=PubSubKey.RETRIEVER,
                    session_bus=session_bus,
                )
                for prompt in utility_prompts
            ]
        )
        (self._populate_runtime_context_utility_values(),)

    async def _populate_state_context_flow_value(self, session_bus: ConversationSessionBus):
        """Populate value of flow response."""
        _log.info("Running Response prompt")
        if self.is_static_response:
            self._format_static_response_and_save(session_bus=session_bus)
        else:
            await self._run_flow_prompts_and_save(session_bus=session_bus)

    def _populate_runtime_context_utility_values(self):
        """Placeholder to populate runtime context with values of utility prompts.

        Current runtime contexts:
        - Summary
        """
        # Inject summary into conversation
        self.runtime_context.conversation.inject_summary(self._state_context.get(OutputKey.SUMMARY.value, ""))

    async def _run_flow_prompts_and_save(self, session_bus: ConversationSessionBus):
        """Run flow prompts and save to state context."""
        flow_prompts = self._retrieve_prompts_by_type(PromptType.FLOW)
        for prompt in flow_prompts:
            if prompt.can_execute:
                await self._run_prompt_and_save(prompt, pubsub_key=PubSubKey.RESPONSE, session_bus=session_bus)

    async def _run_prompt_and_save(
        self, prompt: Prompt, pubsub_key: PubSubKey, session_bus: ConversationSessionBus
    ) -> str:
        """Run the prompt and save result to state context."""
        _log.info(f"Running prompt Type: {pubsub_key.value}")
        response = await prompt.run(
            session_bus=session_bus,
            pubsub_key=pubsub_key,
            conversation=self.runtime_context.conversation,
            max_conversation_history=self._state_context[
                f"{str(prompt.prompt_type.value).lower()}_max_conversation_history"
            ],
            temperature=self._state_context[f"{str(prompt.prompt_type.value).lower()}_temperature"],
            top_p=self._state_context[f"{str(prompt.prompt_type.value).lower()}_top_p"],
            frequency_penalty=self._state_context[f"{str(prompt.prompt_type.value).lower()}_frequency_penalty"],
            placeholder_values=self._state_context,
        )
        self._state_context[prompt.output_key.value] = response

    def _format_static_response_and_save(self, session_bus: ConversationSessionBus) -> str:
        """Format the static response and save it in state context."""
        response = self.static_response
        for key, value in self._state_context.items():
            response = response.replace(f"{{{key}}}", str(value))

        self._state_context[OutputKey.FLOW.value] = response

        session_bus.publish_chunk(message_content=response)
        # Send END Delimiter message
        session_bus.publish_chunk(message_content=LLMDelimeters.END.value)

    def get_state_classifier_prompt(self) -> Prompt:
        """Get the state classifier prompt."""
        return [prompt for prompt in self.state_prompts if (prompt.output_key == OutputKey.STATE_CLASSIFIER)][0]

    def enrich(self, config: dict):
        """Enrich the state context with the config context."""
        self._state_context.update(config)

    def _populate_dynamic_runtime_context(self, runtime_context: RuntimeContext, can_db_store: bool):
        """Inject the runtime context into the state context."""
        self._state_context.update(runtime_context.extra_info)
        self.runtime_context = runtime_context
        self.can_db_store = can_db_store

    def _post_process_flow_response(self, flow_response: str) -> str:
        """Post-process the flow response."""
        return flow_response.replace(LLMDelimeters.END.value, "")

    async def _save_ai_state(self) -> Response:
        """Save the AI state to the database."""
        flow_response = self._state_context[OutputKey.FLOW.value]
        flow_response = self._post_process_flow_response(flow_response)
        _log.info(f"Flow response: {flow_response}")

        tone_response = self._state_context.get(OutputKey.TONE.value, None)
        sentiment_response = self._state_context.get(OutputKey.SENTIMENT.value, None)
        data_needs_response = self._state_context.get(OutputKey.DATA_NEEDS.value, None)
        plan_type_response = self._state_context.get(OutputKey.PLAN_TYPE.value, None)
        number_of_lines_response = self._state_context.get(OutputKey.NUMBER_OF_LINES.value, None)
        otts_response = self._state_context.get(OutputKey.OTTS.value, None)
        pin_code_response = self._state_context.get(OutputKey.PIN_CODE.value, None)
        existing_services_response = self._state_context.get(OutputKey.EXISTING_SERVICES.value, None)
        discussed_plans_response = self._state_context.get(OutputKey.DISCUSSED_PLANS.value, None)
        other_needs_response = self._state_context.get(OutputKey.OTHER_NEEDS.value, None)
        conversation_summary_response = self._state_context.get(OutputKey.SUMMARY.value, None)

        if self.can_db_store:
            _log.info(
                f"Current conversation language: {self.runtime_context.conversation.current_conversation_language}"
            )
            message_created = await create_message(
                conversation_uid=self.runtime_context.conversation.conversation_uid,
                raw_message_content=flow_response,
                message_type=MessageType.output,
                raw_message_language_code=TranslationLanguages.ENGLISH.value,
                translate_target_language=self.runtime_context.conversation.current_conversation_language,
                is_translation_enabled=self.runtime_context.translation_service_enabled,
            )

            await create_ai_state_for_conversation(
                conversation_uid=self.runtime_context.conversation.conversation_uid,
                ai_state_name=self.state_name,
                ai_state_input_message_uid=self.runtime_context.extra_info.get("user_message_uid", None),
                ai_state_output_message_uid=message_created.message_uid,
                ai_tone=tone_response,
                ai_sentiment=sentiment_response,
                ai_data_needs=data_needs_response,
                ai_plan_type=plan_type_response,
                ai_otts=otts_response,
                ai_pin_code=pin_code_response,
                ai_existing_services=existing_services_response,
                ai_discussed_plans=discussed_plans_response,
                ai_number_of_lines=number_of_lines_response,
                ai_other_needs=other_needs_response,
                ai_conversation_summary=conversation_summary_response,
                ai_state_type=self.ai_state_type,
            )

        return Response(
            llm_response=(
                message_created.message_content_en
                if self.runtime_context.conversation.current_conversation_language != TranslationLanguages.ENGLISH.value
                else flow_response
            ),
            llm_features=LLMFeatures(
                state_name=self.state_name,
                reasoning=self.state_reasoning,
                next_goal=self.state_next_goal,
            ),
            dialogue_features=DialogueFeatures(
                language=self.runtime_context.conversation.current_conversation_language,
                tone=tone_response,
                sentiment=sentiment_response,
                discussed_plans=[discussed_plans_response],
                summary=conversation_summary_response,
            ),
            customer_features=CustomerFeatures(
                data_needs=data_needs_response,
                type_of_plan=plan_type_response,
                number_of_lines=number_of_lines_response,
                otts=otts_response,
                pin_code=pin_code_response,
                existing_services=existing_services_response,
                other_needs=[other_needs_response],
            ),
        )

    def __str__(self):
        return f"State: {self.state_name}\nDescription: {self.state_description}\nstatic response: {self.is_static_response}\nPrompts: {pprint.pformat(self.state_prompts)}\nNext Goal: {self.state_next_goal}\nStatic Response: {self.static_response}\nIs Static Response: {self.is_static_response}\nAI State Type: {self.ai_state_type}\n"
