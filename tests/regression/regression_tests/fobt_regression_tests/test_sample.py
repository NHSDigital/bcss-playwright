class Employee:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def promote(self, new_position):
        self.position = new_position 