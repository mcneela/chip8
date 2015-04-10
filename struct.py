import array from array

class MemStack:
    def __init__(self, size):
        self.items = array('B', (0 for i in range(size)))

    def pop(self):
        self.items.pop()

    def push(self, item):
        self.items.pop()
        self.items[-1] = item

    
        
    
