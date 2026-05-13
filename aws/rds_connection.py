"""
RDS Connection - Disabled for Python 3.13 compatibility
Data storage skipped, report generation works without database
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class RDSConnection:
    """
    Dummy RDS connection - does nothing but prevents crashes.
    psycopg2 doesn't support Python 3.13, so we skip DB storage.
    Report generation still works fully without it.
    """
    
    def __init__(self, min_conn=1, max_conn=10):
        logger.info("RDS storage disabled (Python 3.13 compatibility)")
        self.connection_pool = None

    def create_tables(self):
        logger.info("Skipping table creation (RDS disabled)")
        return True

    def insert_stock_price(self, symbol, date, open_price, high, low, close, volume):
        return True

    def bulk_insert_stock_prices(self, data):
        logger.info(f"Skipping bulk insert of {len(data)} records (RDS disabled)")
        return True

    def get_stock_prices(self, symbol, start_date=None, end_date=None):
        return []

    def insert_fundamental(self, symbol, data):
        return True

    def execute_query(self, query, params=None, fetch=True):
        if fetch:
            return []
        return None

    def close_all_connections(self):
        pass