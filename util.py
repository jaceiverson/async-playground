# standard library
import asyncio
from time import perf_counter_ns
from functools import wraps

# Optional pypi install for pretty outputs
from rich.console import Console


# way to over-engieered timeing decorator | thanks chat-gpt
# works with async and sync programing
def timeit(
    output: bool = True,
    rich_console: None | Console = None,
    return_time: bool = True,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def wrapped_func():
                    start = perf_counter_ns()
                    result = await func(*args, **kwargs)
                    end = perf_counter_ns()
                    if output:
                        if isinstance(rich_console, Console):
                            rich_console.print(
                                f"[green]{func.__name__:<10}[/green]: {end-start:>10,} ns",
                                style="bold",
                            )
                        else:
                            print(f"{func.__name__:<10}: {end-start:>10,} ns")
                    return (result, end - start) if return_time else result

                return wrapped_func()
            else:
                # synchronous wrapper
                start = perf_counter_ns()
                result = func(*args, **kwargs)
                end = perf_counter_ns()
                if output:
                    if isinstance(rich_console, Console):
                        rich_console.print(
                            f"[green]{func.__name__:<10}[/green]: {end-start:>10,} ns",
                            style="bold",
                        )
                    else:
                        print(f"{func.__name__:<10}: {end-start:>10,} ns")
                return (result, end - start) if return_time else result

        return wrapper

    return decorator
