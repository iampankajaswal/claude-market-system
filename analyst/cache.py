"""
SQLite cache for Claude API responses.
Caches by (ticker, quarter_end) to avoid redundant API calls.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class AnalysisCache:
    """SQLite-backed cache for Claude analysis results."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'cache.db'

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    ticker TEXT NOT NULL,
                    quarter_end TEXT NOT NULL,
                    analysis_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (ticker, quarter_end)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker
                ON analysis_cache(ticker)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON analysis_cache(created_at)
            """)
            conn.commit()

    def get(self, ticker: str, quarter_end: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis.

        Args:
            ticker: Stock ticker symbol
            quarter_end: Quarter end date (YYYY-MM-DD)

        Returns:
            dict: Cached analysis or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT analysis_json FROM analysis_cache WHERE ticker = ? AND quarter_end = ?",
                (ticker, quarter_end)
            )
            row = cursor.fetchone()

            if row:
                return json.loads(row[0])

        return None

    def set(self, ticker: str, quarter_end: str, analysis: Dict[str, Any]):
        """
        Store analysis in cache.

        Args:
            ticker: Stock ticker symbol
            quarter_end: Quarter end date (YYYY-MM-DD)
            analysis: Analysis result to cache
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analysis_cache (ticker, quarter_end, analysis_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (ticker, quarter_end, json.dumps(analysis), datetime.now().isoformat())
            )
            conn.commit()

    def clear_ticker(self, ticker: str):
        """Clear all cached analyses for a ticker."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM analysis_cache WHERE ticker = ?", (ticker,))
            conn.commit()

    def clear_all(self):
        """Clear entire cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM analysis_cache")
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM analysis_cache")
            count = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(DISTINCT ticker) FROM analysis_cache")
            unique_tickers = cursor.fetchone()[0]

        return {
            'total_entries': count,
            'unique_tickers': unique_tickers
        }
