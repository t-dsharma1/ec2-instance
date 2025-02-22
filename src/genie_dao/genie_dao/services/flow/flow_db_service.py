import itertools as it
import random
from datetime import datetime
from typing import Optional

from genie_core.utils import logging
from genie_core.utils.helpers import compress_data, safe_decompress_data
from genie_dao.datamodel.chatbot_db_model import ChatbotTable, models
from genie_dao.datamodel.flows_archive.flows_archive_db_table import FlowsArchiveTable
from genie_dao.storage import dynamodb
from genie_dao.storage.operations import query_all_items_dynamodb_table

_log = logging.get_or_create_logger(logger_name="FlowDBService")

flow_attributes_to_archive = ["flow_state_machine", "flow_states", "flow_context_map", "flow_utility_prompts"]


def filter_latest_flow_template_variants(all_template_variants: list[dict]) -> list[dict]:
    """Given all flow template variants, this function filters out the ones that have
    the freshest datetime segment in SK.

    Args:
        all_template_variants: list[dict] list of flow template variants fetched from dynamodb table

    Returns: list[dict] filtered list of flow template variants with unique variant id, but latest datetime
    """
    grouped_variants = it.groupby(
        all_template_variants, lambda item: models.FlowTemplateVariantSK.parse(item["SK"]).variant_id
    )

    result = []
    for _, variants in grouped_variants:
        sorted_variants = list(variants)
        sorted_variants.sort(key=lambda item: models.FlowTemplateVariantSK.parse(item["SK"]).datetime, reverse=True)
        result.append(sorted_variants[0])

    return result


def filter_latest_flow_variants(all_flow_variants: list[dict]) -> list[dict]:
    """Given all flow variants, this function filters out the ones that have the
    freshest datetime segment in SK.

    Args:
        all_flow_variants: list[dict] list of flow variants fetched from dynamodb table

    Returns: list[dict] filtered list of flow variants with unique variant id, but latest datetime
    """
    grouped_variants = it.groupby(all_flow_variants, lambda item: models.FlowVariantSK.parse(item["SK"]).variant_id)

    result = []
    for _, variants in grouped_variants:
        sorted_variants = list(variants)
        sorted_variants.sort(key=lambda item: models.FlowVariantSK.parse(item["SK"]).datetime, reverse=True)
        result.append(sorted_variants[0])

    return result


async def get_latest_flow_template_list() -> list[list[models.Flow]]:
    """Retrieves the latest flow template list from the database.

    Returns:
    - List[List[models.Flow]]: A list of flow variants where each item is a list of objects representing the flow template,
      including state machine definition, configuration, static context, etc.
    """
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"
    filter_expression = "attribute_not_exists(item_deleted_datetime)"
    expression_attribute_values = {
        ":pk": str(models.FlowPK()),
        ":sk_prefix": str(models.FlowTemplateVariantSK()),
    }

    data = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        key_condition_expression=key_condition_expression,
        filter_expression=filter_expression,
        expression_attribute_values=expression_attribute_values,
        consistent_read=True,
    )

    indexed_items = [
        filter_latest_flow_template_variants(variants)
        for _, variants in it.groupby(data, lambda item: models.FlowTemplateVariantSK.parse(item["SK"]).template_id)
    ]

    return [
        [
            models.Flow(
                **{k: v for k, v in variant.items() if k not in flow_attributes_to_archive},
                flow_state_machine=safe_decompress_data(variant, "flow_state_machine"),
                flow_states=safe_decompress_data(variant, "flow_states"),
                flow_context_map=safe_decompress_data(variant, "flow_context_map"),
                flow_utility_prompts=safe_decompress_data(variant, "flow_utility_prompts"),
            )
            for variant in variants
        ]
        for variants in indexed_items
    ]


