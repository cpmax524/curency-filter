import requests
import functools

# In a real implementation, you would move the base URLs to a config file.
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# --- CoinGecko Helpers ---

@functools.lru_cache(maxsize=1)
def _get_coingecko_coin_list(api_key: str) -> list:
    """
    Fetches the list of all coins from CoinGecko and caches it.
    An API key is not strictly required for this endpoint, but passing it is good practice.
    """
    print("DEBUG: Fetching CoinGecko coin list...")
    url = f"{COINGECKO_API_URL}/coins/list"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def _get_coingecko_id(symbol: str, api_key: str) -> str | None:
    """
    Finds the CoinGecko coin ID for a given symbol.
    """
    coin_list = _get_coingecko_coin_list(api_key)
    for coin in coin_list:
        if coin["symbol"].lower() == symbol.lower():
            return coin["id"]
    # Fallback for coins where symbol doesn't match (e.g., 'bitcoin' id is 'bitcoin')
    for coin in coin_list:
        if coin["id"].lower() == symbol.lower():
            return coin["id"]
    return None

def get_derivatives_data(symbol: str, api_key: str = None) -> dict:
    """
    Fetches derivatives data for a given symbol from CoinGecko.
    """
    if not api_key:
        print("DEBUG: No CoinGecko API key provided. Skipping derivatives data.")
        return {}

    coin_id = _get_coingecko_id(symbol, api_key)
    if not coin_id:
        print(f"DEBUG: Could not find CoinGecko ID for {symbol}. Skipping derivatives data.")
        return {}

    print(f"DEBUG: Using REAL derivatives API for {symbol} (CoinGecko ID: {coin_id})")

    url = f"{COINGECKO_API_URL}/coins/{coin_id}/tickers"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key
    }
    params = {
        "include_exchange_logo": "false",
        "depth": "false",
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # The 'tickers' key holds the list of tickers.
    tickers = data.get("tickers", [])

    # Find the first perpetual contract and get its funding rate.
    for ticker in tickers:
        if ticker.get("is_perpetual") and "funding_rate" in ticker:
            return {
                "funding_rate": ticker["funding_rate"],
            }

    print(f"DEBUG: No perpetual contract with funding rate found for {symbol} on CoinGecko.")
    return {}

# A mapping from symbol to ERC20 contract address.
# In a real application, this might come from a database or a more robust service.
TOKEN_CONTRACT_ADDRESSES = {
    "chainlink": "0x514910771af9ca656af840dff83e8264ecf986ca"
}

def get_top_eth_tokens(api_key: str) -> list[str]:
    """
    Fetches the top 30 tokens on the Ethereum chain by market cap from CoinGecko.
    """
    print("DEBUG: Fetching top 30 ETH tokens...")
    url = f"{COINGECKO_API_URL}/coins/markets"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key,
    }
    params = {
        "vs_currency": "usd",
        "category": "ethereum-ecosystem",
        "order": "market_cap_desc",
        "per_page": 30,
        "page": 1,
        "sparkline": "false",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # We only need the symbols for the next steps.
    return [item["symbol"] for item in data]

def get_onchain_data(symbol: str, api_key: str = None) -> dict:
    """
    Fetches on-chain data for a given symbol from Etherscan.
    """
    if not api_key:
        print("DEBUG: No Etherscan API key provided. Skipping on-chain data.")
        return {}

    print(f"DEBUG: Using REAL on-chain API for {symbol}")

    params = {
        "apikey": api_key,
    }

    if symbol == "ethereum":
        params.update({
            "module": "stats",
            "action": "ethsupply",
        })
        response = requests.get(ETHERSCAN_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
    elif symbol in TOKEN_CONTRACT_ADDRESSES:
        params.update({
            "module": "stats",
            "action": "tokensupply",
            "contractaddress": TOKEN_CONTRACT_ADDRESSES[symbol],
        })
        response = requests.get(ETHERSCAN_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
    else:
        print(f"DEBUG: On-chain data not supported for {symbol} in this implementation.")
        return {}

    if data.get("status") == "1":
        # The Etherscan API returns the total supply in the smallest unit (wei for ETH).
        # We will return it as is. The analysis rules would need to be adjusted for this.
        # For this task, we are only concerned with fetching the data.
        return {"total_supply": data.get("result")}
    else:
        print(f"DEBUG: Etherscan API error for {symbol}: {data.get('message')}")
        return {}


def fetch_all_data(symbol: str, api_keys: dict) -> tuple[dict, list[str]]:
    """
    Fetches all available data (derivatives, on-chain) for a symbol.

    Returns a tuple containing:
    - A dictionary with all the combined data.
    - A list of errors encountered during fetching.
    """
    combined_data = {"symbol": symbol}
    errors = []

    try:
        derivatives_data = get_derivatives_data(symbol, api_keys.get("coingecko"))
        combined_data.update(derivatives_data)
    except Exception as e:
        error_message = f"Could not retrieve derivatives data for {symbol.upper()}: {e}"
        print(error_message)
        errors.append(error_message)

    try:
        # Note: On-chain data is blockchain-specific. This assumes Ethereum ecosystem.
        onchain_data = get_onchain_data(symbol, api_keys.get("etherscan"))
        combined_data.update(onchain_data)
    except Exception as e:
        error_message = f"Could not retrieve on-chain data for {symbol.upper()}: {e}"
        print(error_message)
        errors.append(error_message)

    return combined_data, errors
