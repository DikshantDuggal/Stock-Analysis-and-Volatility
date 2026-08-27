import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Stock Volatility & Sector Analysis", layout="wide")
sns.set_theme(style="whitegrid")

TICKERS = [
    "TCS.NS", "INFY.NS", "WIPRO.NS",
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
    "TATAMOTORS.NS", "MARUTI.NS", "M&M.NS",
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS",
    "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS",
    "RELIANCE.NS", "ONGC.NS", "NTPC.NS",
]

SECTOR_MAP = {
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "Auto": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS"],
}
TICKER_TO_SECTOR = {t: s for s, ts in SECTOR_MAP.items() for t in ts}


# ---------------- Steps 1-4: same functions as Visualization.py ----------------

def load_stock(ticker, folder="stock_data"):
    filename = ticker.replace("&", "AND").replace(".", "_") + ".csv"
    path = os.path.join(folder, filename)
    return pd.read_csv(path, index_col="Date", parse_dates=True)


def clean_stock(df):
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.ffill()
    df = df.dropna()
    return df


def add_returns(df):
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    df["LogReturn"] = np.log(df["Close"] / df["Close"].shift(1))
    return df.dropna()


def add_indicators(df):
    df = df.copy()
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI_14"] = (100 - (100 / (1 + rs))).fillna(100)

    df["Volatility_21d"] = df["LogReturn"].rolling(window=21).std() * np.sqrt(252)
    return df


@st.cache_data
def get_final_stock(ticker):
    return add_indicators(add_returns(clean_stock(load_stock(ticker))))


@st.cache_data
def get_master_table():
    frames = []
    for t in TICKERS:
        d = get_final_stock(t).copy()
        d["Ticker"] = t
        d["Sector"] = TICKER_TO_SECTOR[t]
        frames.append(d)
    master = pd.concat(frames).reset_index().rename(columns={"index": "Date"})
    return master.sort_values(["Sector", "Ticker", "Date"]).reset_index(drop=True)


# ---------------- Sidebar ----------------
st.sidebar.title("Stock Explorer")
sector = st.sidebar.selectbox("Sector", list(SECTOR_MAP.keys()))
ticker = st.sidebar.selectbox("Stock", SECTOR_MAP[sector])

st.title("Stock Volatility & Sector Analysis")
st.caption("Thesis project dashboard -- pandas, numpy, matplotlib, seaborn (no ML)")

clean = get_final_stock(ticker)
master = get_master_table()

# ---------------- Metrics ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sector", sector)
col2.metric("Latest Close", f"Rs {clean['Close'].iloc[-1]:,.2f}")
col3.metric("Latest RSI(14)", f"{clean['RSI_14'].iloc[-1]:.1f}")
col4.metric("21d Volatility", f"{clean['Volatility_21d'].iloc[-1]:.1%}")

# ---------------- Statistical summary: mean, median, std, quartiles ----------------
st.subheader(f"{ticker} -- Statistical Summary")
st.dataframe(clean[["Close", "Return", "RSI_14", "Volatility_21d"]].describe().round(4), width="stretch")
st.caption("count / mean / std / min / 25% / 50% (median) / 75% / max -- for price, daily return, RSI, and volatility")

# ---------------- Price + SMA/EMA ----------------
st.subheader(f"{ticker} -- Price with SMA/EMA")
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(clean.index, clean["Close"], label="Close", linewidth=1.1)
ax.plot(clean.index, clean["SMA_20"], label="SMA 20", linewidth=1)
ax.plot(clean.index, clean["SMA_50"], label="SMA 50", linewidth=1)
ax.plot(clean.index, clean["EMA_20"], label="EMA 20", linewidth=1, linestyle="--")
ax.legend(fontsize=8)
st.pyplot(fig)
plt.close(fig)

# ---------------- RSI ----------------
st.subheader(f"{ticker} -- RSI(14)")
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.plot(clean.index, clean["RSI_14"], color="#6a3d9a", linewidth=1.1)
ax.axhline(70, color="crimson", linestyle="--", linewidth=1, label="Overbought")
ax.axhline(30, color="seagreen", linestyle="--", linewidth=1, label="Oversold")
ax.fill_between(clean.index, 70, 100, color="crimson", alpha=0.05)
ax.fill_between(clean.index, 0, 30, color="seagreen", alpha=0.05)
ax.legend(fontsize=8, loc="upper left")
st.pyplot(fig)
plt.close(fig)

st.divider()

# ---------------- Sector-level views ----------------
st.subheader("Sector Volatility Comparison")
c1, c2 = st.columns(2)

with c1:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.boxplot(data=master, x="Sector", y="Volatility_21d", hue="Sector",
                palette="coolwarm", ax=ax, legend=False)
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Volatility Distribution by Sector")
    st.pyplot(fig)
    plt.close(fig)

with c2:
    avg_vol = master.groupby("Sector")["Volatility_21d"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.barplot(x=avg_vol.values, y=avg_vol.index, hue=avg_vol.index,
                palette="rocket", orient="h", ax=ax, legend=False)
    ax.set_title("Mean Volatility, Ranked")
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Distribution of Daily Returns by Sector")
fig, ax = plt.subplots(figsize=(11, 4))
sns.histplot(data=master, x="Return", hue="Sector", element="step", stat="density",
             common_norm=False, palette="tab10", ax=ax, alpha=0.35)
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xlim(-0.08, 0.08)
st.pyplot(fig)
plt.close(fig)

st.subheader("Correlation of Daily Sector Returns")
sector_returns = master.pivot_table(index="Date", columns="Sector", values="Return", aggfunc="mean")
corr = sector_returns.corr()
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, square=True,
            linewidths=0.5, ax=ax, cbar_kws={"label": "Correlation"})
st.pyplot(fig)
plt.close(fig)

st.divider()

# ---------------- Data table + download ----------------
st.subheader(f"{ticker} -- Full Data Table")
st.dataframe(clean, width="stretch")

csv_bytes = clean.to_csv().encode("utf-8")
st.download_button(
    label=f"Download {ticker} full data as CSV",
    data=csv_bytes,
    file_name=f"{ticker.replace('.', '_')}_full.csv",
    mime="text/csv",
)

st.subheader("Summary Statistics by Sector")
rows = []
for s in SECTOR_MAP:
    r = sector_returns[s].dropna()
    ann_ret = r.mean() * 252
    ann_vol = r.std() * np.sqrt(252)
    mask = master["Sector"] == s
    rows.append({
        "Sector": s,
        "Annualised Return": round(float(ann_ret), 4),
        "Annualised Volatility": round(float(ann_vol), 4),
        "Return/Volatility": round(float(ann_ret / ann_vol), 3),
        "% Days Overbought": round(float((master.loc[mask, "RSI_14"] > 70).mean() * 100), 1),
        "% Days Oversold": round(float((master.loc[mask, "RSI_14"] < 30).mean() * 100), 1),
    })
summary_df = pd.DataFrame(rows).set_index("Sector").sort_values("Annualised Volatility", ascending=False)
st.dataframe(summary_df, width="stretch")