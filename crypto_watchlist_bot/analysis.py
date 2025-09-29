import time
from . import data_collector

def filter_tokens(tokens: list) -> list:
    """
    Analyzes tokens and returns a list of those that meet the criteria.
    """
    filtered_tokens = []
    if not tokens:
        print("No tokens to analyze.")
        return []

    print(f"--- Analyzing {len(tokens)} Tokens (GT Score > 70 and Good Distribution) ---")

    for i, token in enumerate(tokens):
        # Add a delay to respect API rate limits (e.g., 30 requests/minute).
        # 60 seconds / 30 requests = 2 seconds per request.
        time.sleep(2.1)

        token_address_html = token.get('token_address_with_chart', '')
        asset = token.get('asset', 'N/A')
        print(f"Processing token {i + 1}/{len(tokens)}: {asset}...")

        token_address = data_collector.extract_token_address(token_address_html)

        if not token_address:
            print(f"  -> Could not extract address for {asset}. Skipping.")
            continue

        token_info = data_collector.get_token_info(token_address)

        if token_info and 'data' in token_info:
            attributes = token_info['data'].get('attributes', {})
            gt_score = attributes.get('gt_score')

            if gt_score is not None and gt_score > 70:
                holders_info = attributes.get('holders', {})
                distribution = holders_info.get('distribution_percentage', {})
                top_10_percentage_str = distribution.get('top_10', '100.0')

                try:
                    top_10_percentage = float(top_10_percentage_str)
                    # We consider a good distribution if top 10 holders have less than 50%
                    if top_10_percentage < 50.0:
                        filtered_tokens.append({
                            "name": attributes.get('name', 'N/A'),
                            "symbol": attributes.get('symbol', 'N/A'),
                            "address": token_address,
                            "market_cap": token.get('market_cap', 'N/A'),
                            "gt_score": gt_score,
                            "top_10_holders": top_10_percentage
                        })
                except (ValueError, TypeError):
                    # Skip if the percentage conversion fails
                    continue

    # Sort by GT Score descending before returning
    filtered_tokens.sort(key=lambda x: x['gt_score'], reverse=True)

    print(f"--- Analysis Complete: Found {len(filtered_tokens)} promising tokens. ---")
    return filtered_tokens