"""
Tushare Pro data source for Chinese A-share market.
Provides stock price data, technical indicators, fundamentals,
financial statements, and news for A-share stocks.
"""

from __future__ import annotations

import os
import logging
from typing import Annotated
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

_pro = None


def _get_pro():
    """Lazy-initialize Tushare Pro API client."""
    global _pro
    if _pro is None:
        import tushare as ts
        token = os.environ.get("TUSHARE_TOKEN", "")
        if not token:
            raise ValueError(
                "TUSHARE_TOKEN is not set. "
                "Get your token from https://tushare.pro and set it in .env"
            )
        ts.set_token(token)
        _pro = ts.pro_api()
    return _pro


def _is_ashare(symbol: str) -> bool:
    """Check if symbol is an A-share ticker (e.g. 600519.SS, 000001.SZ, 600519.SH)."""
    s = symbol.upper()
    # yfinance style: 600519.SS / 000001.SZ
    if s.endswith(".SS") or s.endswith(".SZ"):
        return True
    # tushare style: 600519.SH / 000001.SZ
    if s.endswith(".SH") or s.endswith(".SZ"):
        return True
    # bare 6-digit code
    if s.isdigit() and len(s) == 6:
        return True
    return False


def _to_tushare_code(symbol: str) -> str:
    """Convert various A-share symbol formats to Tushare ts_code format.

    Examples:
        600519.SS  -> 600519.SH
        000001.SZ  -> 000001.SZ
        600519     -> 600519.SH  (6-digit starting with 6/9 = Shanghai)
        000001     -> 000001.SZ  (6-digit starting with 0/3 = Shenzhen)
        688001     -> 688001.SH  (STAR Market, Shanghai)
    """
    s = symbol.upper().strip()

    # Already tushare format
    if s.endswith(".SH") or s.endswith(".SZ"):
        return s

    # yfinance .SS -> .SH
    if s.endswith(".SS"):
        return s[:-3] + ".SH"

    # bare 6-digit
    code = s.replace(".SZ", "").replace(".SS", "").replace(".SH", "")
    if len(code) == 6 and code.isdigit():
        if code.startswith(("6", "9", "5", "688")):
            return code + ".SH"
        else:
            return code + ".SZ"

    return s


def _fmt_date(date_str: str) -> str:
    """Convert yyyy-mm-dd to yyyymmdd for Tushare API."""
    return date_str.replace("-", "")


# ─────────────────────────────────────────────────────────────
# 1. OHLCV price data
# ─────────────────────────────────────────────────────────────

def get_stock_data(
    symbol: Annotated[str, "A-share ticker, e.g. 600519.SS or 000001.SZ"],
    start_date: Annotated[str, "Start date yyyy-mm-dd"],
    end_date: Annotated[str, "End date yyyy-mm-dd"],
) -> str:
    """Fetch daily OHLCV data for an A-share stock via Tushare Pro."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    df = pro.daily(
        ts_code=ts_code,
        start_date=_fmt_date(start_date),
        end_date=_fmt_date(end_date),
        fields="trade_date,open,high,low,close,vol,amount,pct_chg,change"
    )

    if df is None or df.empty:
        return f"No price data found for {symbol} ({ts_code}) between {start_date} and {end_date}."

    df = df.sort_values("trade_date")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.rename(columns={
        "trade_date": "Date", "open": "Open", "high": "High",
        "low": "Low", "close": "Close", "vol": "Volume",
        "amount": "Amount(万元)", "pct_chg": "Pct_Change(%)", "change": "Change"
    })
    df = df.set_index("Date")

    header = (
        f"# A-share daily price data for {ts_code} ({symbol})\n"
        f"# Period: {start_date} to {end_date}\n"
        f"# Total trading days: {len(df)}\n"
        f"# Source: Tushare Pro\n\n"
    )
    return header + df.to_csv()


# ─────────────────────────────────────────────────────────────
# 2. Technical indicators (via daily + stockstats)
# ─────────────────────────────────────────────────────────────

def get_indicators(
    symbol: Annotated[str, "A-share ticker"],
    indicator: Annotated[str, "Technical indicator name, e.g. macd, rsi, boll"],
    curr_date: Annotated[str, "Current trading date yyyy-mm-dd"],
    look_back_days: Annotated[int, "Number of calendar days to look back"],
) -> str:
    """Compute technical indicators for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    # Fetch enough history for indicator calculation
    start = (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=look_back_days + 60)).strftime("%Y-%m-%d")

    df = pro.daily(
        ts_code=ts_code,
        start_date=_fmt_date(start),
        end_date=_fmt_date(curr_date),
        fields="trade_date,open,high,low,close,vol"
    )

    if df is None or df.empty:
        return f"No data available for {symbol} to compute {indicator}."

    df = df.sort_values("trade_date").reset_index(drop=True)
    df = df.rename(columns={"vol": "volume"})

    try:
        from stockstats import StockDataFrame
        stock = StockDataFrame.retype(df.copy())
        ind_lower = indicator.lower().replace(" ", "_")
        values = stock[ind_lower]
        result_df = df[["trade_date"]].copy()
        result_df[indicator] = values.values
        result_df = result_df.tail(look_back_days)
    except Exception as e:
        return f"Could not compute indicator '{indicator}' for {symbol}: {e}"

    header = (
        f"# Technical indicator: {indicator} for {ts_code}\n"
        f"# Look-back: {look_back_days} days up to {curr_date}\n"
        f"# Source: Tushare Pro\n\n"
    )
    return header + result_df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────
