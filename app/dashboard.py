import os
from pathlib import Path

import streamlit as st

from clickpe_pim.queries import load_overview

st.set_page_config(page_title="ClickPe Product Intelligence Monitor", layout="wide")
st.title("ClickPe Product Intelligence Monitor")
st.caption("Evidence-first monitoring of public loan product information. Review items are not regulatory findings.")

db_path = Path(os.getenv("CLICKPE_PIM_DB", "data/db/monitor.sqlite"))
include_synthetic = os.getenv("CLICKPE_PIM_INCLUDE_SYNTHETIC") == "1"
overview = load_overview(db_path, include_synthetic=include_synthetic)
if not overview:
    st.info("No monitoring run is available. Run a live collection or opt into the synthetic replay fixture.")
else:
    if overview.get("synthetic"):
        st.warning("Synthetic replay data is visible. It is not a live ClickPe result.")
    if overview.get("status") == "partial" or overview.get("failed_sources"):
        st.warning("The latest run is partial or has failed sources. Last-good values may be stale.")
    a, b, c, d = st.columns(4)
    a.metric("Monitored products", overview["cohort_products"])
    b.metric("Inventory records", overview["inventory_products"])
    c.metric("Open review items", overview["review_items"])
    d.metric("High priority", overview["high_priority_items"])
    coverage = overview.get("coverage_ratio")
    st.write(f"Applicable official-source coverage: {overview['coverage_numerator']}/{overview['coverage_denominator']} ({coverage:.1%})" if coverage is not None else "Applicable official-source coverage: Unknown")
    st.write(f"Recent changes: {overview['recent_changes']} · Finalized runs: {overview['runs']}")

