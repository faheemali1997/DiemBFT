class FileHandler:

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.file_name = "ledger_" + str(self.node_id) + ".txt"
        self.file_handle = open(self.file_name, "a")

    def write_file(self, data):
        with open(self.file_name, "a"):
            self.file_handle.write(data)
            self.file_handle.flush()
