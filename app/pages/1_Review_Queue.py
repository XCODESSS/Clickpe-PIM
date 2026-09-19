import os
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from components import render_evidence

from clickpe_pim.queries import load_evidence, load_queue, record_review

st.title("Review Queue")
st.caption("Potential differences and missing information requiring review.")
db_path = Path(os.getenv("CLICKPE_PIM_DB", "data/db/monitor.sqlite"))
include_synthetic = os.getenv("CLICKPE_PIM_INCLUDE_SYNTHETIC") == "1"
queue = load_queue(db_path, {}, include_synthetic=include_synthetic)
if queue.empty:
    st.info("No review items are available.")
else:
    fields = st.multiselect("Field", sorted(queue["field"].dropna().unique()))
    statuses = st.multiselect("Status", sorted(queue["status"].dropna().unique()))
    queue = load_queue(db_path, {"field": fields, "status": statuses}, include_synthetic=include_synthetic)
    st.dataframe(queue, hide_index=True, use_container_width=True)
    choice = st.selectbox("Select review item", queue["comparison_id"].tolist(), format_func=lambda value: f"{queue.loc[queue.comparison_id == value, 'product_id'].iloc[0]} · {queue.loc[queue.comparison_id == value, 'field'].iloc[0]}")
    row = queue.loc[queue.comparison_id == choice].iloc[0]
    render_evidence(load_evidence(db_path, choice))
    with st.form("review"):
        reviewer = st.text_input("Reviewer")
        disposition = st.selectbox("Outcome", ["confirmed_useful", "legitimate_programme_difference", "extraction_issue", "dismissed", "resolved"])
        note = st.text_area("Note")
        if st.form_submit_button("Record review"):
            try:
                record_review(db_path, row["fingerprint"], reviewer, disposition, note, datetime.now(timezone.utc))
                st.success("Review event recorded.")
            except ValueError as exc:
                st.error(str(exc))

