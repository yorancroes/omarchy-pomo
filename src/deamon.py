import os
import asyncio
from timer import Timer


class PomodoroDeamon:
    def __init__(self):
        self.path = "/tmp/pomodoro.sock"
        self.json_path = "/tmp/pomodoro_state.json"
        self.timer = Timer()
        if os.path.exists(self.path):
            os.remove(self.path)

    async def setup(self):
        self.server = await asyncio.start_unix_server(self.handle_connection, path=self.path)

    async def serve(self):
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(self.server.serve_forever())
            task2 = tg.create_task(self.tick_loop())

    async def tick_loop(self):
        while True:
            self.timer.advance_phase()
            self.write_json()
            await asyncio.sleep(1)

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        message = (await reader.readline()).decode().strip()

        functions = {
            "START": self.start_timer,
            "PAUSE": self.pause_timer,
            "SKIP": self.skip_timer,
            "PING": self.send_message,
        }

        func = functions.get(message)

        if func is None:
            return await self.send_error(writer)
        return await func(writer)

    async def start_timer(self, writer):
        if self.timer.start():
            await self.send_message(writer)
        else:
            await self.send_error(writer, msg="ERROR: timer unable to start")

    async def pause_timer(self, writer):
        if self.timer.pause():
            await self.send_message(writer)
        else:
            await self.send_error(writer, msg="ERROR: timer unable to pause")

    async def skip_timer(self, writer):
        self.timer.skip_phase()
        await self.send_message(writer)

    async def send_message(self, writer: asyncio.StreamWriter, msg="ok"):
        writer.write(msg.encode())
        await writer.drain()
        await self.close_writer(writer)

    async def send_error(self, writer, msg="ERROR: Unkown operator"):
        writer.write(msg.encode())
        await writer.drain()
        await self.close_writer(writer)

    async def close_writer(self, writer: asyncio.StreamWriter):
        writer.close()
        await writer.wait_closed()

    def write_json(self):
        txt = self.timer.dump()

        # tmp_path so client can't read half written json
        tmp_path = self.json_path + ".tmp"
        with open(tmp_path, "w") as f:
            f.write(txt)
        os.replace(tmp_path, self.json_path)


async def main():
    deamon = PomodoroDeamon()
    await deamon.setup()
    await deamon.serve()


if __name__ == "__main__":
    asyncio.run(main())
