from prometheus_client import Counter, Gauge, Histogram, Summary
from prometheus_client.utils import INF

_LATENCY_BUCKETS = (
    0.005,
    0.01,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.0,
    3.0,
    4.0,
    5.0,
    6.0,
    7.0,
    8.0,
    9.0,
    10.0,
    12.0,
    15.0,
    20.0,
    25.0,
    30.0,
    40.0,
    50.0,
    INF,
)

_PROMPT_RESPONSE_LENGTH_BUCKETS = (1, 10, 25, 50, 75, 100, 150, 200, 500, INF)

llm_latency = Histogram(
    name="genie_llm_api_llm_latency_seconds",
    documentation="Tracks the latency of each LLM prompt.",
    labelnames=["service", "prompt_length", "model"],
    buckets=_LATENCY_BUCKETS,
)

llm_response_length_words = Histogram(
    name="genie_llm_api_llm_response_length_words",
    documentation="Tracks the response lengths of prompts in amount of words.",
    labelnames=["service", "model"],
    buckets=_PROMPT_RESPONSE_LENGTH_BUCKETS,
)

response_latency = Histogram(
    name="genie_llm_api_agent_response_latency_seconds",
    documentation="Tracks the latency of each AI response.",
    labelnames=["flow_id"],
    buckets=_LATENCY_BUCKETS,
)

conversations_handled = Counter(
    name="genie_llm_api_conversations_handled_total", documentation="Amount of cumulatively handled conversations"
)

prompts_handled = Counter(
    name="genie_llm_api_prompts_handled_total", documentation="Amount of cumulatively handled LLM-prompts."
)

prompt_length = Summary(
    name="genie_llm_api_prompt_length",
    documentation="Number of characters sent to LLM",
    labelnames=["service", "model"],
)

prompt_throttle_errors = Counter(
    name="genie_llm_api_prompt_throttle_errors_total",
    documentation="Tracks amount of throttling of LLM prompts.",
)

nb_active_conversations = Gauge(
    name="genie_llm_api_nb_active_conversations_total",
    documentation="Amount of currently active conversations",
)
