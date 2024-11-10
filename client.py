import asyncio


async def handle_messages(reader):
    while True:
        data = await reader.readline()
        if not data:
            print("Server closed the connection.")
            break
        print(f"New message: {data.decode().strip()}")


async def send_messages(writer):
    while True:
        message = input("Enter your message (type 'exit' to quit): ")
        if message.lower() == 'exit':
            print("Exiting chat.")
            break
        writer.write((message + '\n').encode())
        await writer.drain()


async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

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


if __name__ == '__main__':
    asyncio.run(main())
