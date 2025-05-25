def evaluate_stock():
    # Step 1: Get Fed Conditions from User
    print("\n--- Federal Reserve Policy Input ---")
    fed_rates = input("Are interest rates HIGH or LOW? ").strip().lower()
    fed_balance_sheet = input("Is the Fed's balance sheet INCREASING or DECREASING? ").strip().lower()

    # Step 2: Get Stock Metrics from User
    print("\n--- Company Stock Metrics Input ---")
    revenue_growth = float(input("Revenue Growth (%): "))
    earnings_growth = float(input("Earnings Growth (%): "))
    pe_ratio = float(input("P/E Ratio: "))
    debt_ebitda = float(input("Debt/EBITDA: "))

    # Step 3: Initialize Score and Logic
    score = 0
    recommendation = ""
    allocation = ""

    # Rule 1: Fed Policy Alignment
    if fed_rates == "high" and fed_balance_sheet == "decreasing":
        # Conservative stocks favored
        if pe_ratio <= 15 and debt_ebitda <= 2:
            score += 2
        elif revenue_growth >= 5 and earnings_growth >= 5:
            score += 1

    elif fed_rates == "low" and fed_balance_sheet == "increasing":
        # Aggressive growth stocks favored
        if revenue_growth > 50 and pe_ratio > 25:
            score += 2
        elif revenue_growth >= 20 and earnings_growth >= 10:
            score += 1

    # Rule 2: Earnings Growth Penalty
    if earnings_growth < 0:
        score -= 1  # Penalize negative earnings

    # Rule 3: Debt/EBITDA Risk
    if debt_ebitda > 5:
        score -= 2
    elif debt_ebitda <= 1:
        score += 1

    # Step 4: Generate Recommendation
    if score >= 3:
        recommendation = "Strong Buy"
        allocation = "0-50% of portfolio"
    elif score >= 1:
        recommendation = "Moderate Buy"
        allocation = "0-20% of portfolio"
    else:
        recommendation = "Avoid"
        allocation = "0%"

    # Step 5: Print Results
    print("\n--- Recommendation ---")
    print(f"Fed Conditions: Rates={fed_rates.upper()}, Balance Sheet={fed_balance_sheet.upper()}")
    print(
        f"Stock Metrics: Revenue Growth={revenue_growth}%, Earnings Growth={earnings_growth}%, "
        f"P/E={pe_ratio}, Debt/EBITDA={debt_ebitda}")
    print(f"Verdict: {recommendation} ({allocation})")


# Run the function
evaluate_stock()