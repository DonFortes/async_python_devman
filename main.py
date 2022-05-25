import time
import curses


class EventLoopCommand:
    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):
    def __init__(self, seconds):
        self.seconds = seconds


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await Sleep(2)

        canvas.addstr(row, column, symbol)
        await Sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await Sleep(0.5)

        canvas.addstr(row, column, symbol)
        await Sleep(0.3)


def draw(canvas):
    canvas.refresh()
    canvas.border()
    coroutines = [blink(canvas, 5, i) for i in range(5, 26, 5)]

    time_to_wait: int or float = 0.5  # default value, but it will change further
    while True:
        for coroutine in coroutines.copy():
            try:
                wait = coroutine.send(None)
                time_to_wait = wait.seconds
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
                print('That is all')
                time.sleep(2)
        time.sleep(time_to_wait)

        if len(coroutines) == 0:
            print('Len == 0')
            time.sleep(2)
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(0)
    curses.wrapper(draw)

    # while True:
    #     canvas.addstr(row, column, '*', curses.A_DIM)
    #     time.sleep(2)
    #     canvas.refresh()
    #     canvas.addstr(row, column, '*')
    #     time.sleep(0.3)
    #     canvas.refresh()
    #     canvas.addstr(row, column, '*', curses.A_BOLD)
    #     time.sleep(0.5)
    #     canvas.refresh()
    #     canvas.addstr(row, column, '*')
    #     time.sleep(0.3)
    #     canvas.refresh()
