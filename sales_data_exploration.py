# pip install pandas pyarrow
import os
import json
import pandas as pd

# --------- 0) CONFIG ---------
CSV_PATH = "data.csv"                # ✅ your main dataset
LOOKUP_PATH = "lookup.csv"           # ✅ optional: for join demo
REQUIRED_COLS = ["date","item","price","quantity","category"]  # ✅ adjust
DATE_COLS = ["date"]                 # ✅ any date columns to parse
ID_COL = "transaction_id"            # ✅ if you have a unique id

# --------- 1) LOAD + “CSV GOOD?” CHECKS ---------
def load_csv_safely(path, parse_dates=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    if os.path.getsize(path) == 0:
        raise ValueError(f"Empty file: {path}")
    df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)
    if df.empty:
        raise ValueError("No rows found after load.")
    return df

df = load_csv_safely(CSV_PATH, parse_dates=DATE_COLS)

# schema/columns check
missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    raise ValueError(f"CSV not good – missing required columns: {missing}")

print("CSV looks good ✅")
print(df.head(3))

# --------- 2) IDENTIFY DATA TYPES (structured / semi-structured) ---------
print("\nDtypes:")
print(df.dtypes)

# Example: parse a semi-structured text/JSON column if present
# e.g., a column 'attributes' containing JSON strings per row
if "attributes" in df.columns:
    def parse_json_safe(x):
        try:
            return json.loads(x) if pd.notna(x) else {}
        except Exception:
            return {}
    attrs = df["attributes"].apply(parse_json_safe).apply(pd.Series)
    # Merge extracted keys (like color, size) back to the table
    for col in attrs.columns:
        df[f"attr_{col}"] = attrs[col]

# --------- 3) BASIC CLEANING ---------
# trim strings
str_cols = df.select_dtypes(include="object").columns
df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())

# standardize categorical text (example: title case for category)
if "category" in df.columns:
    df["category"] = df["category"].str.title()

# remove obvious duplicates
subset_for_dupes = [ID_COL] if ID_COL in df.columns else REQUIRED_COLS
df = df.drop_duplicates(subset=subset_for_dupes)

# handle nulls: example rules
# - drop rows missing critical fields
critical = ["item","price","quantity"]
df = df.dropna(subset=[c for c in critical if c in df.columns])

# - fill numeric nulls with 0 (demo)
num_cols = df.select_dtypes(include="number").columns
df[num_cols] = df[num_cols].fillna(0)

# --------- 4) TRANSFORM (sort, filter, join, derive new cols) ---------
# derive new columns
if set(["price","quantity"]).issubset(df.columns):
    df["total"] = df["price"] * df["quantity"]

# filter example: keep the last 90 days if date available
if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
    recent_cutoff = df["date"].max() - pd.Timedelta(days=90)
    df_recent = df[df["date"] >= recent_cutoff].copy()
else:
    df_recent = df.copy()

# sort by total desc (if exists)
sort_cols = ["total"] if "total" in df_recent.columns else None
if sort_cols:
    df_recent = df_recent.sort_values(sort_cols, ascending=False)

# optional join with a lookup (e.g., map item → department)
if os.path.exists(LOOKUP_PATH):
    lk = pd.read_csv(LOOKUP_PATH)
    # expect columns: item, department  (adjust if different)
    join_keys = ["item"] if "item" in lk.columns else None
    if join_keys:
        df_recent = df_recent.merge(lk, on=join_keys, how="left")

# --------- 5) AGGREGATE (groupby + pivot) ---------
# Groupby example: total revenue per category
if set(["category","total"]).issubset(df_recent.columns):
    revenue_by_cat = (
        df_recent.groupby("category", dropna=False)["total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"total":"revenue"})
    )
    print("\nRevenue by Category:")
    print(revenue_by_cat.head(10))

# Pivot example: items x month with total revenue
if {"item","total","date"}.issubset(df_recent.columns) and pd.api.types.is_datetime64_any_dtype(df_recent["date"]):
    df_recent["month"] = df_recent["date"].dt.to_period("M").astype(str)
    pivot = pd.pivot_table(
        df_recent,
        index="item",
        columns="month",
        values="total",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="Grand Total"
    )
    print("\nRevenue Pivot (Item x Month):")
    print(pivot.head(10))

# --------- 6) EXPORT CLEAN DATASETS (for capstone use) ---------
df_recent.to_parquet("clean_recent.parquet", index=False)
df_recent.to_csv("clean_recent.csv", index=False)
print("\nSaved: clean_recent.csv & clean_recent.parquet")
