# This is a sample Python script.
# import streamlit as st
#
# st.write("Hello world")

import yfinance as yf

# Fetch SMCI data
smci = yf.Ticker("SMCI")
info = smci.info

# Get growth rates
revenue_growth = info.get('revenueGrowth', None)  # Quarterly revenue growth (YoY)
earnings_growth = info.get('earningsGrowth', None)  # Quarterly earnings growth (YoY)

print(f"SMCI Revenue Growth (YoY): {revenue_growth * 100:.2f}%")
print(f"SMCI Earnings Growth (YoY): {earnings_growth * 100:.2f}%")

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
