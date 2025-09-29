import os
import requests
import re
import time

# --- Configuration ---
DUNE_API_URL = "https://api.dune.com/api/v1/query/5137851/results?limit=1000"
GECKOTERMINAL_API_URL_TEMPLATE = "https://api.geckoterminal.com/api/v2/networks/solana/tokens/{}/info"

# --- Main Functions ---

def get_top_tokens():
    """Fetches the top tokens from the Dune API."""
    print("Fetching top tokens from Dune API...")
    dune_api_key = os.getenv("DUNE_API_KEY")
    if not dune_api_key:
        raise ValueError("DUNE_API_KEY environment variable not set.")

    headers = {"X-Dune-API-Key": dune_api_key}
    try:
        response = requests.get(DUNE_API_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data and data.get('result') and data['result'].get('rows'):
            print(f"Successfully fetched {len(data['result']['rows'])} tokens.")
            return data['result']['rows']
        else:
            print("No token data found in the Dune API response.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Dune API: {e}")
        return []
    except ValueError:
        print("Error decoding JSON from Dune API response.")
        return []

def get_token_info(token_address):
    """Fetches detailed information for a specific token from GeckoTerminal."""
    url = GECKOTERMINAL_API_URL_TEMPLATE.format(token_address)
    try:
        response = requests.get(url)
        if response.status_code == 404:
            # It's common for some new tokens not to be listed yet
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch info for {token_address}: {e}")
        return None
    except ValueError:
        print(f"Error decoding JSON for {token_address}.")
        return None


def extract_token_address(html_string):
    """Extracts the token address from the HTML anchor tag."""
    # A regular expression to find the token address in the href attribute
    match = re.search(r'href="https://axiom.trade/t/([^/"]+)', html_string)
    if match:
        return match.group(1)
    return None