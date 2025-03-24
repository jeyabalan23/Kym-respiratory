import streamlit as st
import os
from orchestrator import Orchestrator

# Streamlit UI
st.title("AI-powered KYB Report Generator")

# Input for company name
company_name = st.text_input("Enter company name:")

# Button to generate the report
if st.button("Generate Report"):
    if company_name:
        st.write("🔄 Processing... Please wait.")
        
        # Initialize Orchestrator
        orchestrator = Orchestrator("./data/knowYourAi - Company Details.csv")
        
        # Run the orchestrator and get the result
        result = orchestrator.run(company_name)
        print(f"Orchestrator result: {result}")  # Debugging output
        
        # Define report file path
        report_path = f"../reports/{company_name}_KYB_Report.txt"

        # Check if the report was generated
        if result:
            # Ensure the report is created
            with open(report_path, "w") as file:
                file.write(result)  # Assuming result contains the report content
            
            # Check if the file exists after writing
            if os.path.exists(report_path):
                st.success(f"✅ Report for {company_name} generated successfully!")

                # Provide download link for the generated report
                with open(report_path, "r") as file:
                    report_content = file.read()
                    st.download_button(
                        label="📥 Download KYB Report",
                        data=report_content,
                        file_name=f"{company_name}_KYB_Report.txt",
                        mime="text/plain"
                    )
            else:
                st.error(f"⚠️ The report file was not created successfully.")
        else:
            st.error(f"⚠️ No data found for {company_name}. Please check the spelling or update the dataset.")
    else:
        st.warning("⚠️ Please enter a company name.")
