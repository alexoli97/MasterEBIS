"""Tools de Yahoo Finance — funciones Python decoradas con @function_tool.

CONCEPTO CLAVE: @function_tool
  El decorador convierte una función Python normal en una tool que el agente
  puede invocar. El SDK lee el docstring y los type hints para generar
  automáticamente el JSON Schema que el modelo necesita para llamarla.

  Regla: el docstring describe QUE hace la tool (el modelo lo lee para decidir
  cuándo usarla). Los Args: describen cada parámetro.

Tools disponibles para los agentes:
  - get_quote()             → precio, sector, capitalización
  - get_fundamentals()      → PER, ROE, deuda, márgenes
  - get_price_history()     → retorno y volatilidad histórica
  - get_technical_signals() → RSI, MACD, medias móviles
  - get_news_headlines()    → titulares recientes de Yahoo Finance

fetch_prices() es una función interna (sin decorador) usada por el optimizador.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from agents import function_tool


@function_tool
def get_quote(ticker: str) -> str:
    """Return latest price, market cap, sector, currency for a ticker.

    Args:
        ticker: Yahoo Finance ticker (e.g. AAPL, SAN.MC, ASML.AS).
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        out = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency"),
            "market_cap": info.get("marketCap"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
        }
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def get_fundamentals(ticker: str) -> str:
    """Return key fundamental ratios: P/E, P/B, ROE, debt/equity, margins, dividend yield."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        out = {
            "ticker": ticker,
            "pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb": info.get("priceToBook"),
            "peg": info.get("pegRatio"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "debt_to_equity": info.get("debtToEquity"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "dividend_yield": info.get("dividendYield"),
            "fcf": info.get("freeCashflow"),
            "beta": info.get("beta"),
        }
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def get_price_history(ticker: str, period: str = "1y") -> str:
    """Return summary stats from price history.

    Args:
        ticker: Yahoo ticker.
        period: 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max.
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist.empty:
            return json.dumps({"error": "no data", "ticker": ticker})
        closes = hist["Close"]
        ret = (closes.iloc[-1] / closes.iloc[0] - 1) * 100
        vol = closes.pct_change().std() * (252**0.5) * 100
        out = {
            "ticker": ticker,
            "period": period,
            "start": str(hist.index[0].date()),
            "end": str(hist.index[-1].date()),
            "start_price": float(closes.iloc[0]),
            "end_price": float(closes.iloc[-1]),
            "total_return_pct": float(ret),
            "annualized_vol_pct": float(vol),
            "max_price": float(closes.max()),
            "min_price": float(closes.min()),
            "sma_50": float(closes.tail(50).mean()) if len(closes) >= 50 else None,
            "sma_200": float(closes.tail(200).mean()) if len(closes) >= 200 else None,
        }
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def get_technical_signals(ticker: str) -> str:
    """RSI(14), MACD, distance to 52w high/low, trend vs SMA50/SMA200."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        if hist.empty or len(hist) < 50:
            return json.dumps({"error": "insufficient data", "ticker": ticker})
        c = hist["Close"]

        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        ema12 = c.ewm(span=12).mean()
        ema26 = c.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()

        last = float(c.iloc[-1])
        sma50 = float(c.tail(50).mean())
        sma200 = float(c.tail(200).mean()) if len(c) >= 200 else None
        high52 = float(c.max())
        low52 = float(c.min())

        out = {
            "ticker": ticker,
            "price": last,
            "rsi_14": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            "macd": float(macd.iloc[-1]),
            "macd_signal": float(signal.iloc[-1]),
            "macd_bullish_cross": bool(macd.iloc[-1] > signal.iloc[-1]),
            "sma_50": sma50,
            "sma_200": sma200,
            "above_sma_50": last > sma50,
            "above_sma_200": (last > sma200) if sma200 else None,
            "pct_from_52w_high": (last / high52 - 1) * 100,
            "pct_from_52w_low": (last / low52 - 1) * 100,
        }
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def get_news_headlines(ticker: str, limit: int = 5) -> str:
    """Recent news headlines for a ticker from Yahoo."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        out = []
        for n in news[:limit]:
            content = n.get("content", n)
            out.append({
                "title": content.get("title"),
                "publisher": (content.get("provider") or {}).get("displayName")
                if isinstance(content.get("provider"), dict) else content.get("publisher"),
                "published": content.get("pubDate") or content.get("providerPublishTime"),
            })
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


def fetch_prices(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    """Bulk price fetch for optimizer. Not exposed as agent tool."""
    df = yf.download(tickers, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(name=tickers[0])
    return df.dropna(axis=1, how="all").ffill().dropna()
