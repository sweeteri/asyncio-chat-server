import asyncio
import logging

logging.basicConfig(level=logging.INFO)


class ChatServer:
    def __init__(self):
        self.rooms = {}
        self.clients = {}

    async def handle_client(self, reader, writer):
        try:
            addr = writer.get_extra_info('peername')
            client_address = f"{addr[0]}:{addr[1]}"  # Строковое представление IP:порт

            username = None
            while True:
                writer.write("Enter your username: ".encode())
                await writer.drain()
                username = (await reader.read(100)).decode().strip()

                if username in self.clients:
                    writer.write("This username is already taken. Please choose another one.\n".encode())
                    writer.write("Enter your username: ".encode())
                    await writer.drain()
                else:
                    break

            self.clients[username] = writer

            writer.write(f"Hello {username}, enter room name: ".encode())
            await writer.drain()

            room_name = (await reader.read(100)).decode().strip()

            if room_name not in self.rooms:
                self.rooms[room_name] = {'clients': []}
            self.rooms[room_name]['clients'].append(writer)

            logging.info(f"{username} joined room {room_name}")

            while True:
                try:
                    data = await reader.readline()
                    if not data:
                        logging.info(f"{username} disconnected.")
                        break

                    message = data.decode().strip()

                    # Если сообщение начинается с "/private", это личное сообщение
                    if message.startswith('/private'):
                        parts = message.split(' ', 2)
                        if len(parts) < 3:
                            writer.write("Invalid private message format. Use /private <username> <message>\n".encode())
                            await writer.drain()
                            continue

                        recipient_name = parts[1]
                        private_message = parts[2]

                        recipient_writer = self.clients.get(recipient_name)
                        if recipient_writer:
                            recipient_writer.write(f"Private message from {username}: {private_message}\n".encode())
                            await recipient_writer.drain()
                            writer.write(f"Message sent to {recipient_name}\n".encode())
                            await writer.drain()
                        else:
                            writer.write(f"No client found with username {recipient_name}\n".encode())
                            await writer.drain()

                    else:
                        logging.info(f"Received message from {username} in {room_name}: {message}")

                        for client in self.rooms[room_name]['clients']:
                            if client != writer:
                                try:
                                    if client.is_closing():
                                        continue
                                    client.write(f"{username}: {message}\n".encode())
                                    await client.drain()
                                except Exception as e:
                                    logging.error(f"Error sending message to {client.get_extra_info('peername')}: {e}")

                except asyncio.CancelledError:
                    logging.info(f"Task for {username} was cancelled")
                    break
                except Exception as e:
                    logging.error(f"Error reading data from {username}: {e}")
                    break

        except Exception as e:
            logging.error(f"Error handling client {client_address}: {e}")
        finally:
            for room in self.rooms.values():
                if writer in room['clients']:
                    room['clients'].remove(writer)

            del self.clients[username]

            writer.close()
            await writer.wait_closed()
            logging.info(f"Closed connection with {username}")

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
