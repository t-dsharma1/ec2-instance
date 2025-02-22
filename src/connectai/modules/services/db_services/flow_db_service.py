import json
import os
from datetime import datetime
from typing import Literal, Optional

from connectai.modules.state_machine.loaders.base_yaml_loader.base_yaml_loader import (
    BaseYAMLLoader,
)
from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import ChatbotTable, models
from genie_dao.datamodel.flows_archive.flows_archive_db_table import FlowsArchiveTable
from genie_dao.services import archive_old_flow_variants, put_flow_to_dynamodb
from genie_dao.storage import dynamodb

_log = logging.get_or_create_logger(logger_name="FlowDBService")


async def seed_flows(seed_dir_name: str):
    """Seed the chatbot table with flows."""
    async with dynamodb.DynamoDBClient() as client_db:
        table = await client_db.Table(ChatbotTable.get_table_name())
        archive_table = await client_db.Table(FlowsArchiveTable.get_table_name())

        creation_time = datetime.now().isoformat()

        for flow_type in os.listdir(seed_dir_name):
            for dir in os.listdir(f"{seed_dir_name}/{flow_type}"):
                if dir.isnumeric():
                    variant_number = dir
                else:
                    # Directory is something else than a variant number
                    continue
                base_config_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/config/base_config.yaml"
                )
                base_config = base_config_loader.load()

                config_llm_prompts_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/config/config.yaml"
                )
                config_llm_prompts = config_llm_prompts_loader.load()

                # TODO: Utilities will need to move to be defined at flow level
                utility_loader = BaseYAMLLoader(f"{seed_dir_name}/../shared/utility_prompts.yaml")
                utility_prompts = utility_loader.load()

                context_map_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/context_map/context_map.yaml", relative_path=False
                )
                context_map = context_map_loader.load()

                states_yaml_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/states/states.yaml", relative_path=False
                )
                states = states_yaml_loader.load()

                flow_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/state_machine/state_machine_flow.yaml",
                    relative_path=False,
                )
                flow = flow_loader.load()

                metadata_yaml_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/_metadata.yaml", relative_path=False
                )
                metadata = metadata_yaml_loader.load()

                callsight_config_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/callsight/pipeline.yaml",
                    relative_path=False,
                )
                callsight_pipeline = callsight_config_loader.load()

                voice_config_loader = BaseYAMLLoader(
                    f"{seed_dir_name}/{flow_type}/{variant_number}/voice/voice_config.yaml",
                    relative_path=False,
                )
                voice_config = voice_config_loader.load()

                if metadata.get("is_flow_seed"):
                    flow_item = _create_flow_seed_item(
                        PK=str(models.FlowPK()),
                        SK=str(
                            models.FlowVariantSK(
                                flow_id=flow_type,
                                datetime=creation_time,
                                variant_id=str(models.FlowVariantID(variant_number=int(variant_number))),
                            )
                        ),
                        states=states,
                        flow=flow,
                        base_config=json.dumps(base_config),
                        config_llm_prompts=config_llm_prompts,
                        context_map=context_map,
                        utility_prompts=utility_prompts,
                        item_type=models.ItemType.STATE_MACHINE.value,
                        item_created_datetime=creation_time,
                        display_name=metadata.get("flow_display_name", None),
                        experience_type="Custom Experience",
                        callsight_pipeline=callsight_pipeline,
                        voice_config=voice_config,
                    )
                    await archive_old_flow_variants(
                        flow_id=flow_type,
                        variant_id=str(models.FlowVariantID(variant_number=int(variant_number))),
                        table=table,
                        archive_table=archive_table,
                        new_timestamp=creation_time,
                    )
                    await put_flow_to_dynamodb(table, flow_item)
                    _log.info(f"Seeded flow `{flow_type}` into the chatbot table")

                if metadata.get("is_template_seed"):
                    template_flow_item = _create_flow_seed_item(
                        PK=str(models.FlowPK()),
                        SK=str(
                            models.FlowTemplateVariantSK(
                                template_id=flow_type,
                                datetime=creation_time,
                                variant_id=str(models.FlowVariantID(variant_number=int(variant_number))),
                            )
                        ),
                        states=states,
                        flow=flow,
                        context_map=context_map,
                        base_config=json.dumps(base_config),
                        config_llm_prompts=config_llm_prompts,
                        utility_prompts=utility_prompts,
                        item_type=models.ItemType.STATE_MACHINE.value,
                        item_created_datetime=creation_time,
                        experience_type="System Template",
                        callsight_pipeline=callsight_pipeline,
                        voice_config=voice_config,
                    )
                    await archive_old_flow_variants(
                        flow_id=flow_type,
                        variant_id=str(models.FlowVariantID(variant_number=int(variant_number))),
                        table=table,
                        archive_table=archive_table,
                        new_timestamp=creation_time,
                        is_template=True,
                    )
                    await put_flow_to_dynamodb(table, template_flow_item)
                    _log.info(f"Seeded template `{flow_type}` into the chatbot table")


def _create_flow_seed_item(
    PK: str,
    SK: str,
    states: dict,
    flow: dict,
    base_config: str,
    config_llm_prompts: dict,
    context_map: dict,
    utility_prompts: dict,
    item_type: str,
    item_created_datetime: str,
    experience_type: Optional[Literal["System Template", "Custom Template", "Custom Experience"]],
    display_name: Optional[str] = "",
    channel: Optional[str] = "",
    product_segment: Optional[str] = "",
    callsight_pipeline: Optional[dict] = "",
    voice_config: Optional[dict] = "",
) -> models.Flow:
    """Create a flow seed item."""
    return models.Flow(
        **{
            "PK": PK,
            "SK": SK,
            "flow_states": states,
            "flow_state_machine": flow,
            "flow_context_map": context_map,
            "flow_base_config": base_config,
            "flow_config_llm_prompts": config_llm_prompts,
            "flow_utility_prompts": utility_prompts,
            "item_type": item_type,
            "item_created_datetime": item_created_datetime,
            "flow_display_name": display_name,
            "channel": channel,
            "product_segment": product_segment,
            "experience_type": experience_type,
            "callsight_pipeline": callsight_pipeline,
            "voice_config": voice_config,
        }
    )
