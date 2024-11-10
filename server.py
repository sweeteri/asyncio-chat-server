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
            self.rooms[room_name] = {'clients': [], 'queue': asyncio.Queue()}
            asyncio.create_task(self.distribute_messages(room_name))

        self.rooms[room_name]['clients'].append(writer)
        logging.info(f"{addr} joined room {room_name}")

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode().strip()
                logging.info(f"Received message from {addr} in {room_name}: {message}")

                await self.rooms[room_name]['queue'].put((addr, message))
        except asyncio.CancelledError:
            pass
        finally:
            logging.info(f"Disconnecting {addr}")
            self.rooms[room_name]['clients'].remove(writer)
            writer.close()
            await writer.wait_closed()

    async def distribute_messages(self, room_name):
        """Асинхронно рассылает сообщения всем клиентам в комнате, кроме отправителя"""
        while True:
            addr, message = await self.rooms[room_name]['queue'].get()
            logging.info(f"Distributing message from {addr} to room {room_name}: {message}")

            for client in self.rooms[room_name]['clients']:
                try:
                    if client.get_extra_info('peername') != addr:
                        client.write(f"{addr}: {message}\n".encode())
                        await client.drain()
                        logging.info(f"Message sent to client {client.get_extra_info('peername')}: {message}")
                except Exception as e:
                    logging.error(f"Error sending message to client: {e}")

    async def start_server(self, host='127.0.0.1', port=8888):
        server = await asyncio.start_server(self.handle_client, host, port)
        logging.info(f"Server started on {host}:{port}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    chat_server = ChatServer()
    asyncio.run(chat_server.start_server())