# 3. Fundamentals (TTM metrics)
# ─────────────────────────────────────────────────────────────

def get_fundamentals(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Reference date yyyy-mm-dd"],
) -> str:
    """Fetch key fundamental metrics (PE, PB, ROE, EPS, etc.) for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    # Daily basic metrics (PE, PB, PS, market cap, etc.)
    end = _fmt_date(curr_date)
    start = _fmt_date(
        (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
    )

    df = pro.daily_basic(
        ts_code=ts_code,
        start_date=start,
        end_date=end,
        fields="trade_date,pe,pe_ttm,pb,ps,ps_ttm,total_mv,circ_mv,turnover_rate,volume_ratio,dv_ratio,dv_ttm"
    )

    if df is None or df.empty:
        return f"No fundamental data found for {symbol} ({ts_code})."

    df = df.sort_values("trade_date", ascending=False).head(1)

    header = (
        f"# Fundamental metrics for {ts_code} ({symbol}) as of {curr_date}\n"
        f"# Source: Tushare Pro\n\n"
        f"Metric definitions:\n"
        f"  pe_ttm: Price-to-Earnings (TTM)\n"
        f"  pb: Price-to-Book ratio\n"
        f"  ps_ttm: Price-to-Sales (TTM)\n"
        f"  total_mv: Total market cap (万元)\n"
        f"  circ_mv: Circulating market cap (万元)\n"
        f"  turnover_rate: Daily turnover rate (%)\n"
        f"  dv_ttm: Dividend yield TTM (%)\n\n"
    )
    return header + df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────
# 4. Balance sheet
# ─────────────────────────────────────────────────────────────

def get_balance_sheet(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Reference date yyyy-mm-dd"],
) -> str:
    """Fetch the latest balance sheet for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    # Get last 4 quarters of balance sheet
    end = _fmt_date(curr_date)
    start = _fmt_date(
        (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    )

    df = pro.balancesheet(
        ts_code=ts_code,
        start_date=start,
        end_date=end,
        fields="end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,money_cap,accounts_receiv,inventories,lt_borr,st_borr"
    )

    if df is None or df.empty:
        return f"No balance sheet data found for {symbol} ({ts_code})."

    df = df.sort_values("end_date", ascending=False).head(4)

    header = (
        f"# Balance sheet for {ts_code} ({symbol}) (latest 4 periods up to {curr_date})\n"
        f"# Source: Tushare Pro\n\n"
    )
    return header + df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────
# 5. Cash flow statement
# ─────────────────────────────────────────────────────────────

def get_cashflow(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Reference date yyyy-mm-dd"],
) -> str:
    """Fetch cash flow statements for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    end = _fmt_date(curr_date)
    start = _fmt_date(
        (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    )

    df = pro.cashflow(
        ts_code=ts_code,
        start_date=start,
        end_date=end,
        fields="end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act,n_incr_cash_cash_equ"
    )

    if df is None or df.empty:
        return f"No cash flow data found for {symbol} ({ts_code})."

    df = df.sort_values("end_date", ascending=False).head(4)

    header = (
        f"# Cash flow statement for {ts_code} ({symbol}) (latest 4 periods up to {curr_date})\n"
        f"# Source: Tushare Pro\n\n"
    )
    return header + df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────
# 6. Income statement
# ─────────────────────────────────────────────────────────────

def get_income_statement(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Reference date yyyy-mm-dd"],
) -> str:
    """Fetch income statements for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    end = _fmt_date(curr_date)
    start = _fmt_date(
        (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    )

    df = pro.income(
        ts_code=ts_code,
        start_date=start,
        end_date=end,
        fields="end_date,total_revenue,revenue,total_cogs,operate_profit,n_income,n_income_attr_p,basic_eps,diluted_eps,ebit,ebitda"
    )

    if df is None or df.empty:
        return f"No income statement data found for {symbol} ({ts_code})."

    df = df.sort_values("end_date", ascending=False).head(4)

    header = (
        f"# Income statement for {ts_code} ({symbol}) (latest 4 periods up to {curr_date})\n"
        f"# Source: Tushare Pro\n\n"
    )
    return header + df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────
# 7. News (via Tushare news API)
# ─────────────────────────────────────────────────────────────

def get_news(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Current date yyyy-mm-dd"],
    look_back_days: Annotated[int, "Days to look back for news"] = 7,
) -> str:
    """Fetch recent news for an A-share stock from Tushare."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    start = (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=look_back_days)).strftime("%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(curr_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Tushare news API (requires sufficient points)
        df = pro.news(
            src="sina",
            start_date=start,
            end_date=end,
            fields="datetime,title,content,channels"
        )

        if df is None or df.empty:
            return f"No news found for {symbol} in the past {look_back_days} days."

        # Filter for relevant news (ticker name or code mentions)
        # Get company name
        basic = pro.stock_basic(ts_code=ts_code, fields="ts_code,name")
        company_name = basic["name"].iloc[0] if not basic.empty else ts_code.split(".")[0]

        code = ts_code.split(".")[0]
        mask = (
            df["title"].str.contains(company_name, na=False) |
            df["title"].str.contains(code, na=False) |
            df["content"].str.contains(company_name, na=False)
        )
        filtered = df[mask] if mask.any() else df.head(10)

        result = filtered[["datetime", "title"]].head(20)

        header = (
            f"# Recent news for {ts_code} ({company_name}) — last {look_back_days} days\n"
            f"# Source: Tushare/Sina Finance\n\n"
        )
        return header + result.to_csv(index=False)

    except Exception as e:
        return f"News fetch failed for {symbol}: {e}. This may require higher Tushare point level."


def get_global_news(
    curr_date: Annotated[str, "Current date yyyy-mm-dd"],
    look_back_days: Annotated[int, "Days to look back"] = 3,
) -> str:
    """Fetch recent macro/market news relevant to A-share market."""
    pro = _get_pro()

    start = (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=look_back_days)).strftime("%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(curr_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pro.news(
            src="sina",
            start_date=start,
            end_date=end,
            fields="datetime,title,channels"
        )

        if df is None or df.empty:
            return f"No macro news found for the past {look_back_days} days."

        # Focus on market-level news
        keywords = ["A股", "上证", "深证", "沪深", "央行", "利率", "GDP", "CPI", "政策", "美联储", "外资", "北向"]
        mask = df["title"].apply(lambda t: any(k in str(t) for k in keywords))
        macro = df[mask] if mask.any() else df.head(15)

        result = macro[["datetime", "title"]].head(20)

        header = (
            f"# A-share macro/market news — last {look_back_days} days up to {curr_date}\n"
            f"# Source: Tushare/Sina Finance\n\n"
        )
        return header + result.to_csv(index=False)

    except Exception as e:
        return f"Global news fetch failed: {e}"


# ─────────────────────────────────────────────────────────────
# 8. Insider / major shareholder transactions
# ─────────────────────────────────────────────────────────────

def get_insider_transactions(
    symbol: Annotated[str, "A-share ticker"],
    curr_date: Annotated[str, "Reference date yyyy-mm-dd"],
) -> str:
    """Fetch major shareholder change disclosures for an A-share stock."""
    pro = _get_pro()
    ts_code = _to_tushare_code(symbol)

    end = _fmt_date(curr_date)
    start = _fmt_date(
        (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=180)).strftime("%Y-%m-%d")
    )

    try:
        df = pro.stk_holdertrade(
            ts_code=ts_code,
            start_date=start,
            end_date=end,
            fields="ann_date,holder_name,hold_amount,vol,price,in_de,change_reason"
        )

        if df is None or df.empty:
            return f"No insider/holder transactions found for {symbol} ({ts_code}) in past 6 months."

        df = df.sort_values("ann_date", ascending=False).head(20)

        header = (
            f"# Major shareholder transactions for {ts_code} ({symbol})\n"
            f"# Past 6 months up to {curr_date}\n"
            f"# Source: Tushare Pro\n\n"
        )
        return header + df.to_csv(index=False)

    except Exception as e:
        return f"Insider transaction fetch failed for {symbol}: {e}"
