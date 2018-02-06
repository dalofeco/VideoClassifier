class Categories():
    def __init__(self):
        self.NORMAL = 0;
        self.SHOOTING = 1;
        self.ROBBERY = 2;
        self.EXPLOSION = 3;
        self.FIGHTING = 4;
        
    def labelToNum(self, label):
        if label == 'normal':
            return self.NORMAL;
        if label == 'shooting':
            return self.SHOOTING
        if label == 'robbery':
            return self.ROBBERY
        if label == 'explosion':
            return self.EXPLOSION
        if label == 'fighting':
            return self.FIGHTING