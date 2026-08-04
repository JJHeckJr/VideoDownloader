def create_video_request(conn, url, title, thumbnail):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO video_requests (url, title, thumbnail) VALUES (%s, %s, %s) RETURNING id",
        (url, title, thumbnail)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return new_id

def get_video_request(conn, request_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, url, title, thumbnail FROM video_requests WHERE id = %s",
        (request_id,) 
    )
    row = cur.fetchone()
    cur.close()
    return row

def update_video_request(conn, request_id, url, title, thumbnail):
    cur = conn.cursor()
    cur.execute(
        "UPDATE video_requests SET url = %s, title = %s, thumbnail = %s WHERE id = %s",
        (url, title, thumbnail, request_id)
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    return updated

def delete_video_request(conn, request_id):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM video_requests WHERE id = %s",
        (request_id,)
    )
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    return deleted