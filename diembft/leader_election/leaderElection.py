import random
from diembft.utilities.constants import WINDOW_SIZE, EXCLUDE_SIZE, GENESIS_PARENT_ID, GENESIS_GRAND_PARENT_ID, GENESIS
from diembft.certificates.qc import QC
from diembft.ledger.ledgerImpl import LedgerImpl
from diembft.block_tree.block import Block
from diembft.pacemaker.pacemaker import Pacemaker


class LeaderElection:

    def __init__(self, validators, pace_maker: Pacemaker, ledger: LedgerImpl):
        self.validators = validators  # All the nodes - the node that is proposing the message
        self.window_size = WINDOW_SIZE
        self.exclude_size = EXCLUDE_SIZE
        self.reputation_leaders = {}
        self.pace_maker = pace_maker
        self.ledger = ledger

    def elect_reputation_leader(self, qc: QC):

        # Validators that signed the last window_size committed blocks
        active_validators = []

        # Ordered set of authors of last exclude_size committed blocks
        last_authors = []
        current_qc = qc
        i = 0
        while i < self.window_size or len(last_authors) < self.exclude_size:

            if current_qc.vote_info.parent_id == GENESIS or current_qc.vote_info.parent_id == GENESIS_GRAND_PARENT_ID or current_qc.vote_info.parent_id == GENESIS_PARENT_ID:
                return self.get_leader(self.pace_maker.current_round)

            # Block committed for the round r-2
            current_block: Block = self.ledger.committed_block(current_qc.vote_info.parent_id)

            # Author of the block committed in round r-2
            block_author = current_block.author

            if i < self.window_size:
                active_validators.append(self.get_signature_signer(current_qc.signatures))

            # Adding the latest Exclude_size of authors to the list
            if len(last_authors) < self.exclude_size:
                last_authors.append(block_author)

            current_qc = current_block.qc

            i = i + 1

        # To convert the list to an ordered set of last_authors
        last_authors = list(dict.fromkeys(last_authors))

        # Final list of active_validators after removing the nodes that were authors in Excluded_Size of rounds.
        active_validators = [x for x in active_validators if x not in last_authors]

        # To generate pseudo random numbers based on the round number
        random.seed(qc.vote_info.round)

        return active_validators[random.randint(0, len(active_validators) - 1)]

    @staticmethod
    def get_signature_signer(signatures: list):
        signers = []
        for signature in signatures:
            signers.append(signature.node_id)

        return signers

    def update_leaders(self, qc: QC):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = self.pace_maker.current_round
        if extended_round + 1 == qc_round and \
                qc_round + 1 == current_round and \
                qc.vote_info.parent_id != GENESIS_PARENT_ID and \
                qc.vote_info.parent_id != GENESIS:
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(qc)

    def get_leader(self, round):

        if round in self.reputation_leaders.keys():
            return self.reputation_leaders[round]
        index = (round // 2) % len(self.validators)

        # Simply return a leader by round robin selection
        return self.validators[index]
