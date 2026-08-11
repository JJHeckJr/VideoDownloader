def run_query(conn, sql, params=None, fetch=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    if fetch == "one":
        result = cur.fetchone()
    elif fetch == "all":
        result = cur.fetchall()
    elif fetch == "rowcount":
        result = cur.rowcount
    else:
        result = None
    conn.commit()
    cur.close()
    return result

def create_video_request(conn, url, title, thumbnail):
    row = run_query(
        conn,
        "INSERT INTO video_requests (url, title, thumbnail) VALUES (%s, %s, %s) RETURNING id",
        (url, title, thumbnail),
        fetch="one"
    )
    return row[0]

def get_video_request(conn, request_id):
    id_row = run_query(
        conn, 
        "SELECT id, url, title, thumbnail FROM video_requests WHERE id = %s",
        (request_id,),
        fetch="one"
    )
    return id_row

def get_video_request_by_url(conn, url):
    return run_query(
        conn,
        "SELECT id, url, title, thumbnail FROM video_requests WHERE url = %s",
        (url,),
        fetch="one"
    )

def get_all_video_request(conn):
    return run_query(
        conn,
        "SELECT id, url, title, thumbnail FROM video_requests",
        fetch="all"
    )

def update_video_request(conn, request_id, url, title, thumbnail):
    updated = run_query(
        conn, 
        "UPDATE video_requests SET url = %s, title = %s, thumbnail = %s WHERE id = %s",
        (url, title, thumbnail, request_id),
        fetch="rowcount"
    )
    return updated

def delete_video_request(conn, request_id):
    deleted = run_query(
        conn, 
        "DELETE FROM video_requests WHERE id = %s",
        (request_id,),
        fetch="rowcount"
    )
    return deleted

