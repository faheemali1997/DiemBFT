class FileHandler:

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.file_name = "ledger_" + str(self.node_id) + ".txt"

    def write_file(self, data):
        with open(self.file_name, "a") as file:
            file.write(data)
