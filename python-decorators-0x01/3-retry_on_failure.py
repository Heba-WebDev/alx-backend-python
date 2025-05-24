import time
import sqlite3
import functools

#### paste your with_db_decorator here

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('user_db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(conn, *args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(conn, *args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"[Retry {attempt}] Error: {e}")
                    if attempt == retries:
                        print("Max retries reached.")
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)