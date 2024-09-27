
import os
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
from io import BytesIO

# Function to replace post IDs in uploaded XML files
def replace_post_ids(csv_file, uploaded_xml_files):
    # Read the CSV file with semicolon separator
    st.write("Reading CSV file...")
    try:
        df = pd.read_csv(csv_file, sep=';')
        st.write("CSV file structure:")
        st.write(df.head())
        st.write("CSV columns:", df.columns)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return

    # Ensure that the required columns are present
    if 'Postnr' not in df.columns or 'Id' not in df.columns:
        st.error("CSV file must contain 'Postnr' and 'Id' columns")
        return

    # Create a mapping of Postnr to Id from the CSV file
    id_mapping = {}
    st.write("Creating ID mapping...")
    for index, row in df.iterrows():
        postnr = str(row['Postnr']).strip()
        post_id = str(row['Id']).strip()
        id_mapping[postnr] = post_id

    # Process each uploaded XML file
    for uploaded_file in uploaded_xml_files:
        try:
            tree = ET.parse(uploaded_file)
            root = tree.getroot()
            modified = False

            for element in root.iter():
                if element.tag == 'Postnummer' and element.text in id_mapping:
                    original_value = element.text
                    element.text = id_mapping[element.text]
                    st.write(f"Replaced {original_value} with {element.text} in {uploaded_file.name}")
                    modified = True

            # Save the modified XML to a downloadable file
            if modified:
                output = BytesIO()
                tree.write(output, encoding="utf-8", xml_declaration=True)
                output.seek(0)
                st.download_button(
                    label=f"Download modified {uploaded_file.name}",
                    data=output,
                    file_name=uploaded_file.name,
                    mime="application/xml"
                )
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")

# Streamlit UI
st.title("Post ID Replacement Tool")
st.write("Upload a CSV file and XML files to replace post IDs.")

csv_file = st.file_uploader("Upload CSV file", type=["csv"])
uploaded_xml_files = st.file_uploader("Upload XML files", type=["xml"], accept_multiple_files=True)

if st.button("Start Processing"):
    if csv_file is not None and uploaded_xml_files:
        replace_post_ids(csv_file, uploaded_xml_files)
    else:
        st.error("Please provide all required inputs.")