async def get_latest_flow_metadata_list() -> list[list[models.Flow]]:
    """Fetch the latest flow metadata for all flow variants.

    Returns:
    - List[List[StateMachineItem]]: A List of Flow Variants where item is a list of objects representing the flow metadata – state machine definition, config,
    static context, etc
    """
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"
    filter_expression = "attribute_not_exists(item_deleted_datetime)"
    expression_attribute_values = {
        ":pk": str(models.FlowPK()),
        ":sk_prefix": str(models.FlowVariantSK()),
    }

    data = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
        filter_expression=filter_expression,
        consistent_read=True,
    )

    indexed_items = [
        filter_latest_flow_variants(variants)
        for flow_id, variants in it.groupby(data, lambda item: models.FlowVariantSK.parse(item["SK"]).flow_id)
    ]

    return [
        [
            models.Flow(
                **{k: v for k, v in variant.items() if k not in flow_attributes_to_archive},
                flow_state_machine=safe_decompress_data(variant, "flow_state_machine"),
                flow_states=safe_decompress_data(variant, "flow_states"),
                flow_context_map=safe_decompress_data(variant, "flow_context_map"),
                flow_utility_prompts=safe_decompress_data(variant, "flow_utility_prompts"),
            )
            for variant in variants
        ]
        for variants in indexed_items
    ]


async def get_all_flow_variants_metadata(flow_id: str) -> Optional[list[models.Flow]]:
    """Fetch full history of flow variant metadata for the given flow_id.

    Parameters:
    - flow_id (str): Id of the flow
    Returns:
    - list[Flow]: An unordered list of flow variants metadata.
    """

    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"
    filter_expression = "attribute_not_exists(item_deleted_datetime)"
    expression_attribute_values = {
        ":pk": str(models.FlowPK()),
        ":sk_prefix": str(models.FlowVariantSK(flow_id=flow_id)),
    }
    data = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        key_condition_expression=key_condition_expression,
        filter_expression=filter_expression,
        expression_attribute_values=expression_attribute_values,
        consistent_read=True,
    )

    if len(data) == 0:
        return None

    return [
        models.Flow(
            **{k: v for k, v in variant.items() if k not in flow_attributes_to_archive},
            flow_state_machine=safe_decompress_data(variant, "flow_state_machine"),
            flow_states=safe_decompress_data(variant, "flow_states"),
            flow_context_map=safe_decompress_data(variant, "flow_context_map"),
            flow_utility_prompts=safe_decompress_data(variant, "flow_utility_prompts"),
        )
        for variant in data
    ]


async def soft_delete_flow(flow_id: str) -> None:
    """Sets a item_deleted_datetime for every variant in history of the flow.

    Args:
        flow_id: An id of the flow to delete

    Returns:
        - list[Flow]: a list of deleted Flow items
    """
    all_flow_variants = await get_all_flow_variants_metadata(flow_id=flow_id)
    if all_flow_variants is None:
        return None

    deleted_time = datetime.now().isoformat()

    async with dynamodb.DynamoDBClient() as client_db:
        table = await client_db.Table(ChatbotTable.get_table_name())

        async with table.batch_writer() as batch_writer:
            for variant in all_flow_variants:
                variant.item_deleted_datetime = deleted_time
                await put_flow_to_dynamodb(batch_writer, flow=variant)

    return all_flow_variants


async def get_latest_flow_variants_metadata(flow_id: str) -> Optional[list[models.Flow]]:
    """Fetch the latest flow variant metadata for the given flow_id.

    Parameters:
    - flow_id (str): Id of the flow
    Returns:
    - list[Flow]: The ordered list of flow variants metadata.
            The first element is the base variant (variant = 0)
    """
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"
    filter_expression = "attribute_not_exists(item_deleted_datetime)"
    expression_attribute_values = {
        ":pk": str(models.FlowPK()),
        ":sk_prefix": str(models.FlowVariantSK(flow_id=flow_id)),
    }
    data = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        key_condition_expression=key_condition_expression,
        filter_expression=filter_expression,
        expression_attribute_values=expression_attribute_values,
        consistent_read=True,
    )

    if len(data) == 0:
        return None

    latest_flow_per_variant = {
        models.FlowVariantSK.parse(variant["SK"]).variant_id: models.Flow(
            **{k: v for k, v in variant.items() if k not in flow_attributes_to_archive},
            flow_state_machine=safe_decompress_data(variant, "flow_state_machine"),
            flow_states=safe_decompress_data(variant, "flow_states"),
            flow_context_map=safe_decompress_data(variant, "flow_context_map"),
            flow_utility_prompts=safe_decompress_data(variant, "flow_utility_prompts"),
        )
        for variant in filter_latest_flow_variants(data)
    }

    # Sort the latest_flow_per_variant keys to ensure that the base variant is always the first one
    latest_flow_per_variant = {key: latest_flow_per_variant[key] for key in sorted(latest_flow_per_variant.keys())}
    return list(latest_flow_per_variant.values())


