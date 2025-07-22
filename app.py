import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import st_folium

# Streamlit page config
st.set_page_config(page_title="Nestory Support Request", layout="centered")

st.title("Nestory Support Request")
st.markdown("Please fill out this form to request support. We’ll connect you to local help near you.")

# Form input
with st.form(key='support_form'):
    name = st.text_input("Your Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone (optional)")
    support_type = st.selectbox(
        "What do you need?",
        ["Food", "Debt Advice", "Healthy Start", "Warm Space", "Mental Health", "Other"]
    )
    location = st.text_input("Your Area or Postcode")
    details = st.text_area("Any additional information")
    submit = st.form_submit_button("Submit Request")

# Save form data
if submit:
    data = {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Support Type": support_type,
        "Location": location,
        "Details": details,
        "Timestamp": datetime.datetime.now()
    }

    df = pd.DataFrame([data])
    df.to_csv("requests.csv", mode='a', header=not pd.io.common.file_exists("requests.csv"), index=False)
    st.success("Thanks! Your request has been received.")

# Show map based on support type
if support_type in ["Food", "Warm Space", "Healthy Start"]:
    st.subheader("Nearby Support Locations For You")

    try:
        df = pd.read_csv("locations.csv")

        # Filter based on support type
        filtered_df = df[df["type"].str.lower().str.contains(support_type.lower())]

        # Type → colour map
        type_color = {
            "Food Bank": "green",
            "Warm Space": "blue",
            "Healthy Start": "red",
            "Debt Advice": "orange",
            "Mental Health": "purple"
        }

        # Create map centered on Bradford
        m = folium.Map(location=[53.7960, -1.7590], zoom_start=12)

        for _, row in filtered_df.iterrows():
            colour = type_color.get(row["type"], "gray")

            # Build popup HTML
            popup_html = f"<b>{row['name']}</b><br>{row['type']}"

            if pd.notna(row.get("website", "")):
                popup_html += f"<br><a href='{row['website']}' target='_blank'>More Info</a>"

            if pd.notna(row.get("contact", "")):
                popup_html += f"<br><b>Contact:</b> {row['contact']}"

            if str(row.get("verified", "")).lower() == "true":
                popup_html += "<br><span style='color:green;'>✅ Verified</span>"

            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=colour)
            ).add_to(m)

        # Show map in Streamlit
        st_folium(m, width=700, height=500)

    except FileNotFoundError:
        st.error("Location data not found. Please add a `locations.csv` file.")
