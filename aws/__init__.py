def __init__(self, min_conn: int = 1, max_conn: int = 10):
    try:
        conninfo = (
            f"host={Config.AWS_RDS_HOST} "
            f"port={Config.AWS_RDS_PORT} "
            f"dbname={Config.AWS_RDS_DATABASE} "
            f"user={Config.AWS_RDS_USER} "
            f"password={Config.AWS_RDS_PASSWORD}"
        )
        self.connection_pool = ConnectionPool(
            conninfo=conninfo,
            min_size=min_conn,
            max_size=max_conn
        )
        logger.info("RDS Connection pool created successfully")
    except Exception as e:
        logger.error(f"Failed to connect to RDS: {str(e)}")
        raise