import unittest
import asyncio
from server import ChatServer


class TestChatServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Запускаем сервер в отдельной задаче перед всеми тестами"""
        cls.server = ChatServer()

    def setUp(self):
        """Перед каждым тестом запускаем сервер в асинхронной задаче"""
        self.loop = asyncio.get_event_loop()
        self.server_task = self.loop.create_task(self.server.start_server())

    def tearDown(self):
        """После каждого теста завершаем сервер"""
        self.server_task.cancel()

    def test_server_start(self):
        """Проверяем, что сервер стартует корректно"""
        self.loop.run_until_complete(asyncio.sleep(1))  # Ожидаем, пока сервер начнет работу
        self.assertFalse(self.server_task.done())

    async def test_client_connection(self):
        """Тестируем подключение клиента"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_username\n'.encode())
        await writer.drain()
        data = await reader.read(100)
        self.assertIn("Enter room name:", data.decode())
        writer.close()
        await writer.wait_closed()

    async def test_room_creation_and_message_broadcast(self):
        """Тестируем создание комнаты и рассылку сообщений"""
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

        self.assertIn("Hello from user1", data1.decode())
        self.assertIn("Hello from user1", data2.decode())

        writer1.close()
        writer2.close()
        await writer1.wait_closed()
        await writer2.wait_closed()

    async def test_client_disconnection(self):
        """Тестируем, что клиент может отключиться без сбоев"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_user_disconnect\n'.encode())
        await writer.drain()

        writer.write('room1\n'.encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()

        self.assertFalse(self.server_task.done())

    async def test_send_message_to_nonexistent_user(self):
        """Тестируем отправку сообщения несуществующему пользователю"""
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write('test_user1\n'.encode())
        await writer.drain()

        writer.write('room1\n'.encode())
        await writer.drain()

        writer.write('/msg 127.0.0.1:12345 Hello\n'.encode())  # Не существующий пользователь
        await writer.drain()

        data = await reader.read(100)
        self.assertIn("No client found with address", data.decode())

        writer.close()
        await writer.wait_closed()
