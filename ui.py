import json
import requests
import streamlit as st

API_URL = "http://localhost:8001/generate"


st.set_page_config(page_title="InteractiveAI Property Generator", layout="wide")
st.title("Property Listing Generator")


col1, col2 = st.columns(2)

with col1:
    st.header("Input JSON")

    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
    default_json_str = ""

    if uploaded_file is not None:
        input_text = uploaded_file.read().decode("utf-8")
    else:
        input_text = st.text_area(
            "Or paste JSON here",
            value=default_json_str,
            height=300,
        )

    generate_clicked = st.button("Generate HTML")


with col2:
    st.header("Output & Validation")

    if generate_clicked:
        try:
            data = json.loads(input_text)
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
        else:
            with st.spinner("Calling API..."):
                resp = requests.post(API_URL, json={"input_json": data})

            if resp.status_code != 200:
                st.error(f"API error {resp.status_code}: {resp.text}")
            else:
                payload = resp.json()
                html = payload["html"]
                validation = payload.get("validation", {})

                st.subheader("Preview")

                wrapped_html = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta charset="utf-8" />
                    <style>
                      body {{
                        margin: 0;
                        padding: 16px;
                        background-color: white;
                        color: #111;
                        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                      }}
                    </style>
                  </head>
                  <body>
                    {html}
                  </body>
                </html>
                """

                st.components.v1.html(wrapped_html, height=700, scrolling=True)

                st.subheader("Validation")
                st.json(validation)
