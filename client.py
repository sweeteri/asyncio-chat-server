import asyncio


async def handle_messages(reader):
    """Функция для получения сообщений от сервера"""
    while True:
        try:
            data = await reader.readline()
            if data:
                message = data.decode().strip()
                print(f"Received message from server: {message}")
            else:
                print("Server closed the connection.")
                break
        except asyncio.CancelledError:
            print("Message handling task was cancelled.")
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


async def send_messages(writer):
    """Функция для отправки сообщений на сервер"""
    while True:
        try:
            message = await asyncio.to_thread(input, "Enter your message (type 'exit' to quit): ")

            if message.lower() == 'exit':
                print("Exiting chat.")
                break

            # Если сообщение начинается с /private, отправляем личное сообщение
            if message.startswith('/private'):
                writer.write((message + '\n').encode())
                await writer.drain()
            else:
                writer.write((message + '\n').encode())
                await writer.drain()

        except Exception as e:
            print(f"Error sending message: {e}")
            break


async def main():
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        addr = writer.get_extra_info('peername')
        print(f"Connected to server as {addr}")

        # Ожидаем запроса на имя
        data = await reader.read(100)
        print(data.decode().strip())

        username = input("Enter your username: ")
        writer.write((username + '\n').encode())
        await writer.drain()

        data = await reader.read(100)
        print(data.decode().strip())

        room_name = input("Enter room name: ")
        writer.write((room_name + '\n').encode())
        await writer.drain()

        receive_task = asyncio.create_task(handle_messages(reader))
        send_task = asyncio.create_task(send_messages(writer))

        await send_task
        receive_task.cancel()
        writer.close()
        await writer.wait_closed()

    except ConnectionRefusedError:
        print("Connection refused. Please check if the server is running.")
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
