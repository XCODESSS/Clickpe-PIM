import os
from pathlib import Path

import streamlit as st

from clickpe_pim.queries import load_changes

st.title("Change History")
db_path = Path(os.getenv("CLICKPE_PIM_DB", "data/db/monitor.sqlite"))
changes = load_changes(db_path, {})
if changes.empty:
    st.info("No historical comparison yet.")
else:
    include_synthetic = st.toggle("Include synthetic history", value=False)
    if not include_synthetic:
        changes = changes[~changes["synthetic"]]
    st.dataframe(changes, hide_index=True, use_container_width=True)

