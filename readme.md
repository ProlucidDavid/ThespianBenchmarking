# Thespian Benchmarking Repo

## Intro
The goal of this repo is to benchmark the Thespian actor framework in its different ActorSystem Implementations. The test (defined in main.py) spins up a number of custom actors (of class TestSendReceiver) who send each other messages and record when these messages are received. Tests can be tweaked by modifying the constants in main.py

## Test Results
Tests Results discussed below have been run on a Windows 10 environment

### simpleSystemBase
All tests with this ActorSystem have run successfully.

### multiprocQueueBase
The following combination of configuration has been observed to cause the application to freeze.

```python
# Configure the test
NUM_ACTORS = 20
BENCHMARK_MESSAGE_SEND_PERIOD_S = 0.01
NUM_BENCHMARK_MESSAGES_PER_ACTOR = 50
COOLDOWN_PERIOD_S = 2
ACTOR_SYS = 'multiprocQueueBase'
```
Generally, this ActorSystem has been observed to freeze when there is a combination of: more parallel actors increases, higher frequency of messages sends or larger number of test messages being sent

Worth noting, in section 9.3.1 of the [Thespian project docs](https://thespianpy.com/doc/using.pdf), there is an issue with multiprocQueueBase described as "an unexplained, core-level concern about dropped messages/deadlocks for the queue messaging in overload conditions.

### multiprocTCPBase
This ActorSystem has not been observed to successfully run. The following error is observed each time it is executed:
```commandline
2023-05-07 16:54:27,412 WARNING =>  Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, 0): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed  [IPBase.py:16]
2023-05-07 16:54:27,415 WARNING =>  Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, AddressInfo.AI_PASSIVE): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed  [IPBase.py:16]
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, 0): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, AddressInfo.AI_PASSIVE): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, 0): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, AddressInfo.AI_PASSIVE): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed
Traceback (most recent call last):
  File "C:\Git\Scratch\ThespianBenchmarking\Main.py", line 23, in <module>
    actor_sys = ActorSystem(ACTOR_SYS)
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\actors.py", line 637, in __init__
    systemBase = self._startupActorSys(
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\actors.py", line 678, in _startupActorSys
    systemBase = sbc(self, logDefs=logDefs)
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\system\multiprocTCPBase.py", line 28, in __init__
    super(ActorSystemBase, self).__init__(system, logDefs)
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\system\multiprocCommon.py", line 83, in __init__
    super(multiprocessCommon, self).__init__(system, logDefs)
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\system\systemBase.py", line 326, in __init__
    self._startAdmin(self.adminAddr,
  File "C:\Users\***************\.virtualenvs\ThespianBenchmarking-5ebENAd8\lib\site-packages\thespian\system\multiprocCommon.py", line 115, in _startAdmin
    raise InvalidActorAddress(adminAddr,
thespian.actors.InvalidActorAddress: ActorAddr-(T|:1900) is not a valid ActorSystem admin

Process finished with exit code 1
```

This behaviour is observed even when different ActorSystem `capabilities` are defined (see commented out code in main.py) 

### multiprocUDPBase
This ActorSystem has been observed with some quirkyness:
* This test can fail if message size is too large which can happen if too many messages are tested. This is expected as it is described in the [docs](https://thespianpy.com/doc/using.pdf) which state that it "can only exchange messages up to 64KiB in size. Larger messages will
fail."
* On startup warnings similar to those copied below can be observed but the test will run successfully
```commandline
2023-05-07 16:34:43,987 WARNING =>  Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, AddressInfo.AI_PASSIVE): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed  [IPBase.py:16]
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, 0): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed
WARNING:root:Unable to get address info for address *************** (AddressFamily.AF_INET, SocketKind.SOCK_DGRAM, 17, AddressInfo.AI_PASSIVE): <class 'socket.gaierror'> [Errno 11001] getaddrinfo failed```

