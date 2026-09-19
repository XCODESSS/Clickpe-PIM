from urllib.parse import urlsplit

import streamlit as st


def safe_url(value: str) -> str | None:
    parsed = urlsplit(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else None


def render_evidence(evidence: dict) -> None:
    comparison = evidence.get("comparison", {})
    st.subheader("Evidence")
    st.write(comparison.get("reason", "No comparison evidence is available."))
    mapping = evidence.get("mapping")
    if mapping:
        st.caption(f"Programme mapping: {mapping.get('rationale', 'No rationale')} (confidence {mapping.get('confidence')})")
    columns = st.columns(2)
    for index, item in enumerate(evidence.get("evidence", [])):
        observation, capture = item["observation"], item["capture"]
        with columns[index % 2]:
            st.markdown(f"**{item['source_type']}**")
            if safe_url(item["url"]):
                st.link_button("Open source", item["url"])
            st.text(observation.get("raw_text", ""))
            st.json(observation.get("value"))
            st.caption(f"Captured {capture.get('retrieved_at')} · SHA-256 {capture.get('sha256')}")

