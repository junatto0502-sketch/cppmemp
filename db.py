import psycopg

DSN = "host=localhost port=5432 dbname=cppmemo user=postgres password=Atto2052"

def init_db():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL DEFAULT '',
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
        conn.commit()

def list_pages():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, updated_at
                FROM pages
                ORDER BY updated_at DESC, id DESC
            """)
            return cur.fetchall()

def create_page(title: str) -> int:
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pages(title, body) VALUES(%s, '') RETURNING id",
                (title,),
            )
            page_id = cur.fetchone()[0]
        conn.commit()
        return page_id

def get_page(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, body FROM pages WHERE id=%s", (page_id,))
            return cur.fetchone()

def update_page(page_id: int, title: str, body: str):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pages
                SET title=%s, body=%s, updated_at=now()
                WHERE id=%s
            """, (title, body, page_id))
        conn.commit()

def delete_page(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pages WHERE id=%s", (page_id,))
        conn.commit()