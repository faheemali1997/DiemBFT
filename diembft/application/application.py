from diembft.block_tree.blockTree import BlockTree
from diembft.ledger.ledgerImpl import LedgerImpl
from diembft.certificates.qc import QC
from diembft.block_tree.voteinfo import VoteInfo
from diembft.utilities.constants import GENESIS, BYZANTINE_NODES, GENESIS_PARENT_ROUND, GENESIS_PARENT_ID, GENESIS_GRAND_PARENT_ID, GENESIS_GRAND_PARENT_ROUND
from diembft.safety.safety import Safety
from diembft.utilities.verifier import Verifier
from diembft.pacemaker.pacemaker import Pacemaker
from diembft.messages.proposalMsg import ProposalMsg
from diembft.leader_election.leaderElection import LeaderElection
from diembft.utilities.generateKeys import GenerateKeys
from diembft.messages.voteMsg import VoteMsg
from diembft.mem_pool.memPoolHelper import MemPoolHelper
from diembft.messages.timeOutMessage import TimeOutMessage
from diembft.certificates.timeOutCertficate import TimeOutCertificate
from diembft.block_tree.ledgerCommitInfo import LedgerCommitInfo
from diembft.block_tree.client_request import ClientRequest
from diembft.logger.logger import Logger
import logging


class Application:

    def __init__(self, mapper: dict, nodes: list, node_id: str, keys: list, timer_constant: int, mem_pool: MemPoolHelper, byzentine_nodes: int = 2):
        self.node_id = node_id
        self.mem_pool = mem_pool
        self.nodes = nodes
        self.verifier = Verifier(mapper, keys)
        self.ledger = LedgerImpl(self.node_id)
        self.genesis_qc = Application.generate_genesis_qc()
        self.block_tree = BlockTree(self.node_id, self.ledger, self.genesis_qc, byzentine_nodes)
        self.safety = Safety(self.block_tree, self.node_id, self.ledger, self.verifier)
        self.pacemaker = Pacemaker(self.safety, self.block_tree, byzentine_nodes, timer_constant)
        self.leader_election = LeaderElection(nodes, self.pacemaker, self.ledger)
        self.logger = Logger.get_logger(self.node_id)

    @staticmethod
    def generate_genesis_qc():
        genesis_vote_info = VoteInfo(
            GENESIS,
            0,
            GENESIS_PARENT_ID,
            -1,
            None
        )
        ledger_commit_info = LedgerCommitInfo(
            '',
            '',
            ClientRequest('', '')
        )
        return QC(
            genesis_vote_info,
            ledger_commit_info,
            0,
            []
        )

    def process_certificate_qc(self, qc: QC):
        if qc is not None:
            self.block_tree.process_qc(qc)
            self.leader_election.update_leaders(qc)
            self.pacemaker.advance_round_qc(qc)

    def process_proposal_msg(self, p: ProposalMsg):
        self.logger.log(logging.INFO, 'Node received proposal message and started processing')
        self.process_certificate_qc(p.block.qc)
        self.process_certificate_qc(p.high_commit_qc)
        self.pacemaker.advance_round_tc(p.last_round_tc)
        current_round = self.pacemaker.current_round
        curr_leader = self.leader_election.get_leader(current_round)
        if p.block.round != current_round or p.sender != curr_leader or p.block.author != curr_leader:
            return [None, None]
        self.block_tree.execute_and_insert(p.block)
        vote_msg = self.safety.make_vote(p.block, p.last_round_tc)
        if vote_msg is not None:
            # send vote msg
            next_leader = self.leader_election.get_leader(current_round + 1)
            return [vote_msg, next_leader]
        return [None, None]

    def process_timeout_msg(self, message: TimeOutMessage):
        self.logger.log(logging.INFO, 'Node received timeout message and started processing')
        self.process_certificate_qc(message.tmo_info.high_qc)
        self.process_certificate_qc(message.high_commit_qc)
        self.pacemaker.advance_round_tc(message.last_round_tc)
        tc = self.pacemaker.process_remote_timeout(message)
        if tc is not None and type(tc) == TimeOutCertificate:
            self.logger.log(logging.INFO, 'Node received timeout certificate and will start processing new round')
            self.pacemaker.advance_round_tc(tc)
            return self.process_new_round_event(tc)

        return tc

    def process_vote_msg(self, message: VoteMsg):
        self.logger.log(logging.INFO, 'Node received vote message and started processing')
        qc = self.block_tree.process_vote(message)
        if qc is not None:
            self.process_certificate_qc(qc)
            return self.process_new_round_event(None)

    def process_new_round_event(self, last_tc):
        self.logger.log(logging.INFO, 'Node started processing new round')
        curr_leader = self.leader_election.get_leader(self.pacemaker.current_round)
        if curr_leader == self.node_id:
            block = self.block_tree.generate_block(self.mem_pool.get_message(), self.pacemaker.current_round)
            # TODO: Send it to da file and let da file handle sending to all nodes
            return ProposalMsg(
                block,
                last_tc,
                self.block_tree.high_commit_qc,
                self.node_id
            )
        return None



# if __name__ == '__main__':

#     gn = GenerateKeys()
#     keys = gn.generate_key()

#     gn2 = GenerateKeys()
#     keys2 = gn2.generate_key()

#     mapper = dict()

#     node_1_id = 'node_id_1'
#     node_2_id = 'node_id_2'

#     mapper[node_2_id] = keys2[1]
#     mapper[node_1_id] = keys[1]

#     nodes = [node_2_id, node_1_id]

#     application = Application(
#         mapper,
#         nodes,
#         node_1_id,
#         keys,
#         4
#     )
#     #
#     # main2 = Application(
#     #     mapper,
#     #     nodes,
#     #     node_2_id,
#     #     keys2,
#     #     4
#     # )
#     #
#     # curr_round = application.pacemaker.current_round


#     # new_block = main2.block_tree.generate_block(['abc'], curr_round)
#     # qc = application.genesis_qc
#     # p = ProposalMsg(
#     #     new_block,
#     #     None,
#     #     qc,
#     #     'node_id_2'
#     # )

#     tn = application.pacemaker.local_timeout_round()
#     application.pacemaker.process_remote_timeout(tn)