async def get_latest_random_flow_variant_metadata(flow_id: str) -> models.Flow:
    """Fetch a random flow variant metadata for the given flow_id. The random selection
    is based on the weights of the base variant (variant = 0) defined in the flow
    config.

    Parameters:
    - flow_id (str): Id of the flow
    Returns:
    - Flow: The flow metadata.
            The default variant id is ItemType.VARIANT.value +"_"+ 0 --> VARIANT_0
    """

    latest_flow_per_variant = await get_latest_flow_variants_metadata(flow_id)
    base_variant: models.Flow = latest_flow_per_variant[0]

    nb_variants = len(latest_flow_per_variant)

    if nb_variants == 1:
        chosen_variant = base_variant
    else:
        _log.info(f"Found {nb_variants} variants for flow {flow_id}")

        weights: list[int] = base_variant.flow_state_machine.FlowConfig.variants_config.variants_weights
        chosen_variant = random.choices(latest_flow_per_variant, weights=weights)[0]
        _log.info(f"Chose variant {chosen_variant}")

    return chosen_variant


async def archive_old_flow_variants(
    flow_id: str, variant_id: str, table, archive_table, new_timestamp: str, is_template=False
):
    """Archive all items for the flow variant in the archive table and delete them from
    the chatbot table.

    Args:
        flow_id: An id of the flow to archive
        variant_id: An id of the variant to archive
        table: The chatbot table
        archive_table: The archive table
        new_timestamp: The new creation time for the flow variant
        is_template: A boolean flag indicating if the flow is a template
    """

    # Get all items for the flow variant
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"
    expression_attribute_values = {
        ":pk": str(models.FlowPK()),
        ":sk_prefix": str(models.FlowTemplateVariantSK(template_id=flow_id, variant_id=variant_id))
        if is_template
        else str(models.FlowVariantSK(flow_id=flow_id, variant_id=variant_id)),
    }

    data = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
        consistent_read=True,
    )

    # Move each item to the archive table
    for item in data:
        flow_item = models.Flow(
            **{k: v for k, v in item.items() if k not in flow_attributes_to_archive},
            flow_state_machine=safe_decompress_data(item, "flow_state_machine"),
            flow_states=safe_decompress_data(item, "flow_states"),
            flow_context_map=safe_decompress_data(item, "flow_context_map"),
            flow_utility_prompts=safe_decompress_data(item, "flow_utility_prompts"),
        )

        if flow_item.item_created_datetime != new_timestamp:
            await put_flow_to_dynamodb(archive_table, flow_item)
            await table.delete_item(Key={"PK": flow_item.PK, "SK": flow_item.SK})


async def put_flow_to_dynamodb(table, flow: models.Flow):
    # Compress flow_state_machine, flow_states, flow_context_map, flow_utility_prompts to make sure PUT operation is not overloaded
    flow.flow_state_machine = compress_data(flow.flow_state_machine)
    flow.flow_states = compress_data(flow.flow_states)
    flow.flow_context_map = compress_data(flow.flow_context_map)
    flow.flow_utility_prompts = compress_data(flow.flow_utility_prompts)

    await table.put_item(Item=flow.model_dump(exclude={"flow_context_variables"}, exclude_none=True))


async def create_flow_metadata(flow_item: models.Flow) -> dict:
    """Create flow metadata in the chatbot table. N.B: This is only called for NON
    TEMPLATE flows.

    Parameters:
    - flow_item (StateMachineItem): The flow metadata to create.
    Returns:
    - dict: A dictionary containing the message that the flow metadata was created successfully.
    """
    async with dynamodb.DynamoDBClient() as client_db:
        table = await client_db.Table(ChatbotTable.get_table_name())
        archive_table = await client_db.Table(FlowsArchiveTable.get_table_name())
        creation_time = datetime.now().isoformat()

        # If the flow_item.SK already contains a creation time, remove it and add new creation time
        stripped_SK = flow_item.SK

        parts = flow_item.SK.split("#", 3)

        if len(parts) == 4:
            stripped_SK = "#".join(parts[:3])

        flow_item.SK = stripped_SK + f"#{creation_time}"

        await archive_old_flow_variants(
            flow_id=parts[1], variant_id=parts[2], table=table, archive_table=archive_table, new_timestamp=creation_time
        )
        await put_flow_to_dynamodb(table, flow_item)
        return {"message": "Flow metadata created successfully"}
