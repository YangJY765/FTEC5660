import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

mcp = FastMCP("LocalPrices")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.general_tools import get_config_value

def _workspace_data_path(filename: str, symbol: Optional[str] = None) -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    
    if filename == "merged.jsonl" and symbol:
        filename = f"daily_prices_{symbol}.json"

    if symbol and (symbol.endswith(".SH") or symbol.endswith(".SZ")):
        return base_dir / "data" / "A_stock" / filename
    elif symbol and symbol.endswith("-USDT"):
        crypto_filename = "crypto_merged.jsonl" if filename == "merged.jsonl" else filename
        return base_dir / "data" / "crypto" / crypto_filename
    else:
        return base_dir / "data" / filename

def _validate_date_daily(date_str: str) -> None:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("date must be in YYYY-MM-DD format") from exc

@mcp.tool()
def get_price_local(symbol: str, date: str) -> Dict[str, Any]:
    """Read OHLCV data for specified stock and date."""
    return get_price_local_daily(symbol, date)

def get_price_local_daily(symbol: str, date: str) -> Dict[str, Any]:
    filename = "merged.jsonl" 
    
    data_path = _workspace_data_path(filename, symbol)
    if not data_path.exists():
        return {"error": f"Data file not found: {data_path}", "symbol": symbol, "date": date}

    with data_path.open("r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON file.", "symbol": symbol, "date": date}
            
        meta = doc.get("Meta Data", {})
        if meta.get("2. Symbol") != symbol:
            return {"error": "Symbol mismatch in file.", "symbol": symbol, "date": date}
            
        series = doc.get("Time Series (60min)", doc.get("Time Series (Daily)", {}))
        
        matching_keys = [k for k in series.keys() if k.startswith(date)]
        
        if not matching_keys:
            sample_dates = sorted(series.keys(), reverse=True)[:5]
            return {
                "error": f"Data not found for date {date}. Sample available dates: {sample_dates}",
                "symbol": symbol,
                "date": date,
            }
            
        latest_key = sorted(matching_keys)[-1]
        day = series.get(latest_key)
            
        return {
            "symbol": symbol,
            "date": date,
            "ohlcv": {
                "open": day.get("1. open"),
                "high": day.get("2. high"),
                "low": day.get("3. low"), 
                "close": day.get("4. close"),
                "volume": day.get("5. volume"),
            },
        }

if __name__ == "__main__":
    port = int(os.getenv("GETPRICE_HTTP_PORT", "8003"))
    mcp.run(transport="streamable-http", port=port)