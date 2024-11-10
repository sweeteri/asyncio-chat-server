import asyncio
import logging

logging.basicConfig(level=logging.INFO)


class ChatServer:
    def __init__(self):
        self.rooms = {}

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"Connected: {addr}")


        writer.write("Enter room name: ".encode())
        await writer.drain()
        room_name = (await reader.readline()).decode().strip()


        if room_name not in self.rooms:
            self.rooms[room_name] = []
        self.rooms[room_name].append(writer)
        logging.info(f"{addr} joined room {room_name}")

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode().strip()
                logging.info(f"Message from {addr} in {room_name}: {message}")


                for client in self.rooms[room_name]:
                    if client != writer:
                        client.write(f"{addr}: {message}\n".encode())
                        await client.drain()
        except asyncio.CancelledError:
            pass
        finally:
            logging.info(f"Disconnecting {addr}")
            self.rooms[room_name].remove(writer)
            writer.close()
            await writer.wait_closed()

    async def start_server(self, host='127.0.0.1', port=8888):
        server = await asyncio.start_server(self.handle_client, host, port)
        logging.info(f"Server started on {host}:{port}")
        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    chat_server = ChatServer()
    asyncio.run(chat_server.start_server())
