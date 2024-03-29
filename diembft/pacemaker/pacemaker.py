from diembft.certificates.timeOutCertficate import TimeOutCertificate
from diembft.safety.safety import Safety
from diembft.block_tree.blockTree import BlockTree
from diembft.messages.timeOutMessage import TimeOutMessage
import time
from diembft.certificates.qc import QC
from collections import defaultdict
from diembft.logger.logger import Logger


class Pacemaker:

    def __init__(self, safety: Safety, block_tree: BlockTree, byzantine_nodes: int, timer_constant: int = 4):
        self.current_round = 0
        self.last_round_tc = None
        self.pending_timeouts = defaultdict(Pacemaker.default_function)
        self.timer_constant = timer_constant
        self.current_time = round(time.time() * 1000)
        self.safety = safety
        self.block_tree = block_tree
        self.f = byzantine_nodes
        self.current_time = round(time.time() * 1000)


    @staticmethod
    def default_function():
        return set()

    def get_round_timer(self):
        return 4 * self.timer_constant

    def stop_timer(self, current_round: int):
        self.current_time = None

    # Start new round and stop current round timer
    def start_timer(self, new_round):
        self.current_time = Pacemaker.get_round_timer()
        self.current_round = new_round

    def local_timeout_round(self):
        timeout_info = self.safety.make_timeout(self.current_round, self.block_tree.high_qc, self.last_round_tc)
        # TODO: Broadcast this : send it to da file and da file will send it to every node
        return TimeOutMessage(
            timeout_info,
            self.last_round_tc,
            self.block_tree.high_commit_qc
        )

    @staticmethod
    def find_sender_in_list(tmo_list, sender: str):

        for t in list(tmo_list):
            if t.sender == sender:
                return True

        return False

    def process_remote_timeout(self, tmo: TimeOutMessage):
        tmo_info = tmo.tmo_info
        if tmo_info.round < self.current_round:
            return None
        if tmo_info.sender and not Pacemaker.find_sender_in_list(self.pending_timeouts[tmo_info.round], tmo_info.sender):
            self.pending_timeouts[tmo_info.round].add(tmo_info)
        if len(self.pending_timeouts[tmo_info.round]) == self.f + 1:
            # stop timer
            return self.local_timeout_round()
        if len(self.pending_timeouts[tmo_info.round]) == 2*self.f + 1:
            return TimeOutCertificate(
                tmo_info.round,
                [t for t in self.pending_timeouts[tmo_info.round]],
                [t.signature for t in self.pending_timeouts[tmo_info.round]]
            )
        return None

    def advance_round_qc(self, qc: QC):
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        # start Timer
        self.current_round = qc.vote_info.round + 1
        return True

    def advance_round_tc(self, tc: TimeOutCertificate):
        print(tc)
        if tc is None or tc.round < self.current_round:
            return False
        self.last_round_tc = tc
        self.current_round = tc.round + 1
        # start timer
        return True





