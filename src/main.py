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

# import streamlit as st
# import requests
# import os

# # Streamlit UI
# st.set_page_config(page_title="KYB Due Diligence Tool", layout="centered")
# st.title("Know Your Business (KYB) Due Diligence Tool")

# # Input fields
# api_key = st.text_input("Enter your Groq API Key", type="password")
# company_name = st.text_input("Enter Company Name")
# custom_prompt = st.text_area("Or Write a Custom Prompt")
# admin_view = st.checkbox("Admin View")

# def query_groq_api(prompt, api_key):
#     """Queries the Groq API with a given prompt."""
#     url = "https://api.groq.com/v1/chat/completions"
#     headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#     payload = {
#         "model": "LLaMA-3-70B",
#         "messages": [{"role": "user", "content": prompt}],
#         "max_tokens": 1024
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     return response.json()

# if st.button("Generate Report"):
#     if not api_key:
#         st.error("Please enter a valid Groq API Key.")
#     elif not company_name and not custom_prompt:
#         st.error("Please enter a company name or write a custom prompt.")
#     else:
#         prompt = custom_prompt if custom_prompt else f"Provide a KYB report for {company_name}."
#         st.info("Fetching data, please wait...")
        
#         response = query_groq_api(prompt, api_key)
        
#         if "choices" in response:
#             st.subheader("KYB Report")
#             st.write(response["choices"][0]["message"]["content"])
#         else:
#             st.error("Error fetching data. Check API key or try again.")
