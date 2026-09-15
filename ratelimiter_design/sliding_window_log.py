# In memory design (single machine with multiple threads)

import time
import threading
from collections import deque

class RequestTimestamps:
    def __init__(self, requests: int, window_time_in_sec: int) -> None:

        # A 100 req/min means = 100 requests in window_time = 60 seconds.
        self.lock = threading.Lock()
        self.timestamps = deque()
        self.window_time_in_sec = window_time_in_sec
        self.requests = requests
    
    # evict timestamps older than current from deque.
    def evict_older_timestamps(self, curr_timestamp):
        while len(self.timestamps) > 0 and (curr_timestamp -
                self.timestamps[0] > self.window_time_in_sec):
            self.timestamps.popleft()


class SlidingWindoLogRateLimiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.rate_limiter_store = {}

    @classmethod
    def get_current_timestamp(cls):
        # returns epoch time till seconds precision.
        return int(time.time())

    def add_user(self, user_id: str, requests: int, window_time_in_sec: int):
        with self.lock:
            if user_id in self.rate_limiter_store:
                raise Exception("user already present.")
            
            self.rate_limiter_store[user_id] = RequestTimestamps(requests, window_time_in_sec)
    
    def remove_user(self, user_id: str):
        with self.lock:
            if user_id in self.rate_limiter_store:
                del self.rate_limiter_store[user_id]
    
    def allow_service(self, user_id: str):
        with self.lock:
            if user_id not in self.rate_limiter_store:
                raise Exception("user is not present. please \
                        register the user first.")
        
        user_timestamps : RequestTimestamps = self.rate_limiter_store[user_id]

        with user_timestamps.lock:
            curr_timestamp = self.get_current_timestamp()

            # evict older timestamp
            user_timestamps.evict_older_timestamps(curr_timestamp)

            if len(user_timestamps.timestamps) >= user_timestamps.requests:
                return False
            
            user_timestamps.timestamps.append(curr_timestamp)

            return True








