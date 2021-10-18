from diembft.utilities.nop import Nop
from diembft.mem_pool.message import Message
from threading import Lock

"""
MemPool class takes care of two things:
1. When a replica receives client request, it checks if it has already processed the request.
   If so, it will forward the response 

"""

class MemPool:

    def __init__(self):
        self.queue = []
        self.lock = Lock()

    # Only Leader deques
    def deque(self):

        queue = self.queue

        if len(queue) > 0:
            return queue.pop(0)

        return None

    # Client enques as there can be multiple clients, use lock to synchronize
    def enque(self, message: Message):
        self.queue.append(message)
        self.queue.append(Nop('-1', ''))
        self.queue.append(Nop('-1', ''))

