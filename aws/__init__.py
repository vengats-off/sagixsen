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
            max_size=max_conn,
            open=False
        )
        self.connection_pool.open(wait=True, timeout=10)
        logger.info("RDS Connection pool created successfully")
        logger.info(f"Database: {Config.AWS_RDS_DATABASE}")
        logger.info(f"Host: {Config.AWS_RDS_HOST}")
    except Exception as e:
        logger.error(f"Failed to connect to RDS: {str(e)}")
        raise