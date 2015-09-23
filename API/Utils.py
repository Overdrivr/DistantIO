from collections import deque

class ValuesXY:
    def __init__(self,buffersize):
        self.x = deque(maxlen=buffersize)
        self.y = deque(maxlen=buffersize)

    def append(self,x,y):
        self.x.append(x)
        self.y.append(y)
