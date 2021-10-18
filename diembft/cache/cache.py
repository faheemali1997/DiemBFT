from collections import defaultdict
from diembft.block_tree.client_request import ClientRequest


class Cache:

    def __init__(self):
        self.cache = defaultdict(Cache.get_default_set)

    @staticmethod
    def get_default_set():
        return set()

    def check_request_id(self, client_request: ClientRequest):

        if client_request.client_id not in self.cache:
            return False

        return client_request.request_id in self.cache[client_request.client_id]

    def put_request_id(self, client_request: ClientRequest):

        self.cache[client_request.client_id].add(client_request.request_id)

