import ray

from back.config import settings


class NoOpRemote:
    def __call__(self, *args, **kwargs):
        pass
    def remote(self, *args, **kwargs):
        pass
    def options(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        def no_op(*args, **kwargs):
            pass
        return no_op

def ray_task(*args_decorator, **kwargs_decorator):
    """
    This decorator wraps a function to be a Ray task and only runs the function if Ray is enabled.
    """
    def decorator(func):        
        if settings.USE_RAY:
            @ray.remote(*args_decorator, **kwargs_decorator)
            def wrapped_func(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapped_func
        else:
            print(f"Skipping {func.__name__} (Ray disabled)")
            return NoOpRemote()
    return decorator