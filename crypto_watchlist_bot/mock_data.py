import random

def get_mock_derivatives_data(symbol: str) -> dict:
    """
    Returns mock derivatives data for a given symbol.
    Mimics a response from an API like CoinGecko.
    """
    print(f"DEBUG: Using MOCK derivatives data for {symbol}")
    if "ethereum" in symbol.lower():
        # High priority signals
        return {
            "funding_rate": -0.0006,  # Triggers "Negative Funding" rule
            "open_interest_change_24h": 0.25,  # Triggers "High OI Change" rule
        }
    elif "bitcoin" in symbol.lower():
        # Medium priority signals - ADJUSTED
        return {
            "funding_rate": 0.0001,
            "open_interest_change_24h": 0.21, # ADJUSTED to be > 0.20 to trigger a rule
        }
    else:
        # Low priority signals
        return {
            "funding_rate": 0.0001,
            "open_interest_change_24h": random.uniform(-0.05, 0.05),
        }

def get_mock_onchain_data(symbol: str) -> dict:
    """
    Returns mock on-chain data for a given symbol.
    Mimics a response from an API like Etherscan.
    """
    print(f"DEBUG: Using MOCK on-chain data for {symbol}")
    if "ethereum" in symbol.lower():
        # High priority signals
        return {
            "exchange_net_flow": -2000,  # Triggers "Large Net Outflow" rule
            "onchain_tx_count_change_24h": 0.60, # Triggers rule
            "active_addresses_change_24h": 0.10,
        }
    elif "bitcoin" in symbol.lower():
         # Medium priority signals
        return {
            "exchange_net_flow": 500,
            "onchain_tx_count_change_24h": 0.10,
            "active_addresses_change_24h": 0.35, # Triggers "Active Address Spike"
        }
    else:
        # Low priority signals
        return {
            "exchange_net_flow": random.uniform(-100, 100),
            "onchain_tx_count_change_24h": random.uniform(-0.1, 0.1),
            "active_addresses_change_24h": random.uniform(-0.1, 0.1),
        }
