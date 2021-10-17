from diembft.application.application import Application
from diembft.utilities.generateKeys import GenerateKeys
from diembft.mem_pool.memPoolHelper import MemPoolHelper
from diembft.mem_pool.message import Message
from diembft.block_tree.client_request import ClientRequest

if __name__ == '__main__':

    nodes_length, apps, nodes = 4, [], []

    nodes_to_public_key_mapper = dict()
    nodes_to_key_mapper = dict()
    nodes_to_id_mapper = dict()

    for node in range(nodes_length):
        node = str(node)
        gen = GenerateKeys()
        nodes_to_public_key_mapper[node] = gen.public_key
        nodes_to_key_mapper[node] = gen.generate_key()
        nodes.append(node)

    for node in range(nodes_length):
        node = str(node)
        mem_pool = MemPoolHelper()
        app = Application(
            nodes_to_public_key_mapper,
            nodes,
            node,
            nodes_to_key_mapper[node],
            4,
            mem_pool
        )
        apps.append(
            app
        )
        nodes_to_id_mapper[node] = app

    message = Message(
        ['Add'],
        None,
        ClientRequest(
            '1',
            '1'
        )
    )

    for app in apps:
        app.mem_pool.put_message(message)

    proposal_first, leader = None, None

    for i, app in enumerate(apps):

        if app.leader_election.get_leader(app.pacemaker.current_round) == str(i):
            app.pacemaker.current_round += 1
        proposal_msg = app.process_new_round_event(None)

        if proposal_msg is not None:
            # its the leader
            # send to all other nodes

            for _a in apps:

                vote_msg, _next_leader = _a.process_proposal_msg(proposal_msg)
                new_proposal_msg = nodes_to_id_mapper[_next_leader].process_vote_msg(vote_msg)
                if new_proposal_msg is not None:
                    # send the new proposal to all nodes
                    proposal_first = new_proposal_msg
                    leader = nodes_to_id_mapper[_next_leader]
                    break

            if proposal_first is not None:
                break

    while proposal_first is not None:

        # send to all nodes

        for _a in apps:

            vote_msg, _next_leader = _a.process_proposal_msg(proposal_first)
            new_proposal_msg = nodes_to_id_mapper[_next_leader].process_vote_msg(vote_msg)
            if new_proposal_msg is not None:
                proposal_first = new_proposal_msg
                leader = nodes_to_id_mapper[_next_leader]
                break

