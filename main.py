import asyncio
import time
from functools import partial
from typing import Coroutine
import random
import curses


STARS_COUNT = 200
TIC_TIMEOUT = 0.1


async def wait_for_queue(tics):
    """Function that will be used in case when coroutine needs to skip a step."""
    for _ in range(tics):
        await asyncio.sleep(0)


class SpaceObject:
    """Factory class for space objects."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.border_limits: tuple = self.canvas.getmaxyx()

    async def animate(self, *args, **kwargs) -> None:
        """Method to animate each object."""
        return None

    def create_event_loop(self) -> list[Coroutine]:
        """Method to create event loop of each space object.
        It always returns a list with coroutines."""
        return []


class SkyStar(SpaceObject):
    """Class to make the sky full of stars."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.symbols = "+*.:"

    def make_random_coordinates(self) -> tuple[callable, callable]:
        """Make random star coordinates."""
        x, y = tuple(
            partial(random.randint, 1, limit - 2) for limit in self.border_limits
        )
        return x, y

    async def animate(self, row, column, symbol="*") -> None:
        """Display animation of star."""
        while True:
            self.canvas.addstr(row, column, symbol, curses.A_DIM)
            await wait_for_queue(20 + random.randint(0, 2))

            self.canvas.addstr(row, column, symbol)
            await wait_for_queue(3 + random.randint(0, 2))

            self.canvas.addstr(row, column, symbol, curses.A_BOLD)
            await wait_for_queue(5 + random.randint(0, 2))

            self.canvas.addstr(row, column, symbol)
            await wait_for_queue(3 + random.randint(0, 2))

    def create_event_loop(self) -> list[Coroutine]:
        """Create a star event loop."""
        x, y = self.make_random_coordinates()
        stars_event_loop = [
            self.animate(x(), y(), random.choice(self.symbols))
            for _ in range(STARS_COUNT)
        ]
        return stars_event_loop


class SpaceShot(SpaceObject):
    """Class to make the space shot."""

    def __init__(self, canvas):
        super().__init__(canvas)

    async def animate(self, row, column, rows_speed=-1, columns_speed=0) -> None:
        """Display animation of gun shot, direction and speed can be specified."""
        self.canvas.addstr(round(row), round(column), "*")
        curses.beep()
        await asyncio.sleep(0)

        self.canvas.addstr(round(row), round(column), "O")
        await asyncio.sleep(0)

        self.canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed
        symbol = "-" if columns_speed else "|"
        rows, columns = self.border_limits
        max_row, max_column = rows - 1, columns - 1

        while 0 < row < max_row and 0 < column < max_column:
            self.canvas.addstr(round(row), round(column), symbol)
            await asyncio.sleep(0)
            self.canvas.addstr(round(row), round(column), " ")
            row += rows_speed
            column += columns_speed

    def create_event_loop(self) -> list[Coroutine]:
        """Create a shot event loop."""
        x, y = self.border_limits
        fire_coroutine = self.animate(x - 2, y / 2)
        return [fire_coroutine]


class EventLoop:
    """Class to create common event loop."""

    def __init__(self, canvas, *args):
        self.sky_star = SkyStar(canvas)
        self.space_shot = SpaceShot(canvas)

    def create_generic_event_loop(self) -> list[Coroutine]:
        """Create event loop of all space objects."""
        final_event_loop = []
        for event_loop in self.__dict__.values():
            loop_to_add = event_loop.create_event_loop()
            final_event_loop.extend(loop_to_add)
        return final_event_loop


def main(canvas) -> None:
    """Draw the hole picture."""
    canvas.refresh()
    canvas.border()
    event_loop = EventLoop(canvas).create_generic_event_loop()

    while True:
        time_start = time.perf_counter()
        for coroutine in event_loop.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                event_loop.remove(coroutine)
            else:
                canvas.refresh()

        time_stop = time.perf_counter()
        elapsed_time = time_stop - time_start
        tic_timeout = TIC_TIMEOUT - elapsed_time

        time.sleep(tic_timeout)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(0)
    curses.wrapper(main)
