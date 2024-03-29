import logging

from diembft.certificates.timeOutCertficate import TimeOutCertificate
from diembft.certificates.qc import QC
from diembft.ledger.ledgerImpl import LedgerImpl
from diembft.block_tree.block import Block
from diembft.utilities.verifier import Verifier
from diembft.block_tree.voteinfo import VoteInfo
from diembft.block_tree.ledgerCommitInfo import LedgerCommitInfo
from diembft.messages.voteMsg import VoteMsg
from diembft.block_tree.blockTree import BlockTree
from diembft.pacemaker.timeoutInfo import TimeOutInfo
from diembft.logger.logger import Logger
from diembft.utilities.signature import Signature
import logging


class Safety(Logger):

    def __init__(self, block_tree: BlockTree, node_id, ledger: LedgerImpl, verifier: Verifier):
        self.private_key = ''
        self.public_keys = []
        self.highest_vote_round = 0
        self.highest_qc_round = -1
        self.ledger = ledger
        self.verifier = verifier
        self.block_tree = block_tree
        self.node_id = node_id
        # super().__init__(self.node_id)
        self.logger = Logger.get_logger(self.node_id)

    def increase_highest_vote_round(self, round):
        self.highest_vote_round = max(self.highest_vote_round, round)

    def update_highest_qc_round(self, qc_round ):
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    @staticmethod
    def check_consecutive(block_round, round):
        return round + 1 == block_round

    @staticmethod
    def safe_to_extend(block_round, qc_round, tc: TimeOutCertificate):
        return Safety.check_consecutive(block_round, tc.round) and qc_round >= max([t.round for t in tc.tmo_high_qc_rounds])

    def safe_to_vote(self, block_round, qc_round, tc: TimeOutCertificate):
        if block_round <= max(self.highest_vote_round, qc_round):
            return False
        return Safety.check_consecutive(block_round, qc_round) or self.safe_to_extend(block_round, qc_round, tc)

    def safe_to_timeout(self, current_round, qc_round, tc: TimeOutCertificate):
        if qc_round < self.highest_qc_round or current_round <= max(self.highest_vote_round - 1, qc_round):
            return False
        return Safety.check_consecutive(current_round, qc_round) or Safety.check_consecutive(current_round, tc.round)

    def commit_state_id_candidate(self, block_round, qc: QC):
        if Safety.check_consecutive(block_round, qc.vote_info.round):
            return self.ledger.pending_state(qc.vote_info.id)
        return None

    def valid_signatures_qc(self, qc: QC, tc: TimeOutCertificate):
        return self.valid_signatures(qc, tc)

    def valid_signatures(self, qc: QC, tc: TimeOutCertificate):

        # if qc is not None:
        #     signatures = qc.signatures
        #     for signature in signatures:
        #         node_id, message = signature.node_id, signature.message
        #         if not self.verifier.verify(node_id, message):
        #             self.log_debug('QC verification failed : for node_id: ' + node_id + ' and message: ' + message)
        #             return False
        #
        # if tc is not None:
        #     for signature in tc.tmo_signatures:
        #         node_id, message = signature.node_id, signature.message
        #         if not self.verifier.verify(node_id, message):
        #             self.log_debug('TC verification failed : for node_id: ' + node_id + ' and message: ' + message)
        #             return False

        self.logger.log(logging.INFO, 'Node Verified Signatures and are valid')
        return True

    def valid_signatures_block(self, b: Block, tc: TimeOutCertificate):
        return self.valid_signatures(b.qc, tc)

    # public methods
    def make_vote(self, b: Block, last_tc: TimeOutCertificate):
        qc_round = b.qc.vote_info.round
        if self.valid_signatures_block(b, last_tc) and self.safe_to_vote(b.round, qc_round, last_tc):
            self.update_highest_qc_round(qc_round)
            self.increase_highest_vote_round(b.round)
            vote_info = VoteInfo(
                b.id,
                b.round,
                b.qc.vote_info.id,
                qc_round,
                self.ledger.pending_state(b.id)
            )
            ledger_commit_info = LedgerCommitInfo(
                self.commit_state_id_candidate(b.round, b.qc),
                Verifier.encode(str(vote_info)),
                b.client_request
            )
            self.logger.log(logging.INFO, 'Node Sending Vote Message to Next Leader')
            return VoteMsg(
                vote_info,
                ledger_commit_info,
                self.block_tree.high_commit_qc,
                self.node_id,
                Signature(
                    self.node_id,
                    self.verifier.sign(str(ledger_commit_info))
                )
            )
        return None

    def make_timeout(self, round: int, high_qc: QC, last_tc: TimeOutCertificate):
        qc_round = high_qc.vote_info.round
        if self.valid_signatures_qc(high_qc, last_tc) and self.safe_to_timeout(round, qc_round, last_tc):
            self.increase_highest_vote_round(round)
            self.logger.log(logging.INFO, 'Node Timing out')
            return TimeOutInfo(
                round,
                high_qc,
                self.node_id,
                Signature(
                    self.node_id,
                    self.verifier.sign(str(round) + str(high_qc.round))
                )
            )
        return None

