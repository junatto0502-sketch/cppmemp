import psycopg

DSN = "host=localhost port=5432 dbname=cppmemo user=postgres password=Atto2052"

def init_db():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memos (
                    id BIGSERIAL PRIMARY KEY,
                    page_id BIGINT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
        conn.commit()

# --- pages ---
def list_pages():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.title, p.updated_at, COALESCE(c.cnt, 0) AS memo_count
                FROM pages p
                LEFT JOIN (
                    SELECT page_id, COUNT(*) cnt FROM memos GROUP BY page_id
                ) c ON c.page_id = p.id
                ORDER BY p.updated_at DESC, p.id DESC
            """)
            return cur.fetchall()

def create_page(title: str) -> int:
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO pages(title) VALUES(%s) RETURNING id", (title,))
            pid = cur.fetchone()[0]
        conn.commit()
        return pid

def get_page(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM pages WHERE id=%s", (page_id,))
            return cur.fetchone()

def update_page_title(page_id: int, title: str):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pages SET title=%s, updated_at=now() WHERE id=%s
            """, (title, page_id))
        conn.commit()

def touch_page(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE pages SET updated_at=now() WHERE id=%s", (page_id,))
        conn.commit()

def delete_page(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pages WHERE id=%s", (page_id,))
        conn.commit()

# --- memos ---
def list_memos(page_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, body
                FROM memos
                WHERE page_id=%s
                ORDER BY id DESC
            """, (page_id,))
            return cur.fetchall()

def create_memo(page_id: int, title: str, body: str):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memos(page_id, title, body) VALUES(%s,%s,%s)
            """, (page_id, title, body))
        conn.commit()
    touch_page(page_id)

def update_memo(memo_id: int, title: str, body: str):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE memos SET title=%s, body=%s WHERE id=%s", (title, body, memo_id))
        conn.commit()

def delete_memo(memo_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT page_id FROM memos WHERE id=%s", (memo_id,))
            row = cur.fetchone()
            if not row:
                return
            page_id = row[0]
            cur.execute("DELETE FROM memos WHERE id=%s", (memo_id,))
        conn.commit()
    touch_page(page_id)

def get_memo(memo_id: int):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, page_id, title, body FROM memos WHERE id=%s", (memo_id,))
            return cur.fetchone()