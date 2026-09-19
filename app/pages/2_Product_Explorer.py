import json
import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from clickpe_pim.queries import load_product

st.title("Product Explorer")
db_path = Path(os.getenv("CLICKPE_PIM_DB", "data/db/monitor.sqlite"))
if not db_path.exists():
    st.info("No monitoring run is available.")
else:
    with sqlite3.connect(db_path) as con:
        products = [(row[0], json.loads(row[1]).get("name", row[0])) for row in con.execute("SELECT product_id,record_json FROM products ORDER BY product_id")]
    if not products:
        st.info("No monitored products are available.")
    else:
        labels = dict(products)
        product_id = st.selectbox("Product", [item[0] for item in products], format_func=lambda value: f"{labels[value]} ({value})")
        detail = load_product(db_path, product_id)
        st.subheader(detail["product"]["name"])
        mappings = detail.get("mappings", [])
        if not any(item.get("review_state") == "approved" and item.get("role") == "lender" for item in mappings):
            st.warning("Unresolved lender")
        rows = []
        for item in detail.get("observations", []):
            value = item.get("value") or {}
            normalized = value.get("text")
            if normalized is None and value.get("boolean") is not None:
                normalized = str(value["boolean"])
            if normalized is None:
                normalized = " – ".join(
                    part
                    for part in (
                        str(value.get("lower")) if value.get("lower") is not None else "",
                        str(value.get("upper")) if value.get("upper") is not None else "",
                    )
                    if part
                ) or "Unknown"
            rows.append(
                {
                    "field": item["field"],
                    "source": item["source_id"],
                    "state": item["state"],
                    "normalized": normalized,
                    "unit": value.get("unit"),
                    "period": value.get("period"),
                    "basis": value.get("basis"),
                    "raw evidence": item["raw_text"],
                    "evidence ID": item["observation_id"],
                }
            )
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
            column_config={"raw evidence": st.column_config.TextColumn(width="large")},
        )
        with st.expander("Entity and programme mappings"):
            st.json(mappings)
