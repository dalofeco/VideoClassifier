import sys

NORMAL = 0;
SHOOTING = 1;
ROBBERY = 2;
EXPLOSION = 3;
FIGHTING = 4;

def labelToNum(label):
    if label == 'normal':
        return NORMAL;
    if label == 'shooting':
        return SHOOTING
    if label == 'robbery':
        return ROBBERY
    if label == 'explosion':
        return EXPLOSION
    if label == 'fighting':
        return FIGHTING
    else:
        print("ILLEGAL LABEL!")
        print(label)
        sys.exit();