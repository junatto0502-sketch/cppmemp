import psycopg

DSN = "host=localhost port=5432 dbname=cppmemo user=postgres password=Atto2052"


def init_db():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memos (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
        conn.commit()


def fetch_all():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, url
                FROM memos
                ORDER BY id DESC
            """)
            return cur.fetchall()


def insert_memo(title, url):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO memos(title, url) VALUES(%s,%s)",
                (title, url),
            )
        conn.commit()


def delete_memo(memo_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM memos WHERE id = %s", (memo_id,))
        conn.commit()


def fetch_one(memo_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, url FROM memos WHERE id = %s",
                (memo_id,),
            )
            return cur.fetchone()