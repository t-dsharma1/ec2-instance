import time


def cache_results(expiration_seconds=600):  # Default expiration time in seconds (10 minutes)
    def decorator(func):
        cache = {}

        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = (func.__name__, args, frozenset(kwargs.items()))

            # Check if the item is in the cache and hasn't expired
            if key in cache and (current_time - cache[key]["time"]) < expiration_seconds:
                return cache[key]["result"]

            # Call the function and store the result along with the current time
            result = func(*args, **kwargs)
            cache[key] = {"result": result, "time": current_time}
            return result

        def clear_cache():
            """Clears all cache entries for this function."""
            cache.clear()

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator
