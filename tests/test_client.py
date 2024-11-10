import unittest
import asyncio


class TestChatClient(unittest.TestCase):

    async def test_client_connection_success(self):
        """Проверяем, что клиент может успешно подключиться к серверу"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_user\n'.encode())
        await writer.drain()

        data = await reader.read(100)
        self.assertIn("Enter room name:", data.decode())

        writer.close()
        await writer.wait_closed()

    async def test_send_message_to_room(self):
        """Проверяем, что клиент может отправить сообщение в комнату"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_user\n'.encode())
        await writer.drain()

        writer.write('room1\n'.encode())
        await writer.drain()

        writer.write('Hello, room1!\n'.encode())
        await writer.drain()

        data = await reader.read(100)
        self.assertIn('Hello, room1!', data.decode())

        writer.close()
        await writer.wait_closed()

    async def test_receive_message_from_room(self):
        """Проверяем, что клиент получает сообщения из комнаты"""
        reader1, writer1 = await asyncio.open_connection('127.0.0.1', 8888)
        writer1.write('test_user1\n'.encode())
        await writer1.drain()

        reader2, writer2 = await asyncio.open_connection('127.0.0.1', 8888)
        writer2.write('test_user2\n'.encode())
        await writer2.drain()

        writer1.write('room1\n'.encode())
        writer2.write('room1\n'.encode())
        await writer1.drain()
        await writer2.drain()

        writer1.write('Hello from user1\n'.encode())
        await writer1.drain()

        data1 = await reader1.read(100)
        data2 = await reader2.read(100)

        self.assertIn('Hello from user1', data1.decode())
        self.assertIn('Hello from user1', data2.decode())

        writer1.close()
        writer2.close()
        await writer1.wait_closed()
        await writer2.wait_closed()

    async def test_invalid_username(self):
        """Тестируем обработку ошибки при попытке подключиться с уже занятым именем"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_user\n'.encode())
        await writer.drain()

        writer.write('room1\n'.encode())
        await writer.drain()

        writer.write('Hello, room1!\n'.encode())
        await writer.drain()

        data = await reader.read(100)
        self.assertIn('Hello, room1!', data.decode())

        writer.close()
        await writer.wait_closed()
