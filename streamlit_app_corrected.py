
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
        st.write(f"Mapping {postnr} to {post_id}")

    # Process each uploaded XML file
    for uploaded_file in uploaded_xml_files:
        try:
            st.write(f"Processing file: {uploaded_file.name}")
            tree = ET.parse(uploaded_file)
            root = tree.getroot()
            modified = False

            st.write("Checking values in XML file for matches...")
            # Collecting all PostNr values in XML
            xml_postnr_values = []
            for element in root.iter('Post'):
                postnr_element = element.find('PostNr')
                if postnr_element is not None:
                    postnr_value = postnr_element.text.strip()
                    xml_postnr_values.append(postnr_value)
                    if postnr_value in id_mapping:
                        original_value = postnr_value
                        postnr_element.text = id_mapping[postnr_value]
                        st.write(f"Replaced {original_value} with {postnr_element.text} in {uploaded_file.name}")
                        modified = True
            
            # Display all found 'PostNr' values in the XML file for debugging
            st.write("Found 'PostNr' values in XML file:", xml_postnr_values)
            st.write("These are the 'Postnr' values we're trying to match from CSV:", list(id_mapping.keys()))

            # Save the modified XML to a downloadable file
            if modified:
                output = BytesIO()
                tree.write(output, encoding="utf-8", xml_declaration=True)
                output.seek(0)
                st.download_button(
                    label=f"Download modified {uploaded_file.name}",
                    data=output,
                    file_name=f"modified_{uploaded_file.name}",
                    mime="application/xml"
                )
                st.success(f"Processed and created downloadable XML for {uploaded_file.name}")
            else:
                st.warning(f"No changes made to the file: {uploaded_file.name}. Check if 'PostNr' values match those in the CSV.")
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
