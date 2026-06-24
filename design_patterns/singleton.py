import threading

class Counter:
    _instance = None
    _count = 0
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with Counter._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance
    
    def __init__(self):
        pass

    @staticmethod
    def increment():
        with Counter._lock:
            Counter._count += 1
        
        return Counter._count
    
    @staticmethod
    def get_count():
        return Counter._count
    

if __name__ == "__main__":
    c1 = Counter()
    c1.increment()
    print(c1.get_count())
    c2 = Counter()
    print(f"Same instance: {c1 is c2}")
    for _ in range(5):
        c1.increment()
    print(f"Count after 5 other increments: {c2.get_count()}")