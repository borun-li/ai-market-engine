"""
analysis.py

Pure functions for computing financial time-series metrics.
Input: cleaned close price DataFrames.
Output: derived metric DataFrames. No side effects.
"""

import pandas as pd
import numpy as np

__all__ = ['compute_returns', 'compute_rolling_vol', 'compute_summary_stats', 'compute_parkinson_vol']


def compute_returns(close: pd.DataFrame) -> pd.DataFrame:
    """Compute daily percentage returns for each ticker.

    Args:
        close: DataFrame with DatetimeIndex, one column per ticker.

    Returns:
        DataFrame of daily returns with the first row dropped (NaN from pct_change).
    """
    return close.pct_change().dropna()


def compute_rolling_vol(returns: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Compute rolling volatility (std of returns) for each ticker.

    Args:
        returns: DataFrame of daily returns (output of compute_returns).
        window:  Rolling window in trading days. Default is 20 (~1 month).

    Returns:
        DataFrame of rolling std values. First (window-1) rows will be NaN.
    """
    return returns.rolling(window=window).std()


def compute_summary_stats(returns: pd.DataFrame) -> pd.DataFrame:
    """Compute per-ticker summary statistics.

    Args:
        returns: DataFrame of daily returns (output of compute_returns).

    Returns:
        DataFrame with one row per ticker and columns:
        mean_daily_return, annualized_vol, max_drawdown, total_return.
    """
    cum = (1 + returns).cumprod()

    stats = pd.DataFrame({
        'mean_daily_return': returns.mean(),
        'annualized_vol':    returns.std() * np.sqrt(252),
        'max_drawdown':      (cum / cum.cummax() - 1).min(),
        'total_return':      cum.iloc[-1] - 1,
    })

    return stats

def compute_parkinson_vol(high: pd.DataFrame, low: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Compute rolling Parkinson volatility using High/Low prices.

    More efficient than Close-to-Close std — captures intraday price range.
    Formula: sqrt( (1 / 4·ln2) · rolling_mean( ln(High/Low)² ) )

    Args:
        high:   DataFrame of daily High prices, one column per ticker.
        low:    DataFrame of daily Low prices, one column per ticker.
        window: Rolling window in trading days. Default is 20.

    Returns:
        DataFrame of rolling Parkinson vol values (same shape as high/low).
    """
    log_hl_sq = np.log(high / low) ** 2
    factor    = 1 / (4 * np.log(2))
    return np.sqrt(factor * log_hl_sq.rolling(window=window).mean())

