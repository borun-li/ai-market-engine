import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

# Import clean_data function from data_cleaning
from data_cleaning import clean_data


# --- STEP 1: Import Data & Loading ---
TICKERS  = ['NVDA', 'MU', 'MSFT']
COLORS   = {'NVDA': '#76B900', 'MU': '#0057B8', 'MSFT': '#0078D4'}

# Load and clean all three tickers
close_prices = {}
for ticker in TICKERS:
    raw = pd.read_csv(f'data/{ticker}.csv', index_col=0)
    df = raw.iloc[2:].astype(float)
    df.index = pd.to_datetime(df.index) # convert df's index to DateTimeIndex
    cleaned = clean_data(df)
    close_prices[ticker] = cleaned['Close'] # add the cleaned ticker into the dict

# Combine into one DataFrame — one column per ticker
close = pd.DataFrame(close_prices)


# --- Step 2: Compute the two data series ---

# Daily returns: (today - yesterday) / yesterday
returns = close.pct_change().dropna()

# Panel 1: cumulative return from start date
# Formula: (1 + r1) * (1 + r2) * ... - 1
cum_returns = (1 + returns).cumprod() - 1

# Panel 2: 20-day rolling volatility (std of daily returns)
# First 19 rows will be NaN — matplotlib skips these automatically
rolling_vol = returns.rolling(window=20).std()


# --- Step 3: Create the two-panel figure ---

# 2 rows, 1 column — Panel 1 is 3x taller than Panel 2
# sharex=True: zooming one panel zooms both
gridspec_kw={'height_ratios': [3, 1]}

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(14, 9),
    sharex=True,
    gridspec_kw=gridspec_kw
)

# Horizontal layout is better for:
# comparing two unrelated charts that don't share an axis
# (e.g., a bar chart next to a pie chart).

# Vertical stacking is better for: financial charts where the same time period appears in multiple indicators — which is exactly what you have. TradingView, Bloomberg terminals, and every professional charting tool uses this layout for exactly this reason.


# --- Step 4: Plot Panel 1 — Cumulative Returns ---
for ticker in TICKERS:
    ax1.plot(cum_returns.index, cum_returns[ticker],
            label=ticker, color=COLORS[ticker], linewidth=1.8)

ax1.axhline(y=0, color='grey', linewidth=0.8, linestyle='--')  # zero baseline
ax1.set_ylabel('Cumulative Return', fontsize=11)
ax1.legend(frameon=False)


# --- Step 5: Plot Panel 2 — Rolling Volatility ---
for ticker in TICKERS:
    ax2.plot(rolling_vol.index, rolling_vol[ticker],
            color=COLORS[ticker], linewidth=1.2)

ax2.set_ylabel('20-Day Volatility', fontsize=11)
ax2.set_xlabel('Date', fontsize=11)


# --- Step 6: Remove the Top and Right Border Lines ---
for spine in ['top', 'right']:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)


# --- Step 7: Figure-Level Title ---
# fig.suptitle(): Super Title --> puts the title above the entire figure
fig.suptitle('NVDA / MU / MSFT: Performance & Volatility (2024–2026)',
            fontsize=14, fontweight='bold')


# --- Step 8: Tight Layout ---
plt.tight_layout()


# --- Step 9: Save the Chart ---
fig.savefig('charts/performance_overview.png', dpi=300, bbox_inches='tight')


# --- Step 10: Show the Chart ---
# plt.show()


# --- Founder Challenge: Interactive Line Plots ---
fig_interactive = px.line(
    cum_returns,
    title='NVDA / MU / MSFT: Cumulative Returns (2024–2026)',
    labels={'value': 'Cumulative Return', 'variable': 'Ticker'} # keys: column names, values: desired display labels"
)
fig_interactive.write_html('charts/interactive.html')
print("Interactive chart saved to charts/interactive.html")