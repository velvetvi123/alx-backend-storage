#!/usr/bin/env python3
"""
Redis basic exercise
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


class Cache:
    """ Cache class to interact with Redis """

    def __init__(self):
        """ Initialize Redis connection and flush the database """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key and return the key.
        :param data: str, bytes, int or float
        :return: the generated key (str)
        """
        key = str(uuid.uuid4())  # Generate a random key
        self._redis.set(key, data)  # Store the data in Redis
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and apply an optional transformation function.
        :param key: the key in Redis
        :param fn: optional callable to transform the data
        :return: the original data or None if key does not exist
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """ Retrieve data as a UTF-8 string """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """ Retrieve data as an integer """
        return self.get(key, int)


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    :param method: the method to be decorated
    :return: the wrapped method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Increment the count each time the method is called """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.
    :param method: the method to be decorated
    :return: the wrapped method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Store input parameters and output in Redis """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))  # Store input arguments
        output = method(self, *args, **kwargs)  # Call the original method
        self._redis.rpush(output_key, output)  # Store output
        return output
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.
    :param method: the method to display the history for
    :return: None
    """
    redis_instance = method.__self__._redis
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for inp, out in zip(inputs, outputs):
        inp_str = inp.decode("utf-8")
        out_str = out.decode("utf-8")
        print(f"{method.__qualname__}(*{inp_str}) -> {out_str}")
