import asyncio
import random
import time
import curses
from functools import partial


STARS_COUNT = 200
MIN_OFFSET_TIME = 0.0001
MAX_OFFSET_TIME = 0.01


class Sleep:
    def __init__(self, seconds):
        self.seconds = seconds

    def __await__(self):
        return (yield self)


async def blink(canvas, row, column, symbol="*", offset=0):
    while True:
        if offset == 0:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await Sleep(0.5)
            offset += 1

        else:
            time.sleep(random.uniform(MIN_OFFSET_TIME, MAX_OFFSET_TIME))
            canvas.addstr(row, column, symbol)
            await Sleep(0.3)

            time.sleep(random.uniform(MIN_OFFSET_TIME, MAX_OFFSET_TIME))
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await Sleep(0.5)

            time.sleep(random.uniform(MIN_OFFSET_TIME, MAX_OFFSET_TIME))
            canvas.addstr(row, column, symbol)
            await Sleep(0.3)

            time.sleep(random.uniform(MIN_OFFSET_TIME, MAX_OFFSET_TIME))
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await Sleep(0.5)


def make_coroutines(canvas) -> list:
    """Make a list with coroutines."""

    border_limits: tuple = canvas.getmaxyx()
    x, y = tuple(partial(random.randint, 1, limit - 2) for limit in border_limits)
    symbols = "+*.:"
    coroutines = [
        blink(canvas, x(), y(), random.choice(symbols)) for _ in range(STARS_COUNT)
    ]
    return coroutines


def draw(canvas) -> None:
    """Draw the stars."""

    canvas.refresh()
    canvas.border()
    coroutines = make_coroutines(canvas)
    time_to_wait: int or float = 0.5  # default value, but it will change further

    while True:
        for coroutine in coroutines.copy():
            try:
                wait = coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
                print("That is all")
            else:
                time_to_wait = wait.seconds
                canvas.refresh()

        time.sleep(time_to_wait)

        if len(coroutines) == 0:
            print("Len == 0")
            time.sleep(2)
            break


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(0)
    curses.wrapper(draw)
