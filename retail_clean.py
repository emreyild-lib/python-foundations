"""
Data cleaning and revenue summary for Online Retail dataset.

Steps:
1) Remove exact duplicate rows.
2) Handle missing values:
   - Drop rows with missing CustomerID.
   - Drop rows with missing Quantity or UnitPrice.
   - Fill missing Description with "Unknown".
   - Fill missing Country with "Unknown".
3) Remove invalid rows where Quantity <= 0 or UnitPrice <= 0.
4) Add TotalPrice = Quantity * UnitPrice.
5) Produce a country-level revenue summary (sum of TotalPrice).

Usage:
    python retail_clean.py /path/to/large_online_retail.csv --outdir /path/to/outdir
"""

import argparse
import pandas as pd
from pathlib import Path

def process(input_csv: str, outdir: str):
    inp = Path(input_csv)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp)

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Handle missing values
    df = df.dropna(subset=["CustomerID"])
    df = df.dropna(subset=["Quantity", "UnitPrice"])
    if "Description" in df.columns:
        df["Description"] = df["Description"].fillna("Unknown")
    if "Country" in df.columns:
        df["Country"] = df["Country"].fillna("Unknown")

    # Remove invalid Quantity/UnitPrice
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    # Create TotalPrice
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    # Summarize by country
    country_revenue = (
        df.groupby("Country", dropna=False, as_index=False)["TotalPrice"]
          .sum()
          .rename(columns={"TotalPrice": "TotalRevenue"})
          .sort_values("TotalRevenue", ascending=False)
          .reset_index(drop=True)
    )

    # Save outputs
    clean_path = out / "retail_cleaned.csv"
    summary_path = out / "country_revenue.csv"
    df.to_csv(clean_path, index=False)
    country_revenue.to_csv(summary_path, index=False)
    return clean_path, summary_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", help="Path to large_online_retail.csv")
    ap.add_argument("--outdir", default=".", help="Directory to write outputs")
    args = ap.parse_args()
    clean_path, summary_path = process(args.input_csv, args.outdir)
    print(f"Cleaned dataset saved to: {clean_path}")
    print(f"Country revenue summary saved to: {summary_path}")

if __name__ == "__main__":
    main()
