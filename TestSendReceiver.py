from thespian.actors import *
from Messages import *
import time
from typing import cast
from datetime import datetime
class TestSendReceiver(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(TestSendReceiver, self).__init__(*args, **kw)
        self.finished_sending = False
        self.current_actor_index = 0
        self.message_count = 0
        self.benchmark_messages = []

        self.config = None
        cast(self.config, ConfigureActor)

    # Receive configuration including test details and information about this instance of actor
    def receiveMsg_ConfigureActor(self, config: ConfigureActor, sender):
        self.config = config
        self.wakeupAfter(self.config.benchmark_message_send_period_s)

    # Receive a message from another actor and track it internally
    def receiveMsg_BenchmarkMessage(self, benchmark_message: BenchmarkMessage, sender):
        receipt_time = time.time()
        if benchmark_message.sending_actor_msg_index > 0:
            '''
            entry = {
                "receiving_actor_name": self.config.actor_name,
                "sending_actor_name": benchmark_message.sending_actor_name,
                "sending_actor_msg_index": benchmark_message.sending_actor_msg_index - 1,
            }
            '''
            actor_name_confirm = ('sending_actor_name', benchmark_message.sending_actor_name)
            msg_index_confirm = ("sending_actor_msg_index", benchmark_message.sending_actor_msg_index - 1)
            proceeding_msg_received = any([actor_name_confirm in d.items() and msg_index_confirm in d.items() for d in self.benchmark_messages])
        else:
            proceeding_msg_received = True

        new_entry = {
            "receiving_actor_name": self.config.actor_name,
            "sending_actor_name": benchmark_message.sending_actor_name,
            "sending_actor_msg_index": benchmark_message.sending_actor_msg_index,
            "sending_timestamp": benchmark_message.sending_timestamp,
            "receiving_timestamp": receipt_time,
            "timestamp_diff": (receipt_time - benchmark_message.sending_timestamp),
            "proceeding_msg_received": proceeding_msg_received
        }
        self.benchmark_messages.append(new_entry)
        # if self.config.actor_name == "0":
             # print(new_entry)


    # Getter Function
    def receiveMsg_AskIfDone(self, message, sender):
        self.send(sender, self.finished_sending)

    # Getter Function
    def receiveMsg_GetMessageSummary(self, message, sender):
        self.send(sender, self.benchmark_messages)

    # Getter Function
    def receiveMsg_AskNumReceived(self, message, sender):
        self.send(sender, len(self.benchmark_messages))


    # On wakeup, send a message to the next actor
    def receiveMsg_WakeupMessage(self, message, sender):
        # Check if time to move onto next actor
        if self.message_count > self.config.num_benchmark_msgs_per_actor:
            self.message_count = 0
            self.current_actor_index = self.current_actor_index + 1

        # Check if test is complete
        if self.current_actor_index >= len(self.config.other_actor_queues):
            self.finished_sending = True

        # Check if test still in progress, if so, send next message and queue next message send
        if not self.finished_sending:
            self.send(
                self.config.other_actor_queues[self.current_actor_index],
                BenchmarkMessage(
                    sending_actor_name=self.config.actor_name,
                    sending_actor_msg_index=self.message_count,
                    sending_timestamp=time.time()
                )
            )
            self.message_count = self.message_count + 1
            self.wakeupAfter(self.config.benchmark_message_send_period_s)