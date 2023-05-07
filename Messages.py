from dataclasses import dataclass, field
from typing import List, Any
from datetime import datetime
from time import time

@dataclass
class ConfigureActor:
    other_actor_queues: List[Any]
    actor_name: str
    num_benchmark_msgs_per_actor: int
    benchmark_message_send_period_s: float

@dataclass
class BenchmarkMessage:
    sending_actor_name: str
    sending_actor_msg_index: int
    sending_timestamp: time

@dataclass
class AskIfDone: pass

@dataclass
class AskNumReceived: pass

@dataclass
class GetMessageSummary: pass