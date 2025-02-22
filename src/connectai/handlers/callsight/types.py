import dataclasses
from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, ValidationError

__all__ = ["CallsightResponse"]


class StepStatus(StrEnum):
    PENDING = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    SKIPPED = auto()
    ERROR = auto()


class PipelineStatus(StrEnum):
    RUNNING = auto()
    DONE = auto()
    DONE_WITH_ERRORS = auto()
    BLOCKED = auto()
    ERROR = auto()


class TimeMetrics(BaseModel):
    start_time: datetime
    finish_time: datetime


@dataclasses.dataclass
class CallsightResponse:
    input: dict[str, any]
    metadata: dict[str, any]
    responses: dict[str, any]
    step_status: dict[str, StepStatus]
    pipeline_metrics: TimeMetrics
    step_metrics: dict[str, TimeMetrics]
    pipeline_status: PipelineStatus


class CallsightResponseFactory:
    @staticmethod
    def create(payload_data: dict[str, any]) -> CallsightResponse:
        try:
            # Parse pipeline metrics
            pipeline_metrics = TimeMetrics(
                start_time=datetime.fromisoformat(payload_data["pipeline_metrics"]["start_time"]),
                finish_time=datetime.fromisoformat(payload_data["pipeline_metrics"]["finish_time"]),
            )

            # Parse step metrics
            step_metrics = {
                k: TimeMetrics(
                    start_time=datetime.fromisoformat(v["start_time"]),
                    finish_time=datetime.fromisoformat(v["finish_time"]),
                )
                for k, v in payload_data["step_metrics"].items()
            }

            # Create CallsightResponse instance
            callsight_response_instance = CallsightResponse(
                input=payload_data["input"],
                metadata=payload_data["metadata"],
                responses=payload_data["responses"],
                step_status={k: StepStatus[v.upper()] for k, v in payload_data["step_status"].items()},
                pipeline_metrics=pipeline_metrics,
                step_metrics=step_metrics,
                pipeline_status=PipelineStatus[payload_data["pipeline_status"].upper()],
            )

            return callsight_response_instance

        except KeyError as e:
            raise ValueError(f"Missing key in payload data: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation error: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing payload: {e}")
