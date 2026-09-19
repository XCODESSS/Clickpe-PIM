import os
from pathlib import Path

import streamlit as st

from clickpe_pim.queries import load_providers

st.title("Provider Intelligence")
st.caption("Entity roles and programmes stay separate; no provider ranking is produced.")
providers = load_providers(Path(os.getenv("CLICKPE_PIM_DB", "data/db/monitor.sqlite")))
if providers.empty:
    st.info("No reviewed provider mappings are available.")
else:
    st.dataframe(providers, hide_index=True, use_container_width=True)

