from collections import OrderedDict


class OrderedSet:
    """
    window: a window size of elements to keep track of. last `window` number of elements are in kept in the set.
    """

    def __init__(self, window: int = 100):
        self.limit = window
        self.dict = OrderedDict()  # Ordered dict preserves the insertion order of the items.

    def add(self, data: str):
        if len(self.dict.keys()) >= self.limit:
            self.dict.popitem(last=False)
        self.dict[data] = None  # put `None` in the ordered dictionary since we will only use the key set.

    def __contains__(self, data):
        if data in self.dict:
            return True
        else:
            return False

    def __len__(self):
        return len(self.dict.keys())


if __name__ == '__main__':
    set = OrderedSet()
    for i in range(1000, 0, -1):
        set.add(str(i))

    print(f'size: {len(set)}')

    for i in range(100, 0, -1):
        if str(i) in set:
            print(f'set contains: {i}')
        else:
            print(f'set does not contain: {i}')

    print(f'size: {len(set)}')
