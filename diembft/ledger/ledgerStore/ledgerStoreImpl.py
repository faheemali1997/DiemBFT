from treelib import Tree
from diembft.block_tree.block import Block
from diembft.ledger.ledgerStore.ledgerStore import LedgerStore
from diembft.utilities.constants import GENESIS, GENESIS_PARENT_ID, GENESIS_GRAND_PARENT_ID


class LedgerStoreImpl(LedgerStore):

    def __init__(self):
        super().__init__()
        self.tree = Tree()
        self.tree.create_node(identifier=GENESIS, tag=GENESIS, data=None)

    def add(self, block_id, exec_state_id, prev_block_id, block: Block):
        # tag = exec_state_id
        # identifier = block_id
        # parent = prev_block_id
        # data = Block
        something = self.tree.create_node(identifier=block_id, tag=exec_state_id, parent=prev_block_id, data=block)

        self.show()

        return something

    def delete(self, block_id):
        return self.tree.remove_node(block_id)

    def find(self, block_id):
        return self.tree.get_node(block_id)

    def prune(self, block_id):

        if block_id == GENESIS or block_id == GENESIS_PARENT_ID or block_id == GENESIS_GRAND_PARENT_ID:
            return

        node = self.tree.get_node(block_id)

        parent_node_id = node.predecessor(self.tree.identifier)

        sibling_nodes = self.tree.children(parent_node_id)

        for n in sibling_nodes:
            if n.identifier != block_id:
                self.tree.remove_node(n.identifier)

    def show(self):
        self.tree.show()


# # Testing
# c = LedgerStoreImpl()
#
# c.add(1, "StateId1", -100 , Block())
# c.add(100, 2, "Add")
# c.add(100, 3, "Add")
# c.add(3, 4, "Add")
# c.add(3, 5, "Add")
# c.add(3, 6, "Add")
# c.add(2, 7, "Add")
# c.add(2, 8, "Add")
#
# c.show()
# c.prune(5)
# c.show()
