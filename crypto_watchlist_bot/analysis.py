def analyze_asset(data: dict, rules_config: dict) -> tuple[int, list[str]]:
    """
    Analyzes the collected data for an asset based on a set of rules.

    Args:
        data: A dictionary containing the combined data for the asset.
        rules_config: A dictionary loaded from the rules.json file.

    Returns:
        A tuple containing:
        - The total calculated score for the asset.
        - A list of strings describing the reasons for the score.
    """
    total_score = 0
    reasons = []

    for rule in rules_config.get("rules", []):
        metric = rule.get("metric")
        condition = rule.get("condition")
        value = rule.get("value")
        score = rule.get("score")
        reason = rule.get("reason")

        if metric not in data:
            # If the required data point is missing (e.g., API failed), skip this rule.
            continue

        asset_value = data[metric]

        # Check if the condition for this rule is met
        if condition == "less_than" and asset_value < value:
            total_score += score
            reasons.append(reason)
        elif condition == "greater_than" and asset_value > value:
            total_score += score
            reasons.append(reason)
        # Add other conditions (e.g., 'equals') here if needed in the future

    return total_score, reasons


def categorize_score(score: int, rules_config: dict) -> str:
    """
    Categorizes a score into a priority level based on thresholds.

    Args:
        score: The score of the asset.
        rules_config: A dictionary loaded from the rules.json file.

    Returns:
        A string label for the priority category (e.g., "🔥 High Priority").
    """
    categories = rules_config.get("categories", {})

    # Check from highest priority to lowest
    if score >= categories.get("high", {}).get("min_score", 999):
        return categories.get("high", {}).get("label", "High Priority")
    elif score >= categories.get("medium", {}).get("min_score", 999):
        return categories.get("medium", {}).get("label", "Medium Priority")
    else:
        return categories.get("low", {}).get("label", "Low Priority")
