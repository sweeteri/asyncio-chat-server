import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class ChatServer:
    def __init__(self):
        self.rooms = {}

    async def handle_client(self, reader, writer):
        try:
            addr = writer.get_extra_info('peername')
            logging.info(f"New connection from {addr}")

            writer.write("Enter room name: ".encode())
            await writer.drain()
            room_name = (await reader.read(100)).decode().strip()

            if room_name not in self.rooms:
                self.rooms[room_name] = {'clients': []}
            self.rooms[room_name]['clients'].append(writer)

            logging.info(f"{addr} joined room {room_name}")

            while True:
                try:
                    data = await reader.readline()
                    if not data:
                        logging.info(f"{addr} disconnected.")
                        break

                    message = data.decode().strip()
                    logging.info(f"Received message from {addr} in {room_name}: {message}")

                    for client in self.rooms[room_name]['clients']:
                        if client != writer:
                            try:
                                client.write(f"{addr}: {message}\n".encode())
                                await client.drain()
                            except Exception as e:
                                logging.error(f"Error sending message to {client.get_extra_info('peername')}: {e}")
                except asyncio.CancelledError:
                    logging.info(f"Task for {addr} was cancelled")
                    break
                except Exception as e:
                    logging.error(f"Error reading data from {addr}: {e}")
                    break

        except Exception as e:
            logging.error(f"Error handling client {addr}: {e}")
        finally:
            for room in self.rooms.values():
                if writer in room['clients']:
                    room['clients'].remove(writer)

            writer.close()
            await writer.wait_closed()
            logging.info(f"Closed connection with {addr}")

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, '127.0.0.1', 8888)
        addr = server.sockets[0].getsockname()
        logging.info(f"Server started on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = ChatServer()
    asyncio.run(server.start_server())
