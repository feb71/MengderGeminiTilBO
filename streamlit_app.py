
import os
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st

# Function to replace post IDs in XML files
def replace_post_ids(csv_file, input_dir, output_dir):
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

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each XML file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".xml"):
            file_path = os.path.join(input_dir, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                for element in root.iter():
                    if element.tag == 'Postnummer' and element.text in id_mapping:
                        original_value = element.text
                        element.text = id_mapping[element.text]
                        st.write(f"Replaced {original_value} with {element.text} in {filename}")

                # Write the modified XML to the output directory
                output_path = os.path.join(output_dir, filename)
                tree.write(output_path, encoding="utf-8", xml_declaration=True)
                st.success(f"Processed and saved {filename} to {output_dir}")
            except Exception as e:
                st.error(f"Error processing file {filename}: {e}")

# Streamlit UI
st.title("Post ID Replacement Tool")
st.write("Upload a CSV file and provide directories for input XML files and output.")

csv_file = st.file_uploader("Upload CSV file", type=["csv"])
input_dir = st.text_input("Input Directory (Path to XML files)")
output_dir = st.text_input("Output Directory (Path to save processed XML files)")

if st.button("Start Processing"):
    if csv_file is not None and input_dir and output_dir:
        replace_post_ids(csv_file, input_dir, output_dir)
    else:
        st.error("Please provide all required inputs.")
