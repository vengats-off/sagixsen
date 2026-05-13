"""
Yahoo Finance Data - Replaces Angel One / Fyers
Works from any cloud server with no API key needed.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
from utils.logger import get_logger
from utils.validators import validate_stock_symbol

logger = get_logger(__name__)


class AngelOneAPI:
    """
    Yahoo Finance wrapper named AngelOneAPI for compatibility.
    No API key needed, no rate limiting issues on cloud servers.
    NSE symbols: add .NS suffix (TCS -> TCS.NS)
    """

    def __init__(self):
        self.session_active = False
        logger.info("Yahoo Finance API initialized (no auth needed)")

    def login(self) -> bool:
        self.session_active = True
        logger.info("Yahoo Finance ready")
        return True

    def _to_yf_symbol(self, symbol: str) -> str:
        """Convert NSE symbol to Yahoo Finance format."""
        # Yahoo Finance uses .NS suffix for NSE stocks
        symbol = symbol.upper().strip()

        # Special cases
        special = {
            'M&M': 'M%26M.NS',
            'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
        }
        if symbol in special:
            return special[symbol]

        return f"{symbol}.NS"

    def get_historical_data(self, symbol: str, from_date: str,
                            to_date: str, interval: str = 'ONE_DAY') -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from Yahoo Finance.

        Args:
            symbol: NSE symbol like 'TCS', 'INFY'
            from_date: YYYY-MM-DD
            to_date: YYYY-MM-DD
            interval: ignored, always daily

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume, symbol
        """
        try:
            is_valid, symbol_or_msg = validate_stock_symbol(symbol)
            if not is_valid:
                logger.error(f"Invalid symbol: {symbol_or_msg}")
                return None

            symbol = symbol_or_msg
            yf_symbol = self._to_yf_symbol(symbol)

            logger.info(f"Fetching {yf_symbol} from {from_date} to {to_date}")

            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=from_date, end=to_date, interval='1d')

            if df is None or df.empty:
                logger.error(f"No data returned for {yf_symbol}")
                return None

            # Rename columns to match existing pipeline
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Keep only needed columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['symbol'] = symbol

            # Ensure timestamp is datetime without timezone
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

            # Sort by date
            df = df.sort_values('timestamp').reset_index(drop=True)

            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            return None

    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current price from Yahoo Finance."""
        try:
            yf_symbol = self._to_yf_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.fast_info

            return {
                'symbol': symbol,
                'ltp': float(info.last_price or 0),
                'open': float(info.open or 0),
                'high': float(info.day_high or 0),
                'low': float(info.day_low or 0),
                'close': float(info.previous_close or 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Failed to fetch current price: {str(e)}")
            return None

    def logout(self):
        self.session_active = False
        logger.info("Yahoo Finance session closed")

    def get_profile(self) -> Optional[Dict]:
        return {'name': 'Yahoo Finance User', 'clientcode': 'YF'}