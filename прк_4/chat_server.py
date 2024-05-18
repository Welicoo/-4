import asyncio

class ChatServer:
    def __init__(self):
        self.rooms = {}  # словарь для хранения комнат и клиентов в них

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")

        # Запрос имени пользователя и комнаты
        writer.write(b"Enter your username: ")
        await writer.drain()
        username = await reader.readuntil(b'\n')
        username = username.decode().strip()

        writer.write(b"Enter the room you want to join: ")
        await writer.drain()
        room_name = await reader.readuntil(b'\n')
        room_name = room_name.decode().strip()

        if room_name not in self.rooms:
            self.rooms[room_name] = []

        self.rooms[room_name].append((username, writer))

        # Отправляем сообщение об успешном присоединении к чату
        welcome_message = f"Welcome to the '{room_name}' room, {username}!\n"
        writer.write(welcome_message.encode())
        await writer.drain()

        try:
            while True:
                data = await reader.readuntil(b'\n')
                message = data.decode().strip()
                if message == "/quit":
                    break

                full_message = f"{username}: {message}\n"
                print(f"Received message from {addr}: {full_message.strip()}")

                # Отправка сообщения всем в комнате
                for client_username, client_writer in self.rooms[room_name]:
                    if client_writer is not writer:
                        client_writer.write(full_message.encode())
                        await client_writer.drain()
        except asyncio.IncompleteReadError:
            pass
        finally:
            print(f"Client disconnected: {addr}")
            self.rooms[room_name].remove((username, writer))
            writer.close()
            await writer.wait_closed()

    async def run_server(self):
        server = await asyncio.start_server(self.handle_client, '127.0.0.1', 8888)
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    chat_server = ChatServer()
    asyncio.run(chat_server.run_server())
