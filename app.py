import streamlit as st
import pandas as pd
import os
from io import BytesIO
import openpyxl
from fpdf import FPDF,HTMLMixin

# Setup of application
st.set_page_config(page_title="✅ Data Sweeper", layout='wide')
st.title("✅ Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")


# pdf convertor function

class PDF(FPDF, HTMLMixin):
    pass  # HTML mixin use karenge for table formatting





# state session
if "cleaned_files" not in st.session_state:
    st.session_state.cleaned_files = {}

# Take input files
uploaded_files = st.file_uploader("Upload your files (CSV or Excel).", type=[
                                  "csv", "xlsx"], accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(
                f"Unsupported file format: {file_ext} Please upload CSV or Excel files.")
            continue

        # Display file details
        file_size_mb = file.size / (1024 * 1024)  # Convert bytes to MB
        st.write(f"📂 File Name: {file.name}")
        st.write(f"📂 File Extension: {file_ext}")
        st.write(f"📏 File Size: {file_size_mb:.2f} MB")

        # Store DataFrame in session state
        if file.name not in st.session_state.cleaned_files:
            st.session_state.cleaned_files[file.name] = df.copy()

        df_cleaned = st.session_state.cleaned_files[file.name]

        # Cleaning options
        st.subheader(f"🛠 Data Cleaning Options for {file.name}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"✔ Remove Duplicates from {file.name}"):
                df_cleaned.drop_duplicates(inplace=True)
                # Save updated version
                st.session_state.cleaned_files[file.name] = df_cleaned
                st.success("✅ Duplicates removed!")

        with col2:
            if st.button(f"🗃️ Fill Missing values for {file.name}"):
                numeric_cols = df_cleaned.select_dtypes(
                    include=['number']).columns
                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(
                    df_cleaned[numeric_cols].mean())
                # Save updated version
                st.session_state.cleaned_files[file.name] = df_cleaned
                st.success("✅ Missing values filled!")

    # Display Updated DataFrame
        st.subheader(f"📊 Data Preview for {file.name}")
        st.dataframe(df_cleaned, height=350)

        
    # Visualization section for uploaded data
        st.subheader("📊 Data Visualization")
        # User selects columns (only numeric columns)
        visualize = st.multiselect(f"Choose columns for visualization (Min 2, Max 3) for {file.name}",
        df.select_dtypes(include='number').columns)
        
        # Check if user selected at least 2 and at most 3 columns
        if st.checkbox(f"Show Visualization for {file.name}"):
            if  len(visualize) == 0:
                st.warning("⚠️ Please select any column columns for visualization.")
            elif len(visualize) < 2 or len(visualize) > 3 :
                st.warning("⚠️ Please select between 2 and 3 columns for visualization.")
            else:
                st.bar_chart(df[visualize])



        # CONVERT FILE

        st.subheader("🎯 Select Columns to Convert")
        # Section to choose file conversion type (CSV or Excel)
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", [
                                   "CSV", "Excel"], key=file.name)
        if st.button(f"Convert the {file.name}"):
            # buffer = BytesIO()  # Creates in-memory buffer for file output
            if conversion_type == "CSV":
                # Save DataFrame as CSV in buffer
                buffer = BytesIO()  
                df_cleaned.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                # Save as Excel using openpyxl
                buffer = BytesIO()  
                df_cleaned.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            

            # Download button for the converted file
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )
