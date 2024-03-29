from diembft.block_tree.block import Block
from diembft.certificates.qc import QC
from diembft.ledger.ledgerImpl import LedgerImpl
from diembft.messages.voteMsg import VoteMsg
from diembft.utilities.constants import BYZANTINE_NODES, GENESIS_PARENT_ID, GENESIS_GRAND_PARENT_ID
from diembft.utilities.verifier import Verifier
from diembft.block_tree.blockId import BlockId
from diembft.utilities.constants import GENESIS
from diembft.mem_pool.message import Message
from diembft.block_tree.voteinfo import VoteInfo


class BlockTree:
    def __init__(self, node_id, ledger: LedgerImpl, genesis_qc: QC, byzentine_nodes: int = BYZANTINE_NODES):
        self.pending_block_tree = []
        self.pending_votes = {}
        # TODO: high_qc should be parent of genesis
        self.high_qc: QC = genesis_qc
        # TODO: Change this to genesis_parent_qc
        self.high_commit_qc: QC = genesis_qc  # At the start we have the genesis QC as the high_qc
        self.node_id = node_id
        self.ledger = ledger
        self.byzentine_nodes = byzentine_nodes
        self.high_qc: QC = genesis_qc
        # TODO: Change this to genesis_parent_qc
        self.genesis_parent_vote_info = VoteInfo(
            GENESIS_PARENT_ID,
            self.high_qc.vote_info.round - 1,
            GENESIS_GRAND_PARENT_ID,
            self.high_qc.vote_info.parent_round - 1,
            None
        )
        self.high_commit_qc = QC(
            self.genesis_parent_vote_info,
            None,
            self.genesis_parent_vote_info.round,
            None
        )  # At the start we have the genesis QC as the high_qc
        self.node_id = node_id
        self.ledger = ledger
        self.byzentine_nodes = byzentine_nodes

    def generate_block(self, message: Message, current_round):

        # Create a BlockId object and hash it.
        block_id = BlockId(self.node_id, current_round, message.transactions, self.high_qc, message.client_request)

        hash_id = Verifier.encode(str(block_id))

        return Block(self.node_id, current_round, message.transactions, self.high_qc, hash_id, message.client_request)

    def execute_and_insert(self, b: Block):

        self.ledger.speculate(b.qc.vote_info.id, b.id, b)

        self.pending_block_tree.append(b.qc.vote_info.parent_id)

    def process_vote(self, v: VoteMsg):

        self.process_qc(v.high_commit_qc)

        vote_idx = Verifier.encode(str(v.ledger_commit_info))

        if vote_idx in self.pending_votes.keys():
            self.pending_votes[vote_idx].append(v.signature)
        else:
            self.pending_votes[vote_idx] = [v.signature]

        if len(self.pending_votes[vote_idx]) == 2 * self.byzentine_nodes + 1:
            # Create a QC
            qc = QC(
                v.vote_info,
                v.ledger_commit_info,
                v.vote_info.round,
                self.pending_votes[vote_idx]
            )
            return qc

        return None

    def process_qc(self, qc: QC):

        if qc is not None and qc.ledger_commit_info and qc.ledger_commit_info.commit_state_id is not None:

            if qc.vote_info.parent_id != GENESIS and qc.vote_info.parent_id != GENESIS_PARENT_ID and qc.vote_info.parent_id != GENESIS_GRAND_PARENT_ID:
                self.ledger.commit(qc.vote_info.parent_id)

                if qc.vote_info.parent_id in self.pending_votes:
                    self.pending_block_tree.remove(qc.vote_info.parent_id)

            self.high_commit_qc = qc if qc.vote_info.round > self.high_commit_qc.round else self.high_commit_qc

            # self.high_commit_qc = max(qc, self.high_commit_qc, key=lambda a, b: a.vote_info.round > b.vote_info.round)

        # self.high_qc = max(qc, self.high_qc, key=lambda a, b: a.vote_info.round > b.vote_info.round)
        self.high_qc = (qc if qc.vote_info.round > self.high_qc.round else self.high_qc)
