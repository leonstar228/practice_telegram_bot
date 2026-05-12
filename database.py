import aiosqlite
from datetime import datetime
from config import settings


def get_connection():
    return aiosqlite.connect(settings.db_path)


async def init_db():
    async with get_connection() as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            username TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            telegram_file_id TEXT NOT NULL,
            file_name TEXT,
            mime_type TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        await db.commit()


async def register_user(
    telegram_id: int,
    full_name: str,
    username: str | None,
    role: str = "user"
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with get_connection() as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (
            telegram_id,
            full_name,
            username,
            role,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            telegram_id,
            full_name,
            username,
            role,
            now
        ))

        await db.commit()


async def get_user_by_telegram_id(telegram_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT *
        FROM users
        WHERE telegram_id = ?
        """, (telegram_id,))

        return await cursor.fetchone()


async def create_request(
    user_id: int,
    title: str,
    description: str
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with get_connection() as db:
        await db.execute("""
        INSERT INTO requests (
            user_id,
            title,
            description,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            title,
            description,
            "new",
            now,
            now
        ))

        await db.commit()


async def get_user_requests(user_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT *
        FROM requests
        WHERE user_id = ?
        ORDER BY id DESC
        """, (user_id,))

        return await cursor.fetchall()


async def get_all_requests():
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT
            requests.*,
            users.full_name,
            users.username
        FROM requests
        JOIN users
            ON users.id = requests.user_id
        WHERE requests.status IN ('new', 'processing')
        ORDER BY requests.id DESC
        """)

        return await cursor.fetchall()


async def get_request_by_id(request_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT *
        FROM requests
        WHERE id = ?
        """, (request_id,))

        return await cursor.fetchone()


async def update_request(
    request_id: int,
    description: str
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with get_connection() as db:
        await db.execute("""
        UPDATE requests
        SET
            description = ?,
            updated_at = ?
        WHERE id = ?
        """, (
            description,
            now,
            request_id
        ))

        await db.commit()


async def update_request_status(
    request_id: int,
    status: str
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with get_connection() as db:
        await db.execute("""
        UPDATE requests
        SET
            status = ?,
            updated_at = ?
        WHERE id = ?
        """, (
            status,
            now,
            request_id
        ))

        await db.commit()


async def delete_request(
    request_id: int,
    user_id: int
):
    async with get_connection() as db:
        await db.execute("""
        DELETE FROM requests
        WHERE id = ? AND user_id = ?
        """, (
            request_id,
            user_id
        ))

        await db.commit()


async def get_user_files(user_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT *
        FROM files
        WHERE user_id = ?
        ORDER BY id DESC
        """, (user_id,))

        return await cursor.fetchall()


async def save_file(
    user_id: int,
    telegram_file_id: str,
    file_name: str | None,
    mime_type: str | None
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with get_connection() as db:
        await db.execute("""
        INSERT INTO files (
            user_id,
            telegram_file_id,
            file_name,
            mime_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            telegram_file_id,
            file_name,
            mime_type,
            now
        ))

        await db.commit()

async def get_file_by_id(file_id: int):
    async with get_connection() as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
        SELECT *
        FROM files
        WHERE id = ?
        """, (file_id,))

        return await cursor.fetchone()


async def update_file_name(file_id: int, user_id: int, file_name: str):
    async with get_connection() as db:
        await db.execute("""
        UPDATE files
        SET file_name = ?
        WHERE id = ? AND user_id = ?
        """, (file_name, file_id, user_id))

        await db.commit()


async def delete_file(file_id: int, user_id: int):
    async with get_connection() as db:
        await db.execute("""
        DELETE FROM files
        WHERE id = ? AND user_id = ?
        """, (file_id, user_id))

        await db.commit()