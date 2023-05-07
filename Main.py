import time

from thespian.actors import ActorSystem
from TestSendReceiver import TestSendReceiver
from Messages import ConfigureActor, AskIfDone, GetMessageSummary, AskNumReceived
from functools import reduce
import csv

# Configure the test
NUM_ACTORS = 20
BENCHMARK_MESSAGE_SEND_PERIOD_S = 0.01
NUM_BENCHMARK_MESSAGES_PER_ACTOR = 50
COOLDOWN_PERIOD_S = 2
# ACTOR_SYS = 'simpleSystemBase'
# ACTOR_SYS = 'multiprocQueueBase'
ACTOR_SYS = 'multiprocTCPBase'
# ACTOR_SYS = 'multiprocUDPBase'


if __name__ == "__main__":
    ActorSystem().shutdown()
    if ACTOR_SYS == "multiprocTCPBase":
        actor_sys = ActorSystem(ACTOR_SYS)
        # actor_sys = ActorSystem(ACTOR_SYS, capabilities={'Convention Address.IPv4': 'localhost:56800', 'Admin Port': 56801})
        # actor_sys = ActorSystem(ACTOR_SYS, capabilities={'Admin Port': 8081})
    elif ACTOR_SYS == "multiprocUDPBase":
        actor_sys = ActorSystem(ACTOR_SYS)
        # actor_sys = ActorSystem(ACTOR_SYS, capabilities={'Admin Port': 8082})
    else:
        actor_sys = ActorSystem(ACTOR_SYS)

    # initialize all actors
    actor_queues = []
    for i in range(NUM_ACTORS):
        actor_queues.append(actor_sys.createActor(TestSendReceiver))

    # Generate and share actor configs (telling all actors about the types of test we want to run and their unique ID
    configs = [ConfigureActor(
                    other_actor_queues=actor_queues,
                    actor_name=str(i),
                    num_benchmark_msgs_per_actor=NUM_BENCHMARK_MESSAGES_PER_ACTOR,
                    benchmark_message_send_period_s=BENCHMARK_MESSAGE_SEND_PERIOD_S
                ) for i in range(NUM_ACTORS)]
    [actor_sys.tell(actor_queues[i], configs[i]) for i in range (NUM_ACTORS)]

    # Print test status (a list of ints representing the number of messages each actor has received
    all_actors_finished = False
    while not all_actors_finished:
        all_actors_finished = all([actor_sys.ask(actor, AskIfDone(), 1) for actor in actor_queues])
        print([actor_sys.ask(actor, AskNumReceived(), 1) for actor in actor_queues])
        actor_sys.listen(1)

    # Actors may be finished once they've sent all their messages
    # Let the system run for a few more seconds to let all actors have time to process messages
    print("Cooling Down")
    actor_sys.listen(COOLDOWN_PERIOD_S)

    # Ask actors for all the details of received messages
    summary_dicts_per_actor = [actor_sys.ask(actor, GetMessageSummary(), 1) for actor in actor_queues]
    summary_dicts = []
    for summary_dict in summary_dicts_per_actor:
        summary_dicts.extend(summary_dict)

    # Export details to a csv file for review
    print("Saving Results")
    with open('summary.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "receiving_actor_name",
            "sending_actor_name",
            "sending_actor_msg_index",
            "sending_timestamp",
            "receiving_timestamp",
            "timestamp_diff",
            "proceeding_msg_received",
        ])
        writer.writeheader()
        for row in summary_dicts:
            writer.writerow(row)

    # Shutdown Actor System
    print("Shutdown")
    actor_sys.shutdown()