import asyncio
import aiohttp
from time import sleep
import requests
from rich.console import Console
from rich.table import Table
from util import timeit

console = Console()


async def api_call():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://example.com", ssl=False) as response:
            return response.status == 200


def api_call_linear():
    response = requests.get("https://example.com")
    return response.status_code == 200


async def fake_api_call():
    await asyncio.sleep(1)
    return True


def fake_api_call_linear():
    sleep(1)
    return True


@timeit(output=False, rich_console=console)
async def run_api_calls(lambda_urls, api_function):
    semaphore = asyncio.Semaphore(100)
    tasks = []
    async with semaphore:
        for _ in lambda_urls:
            task = asyncio.create_task(api_function())
            tasks.append(task)
        done, pending = await asyncio.wait(tasks)
        responses = [t.result() for t in done]
    return responses


@timeit(output=False, rich_console=console)
def run_api_calls_linear(urls, api_function):
    return [api_function() for _ in urls]


def compare_speedups(ranges: list | None = None, include_sleep_comparison: bool = True):
    if ranges is None:
        ranges = [1, 5, 10]

    table = Table(
        title=f"Async vs Sync Comparison for Ranges: {ranges}",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Range", style="cyan")
    table.add_column("Task", style="cyan")
    table.add_column("Async Time", style="green")
    table.add_column("Sync Time", style="red")
    table.add_column("Speedup", style="yellow")

    for r in ranges:
        console.print(f"Range: {r}", style="bold", new_line_start=True)
        units = range(r)
        # real HTTP requests
        h, h_time = asyncio.run(run_api_calls(units, api_call))
        h1, h1_time = run_api_calls_linear(units, api_call_linear)

        table.add_row(
            f"{r}",
            "HTTP Requests",
            f"{h_time:,} ns",
            f"{h1_time:,} ns",
            f"{h1_time/h_time:.2f}x",
        )

        if include_sleep_comparison:
            # sleep
            s, s_time = asyncio.run(run_api_calls(units, fake_api_call))
            s1, s1_time = run_api_calls_linear(units, fake_api_call_linear)
            table.add_row(
                f"{r}",
                "Sleep",
                f"{s_time:,} ns",
                f"{s1_time:,} ns",
                f"{s1_time/s_time:.2f}x",
            )

    console.print(table)


if __name__ == "__main__":
    compare_speedups(False)
