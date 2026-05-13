self.connection_pool = ConnectionPool(conninfo=f"host=... dbname=... user=... password=...", min_size=min_conn, max_size=max_conn)
