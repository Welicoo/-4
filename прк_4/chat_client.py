import asyncio

async def handle_input(writer):
    while True:
        message = await asyncio.get_event_loop().run_in_executor(None, input)
        writer.write((message + '\n').encode())
        await writer.drain()
        if message == "/quit":
            break

async def read_messages(reader):
    try:
        while True:
            data = await reader.readuntil(b'\n')
            print(data.decode().strip())
    except asyncio.IncompleteReadError:
        pass

async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    username = input("Enter your username: ")
    room_name = input("Enter the room you want to join: ")

    writer.write((username + '\n').encode())
    await writer.drain()
    writer.write((room_name + '\n').encode())
    await writer.drain()

    await asyncio.gather(
        handle_input(writer),
        read_messages(reader),
    )

    writer.close()
    await writer.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
