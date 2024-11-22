class Queue:
    def __init__(self):
        self._queue = []
        self._mode = 'FIFO'  

    def set_mode(self, mode):
        if mode in ['FIFO', 'LIFO']:
            self._mode = mode
        else:
            raise ValueError("Mode must be 'FIFO' or 'LIFO'")

    def enqueue(self, item):
        self._queue.append(item)

    def dequeue(self):
        if not self._queue:
            return None
        if self._mode == 'FIFO':
            return self._queue.pop(0)  
        else:  # LIFO
            return self._queue.pop() 

    def get_queue(self):
        return self._queue

    def size(self):
        return len(self._queue)