from . import mock_data
import requests

# In a real implementation, you would move the base URLs to a config file.
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

def get_derivatives_data(symbol: str, api_key: str = None) -> dict:
    """
    Fetches derivatives data for a given symbol.
    Uses mock data if no API key is provided.
    """
    if not api_key:
        return mock_data.get_mock_derivatives_data(symbol)

    print(f"DEBUG: Using REAL derivatives API for {symbol}")
    # This is where you would put the real API call logic.
    # For now, we'll return mock data to ensure the flow works.
    # Example for CoinGecko (conceptual):
    # params = {'tickers': 'true', 'market_data': 'false'}
    # response = requests.get(f"{COINGECKO_API_URL}/coins/{symbol}", params=params)
    # response.raise_for_status()
    # data = response.json()
    # ... process and return standardized data
    return mock_data.get_mock_derivatives_data(symbol) # Fallback for now

def get_onchain_data(symbol: str, api_key: str = None) -> dict:
    """
    Fetches on-chain data for a given symbol.
    Uses mock data if no API key is provided.
    """
    if not api_key:
        return mock_data.get_mock_onchain_data(symbol)

    print(f"DEBUG: Using REAL on-chain API for {symbol}")
    # This is where you would put the real API call logic for Etherscan.
    # For now, we'll return mock data.
    return mock_data.get_mock_onchain_data(symbol) # Fallback for now


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
