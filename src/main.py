# import streamlit as st
# import os
# from orchestrator import Orchestrator

# # Streamlit UI
# st.title("AI-powered KYB Report Generator")

# # Input for company name
# company_name = st.text_input("Enter company name:")

# # Button to generate the report
# if st.button("Generate Report"):
#     if company_name:
#         st.write("🔄 Processing... Please wait.")
        
#         # Initialize Orchestrator
#         orchestrator = Orchestrator("./data/knowYourAi - Company Details.csv")
        
#         # Run the orchestrator and get the result
#         result = orchestrator.run(company_name)
#         print(f"Orchestrator result: {result}")  # Debugging output
        
#         # Define report file path
#         report_path = f"../reports/{company_name}_KYB_Report.txt"

#         # Check if the report was generated
#         if result:
#             # Ensure the report is created
#             with open(report_path, "w") as file:
#                 file.write(result)  # Assuming result contains the report content
            
#             # Check if the file exists after writing
#             if os.path.exists(report_path):
#                 st.success(f"✅ Report for {company_name} generated successfully!")

#                 # Provide download link for the generated report
#                 with open(report_path, "r") as file:
#                     report_content = file.read()
#                     st.download_button(
#                         label="📥 Download KYB Report",
#                         data=report_content,
#                         file_name=f"{company_name}_KYB_Report.txt",
#                         mime="text/plain"
#                     )
#             else:
#                 st.error(f"⚠️ The report file was not created successfully.")
#         else:
#             st.error(f"⚠️ No data found for {company_name}. Please check the spelling or update the dataset.")
#     else:
#         st.warning("⚠️ Please enter a company name.")

import streamlit as st
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from groq import Groq, RateLimitError
import json
import time
from duckduckgo_search import DDGS
from ratelimit import limits, sleep_and_retry

# Streamlit UI Setup
st.title("AI-powered KYB Report Generator")

# Input for company name
company_name = st.text_input("Enter company name:")

# Orchestrator Class - Placeholder (adjust as needed)
class Orchestrator:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
    
    def run(self, company_name):
        company_data = self.df[self.df['Company Name'].str.contains(company_name, case=False, na=False)]
        if not company_data.empty:
            return self.generate_report(company_data.iloc[0])
        else:
            return None
    
    def generate_report(self, company_data):
        # Generate the KYB Report using company data
        return f"Company Name: {company_data['Company Name']}\n" + "\n".join([f"{col}: {company_data[col]}" for col in company_data.index])

# API Keys & Rate Limiting
API_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]
current_key_index = 0
clients = [Groq(api_key=key) for key in API_KEYS]
CALLS_PER_MINUTE_GROQ = 5
CALLS_PER_MINUTE_DUCKDUCKGO = 50

# Helper functions
@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE_DUCKDUCKGO, period=60)
def duckduckgo_search(company_name, query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(keywords=f"{company_name} {query}", max_results=1)
            return " ".join(result['body'] for result in results if 'body' in result)[:500]
    except Exception as e:
        print(f"DuckDuckGo search error for {company_name}: {e}")
        return ""

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE_GROQ, period=60)
def call_grok_api(url, company):
    global current_key_index
    client = clients[current_key_index]

    # Web scraping and search content
    website_content = scrape_website(url) if url else "No website content."
    web_search_content = {
        "market_trends": duckduckgo_search(company['Company Name'], "AI industry trends"),
        "competitors": duckduckgo_search(company['Company Name'], "competitors")
    }

    company_details = "\n".join(
        f"- {col}: {company[col] if pd.notna(company[col]) else 'Unknown'}"
        for col in company.index
    )

    prompt = f"""
    Return valid JSON ONLY with actionable insights for 'Market Presence' and 'Competitor Analysis'. Use company details, website (1000 chars), and web searches (500 chars each). Estimate based on industry patterns, funding, valuation, partnerships if sparse, avoiding 'N/A'. Include 'industry_position' in 'Market Presence' if applicable, and list competitor names under 'competitors' in 'Competitor Analysis'.

    Company: {company['Company Name']}
    Details:
    {company_details}
    Website: {website_content}
    Web Search:
    - Market Trends: {web_search_content['market_trends']}
    - Competitors: {web_search_content['competitors']}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Return valid JSON with insights."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            temperature=0.1
        )
        response_text = response.choices[0].message.content.strip()

        if response_text.startswith('{') and response_text.endswith('}'):
            result = json.loads(response_text)
        else:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                result = json.loads(response_text[start:end])
            else:
                print(f"Invalid JSON for {url}. Using 'N/A'.")
                result = {col: "N/A" for col in ["Market Presence", "Competitor Analysis"]}

        return result
    except RateLimitError:
        print(f"Rate limit hit for key {current_key_index + 1}/{len(API_KEYS)} at {url}.")
        if len(API_KEYS) > 1:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            print(f"Switching to key {current_key_index + 1}/{len(API_KEYS)}.")
            return call_grok_api(url, company)  # Retry with next key
        else:
            wait_time = 60  # Fallback wait if only one key
            print(f"Only one key available. Waiting {wait_time}s.")
            time.sleep(wait_time)
            return call_grok_api(url, company)
    except Exception as e:
        print(f"Error for {url}: {e}")
        return {col: "N/A" for col in ["Market Presence", "Competitor Analysis"]}

def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/58.0.3029.110'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)[:1000]  # 1000 chars
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""

# Streamlit button to generate report
if st.button("Generate Report"):
    if company_name:
        st.write("🔄 Processing... Please wait.")
        
        # Initialize Orchestrator and run the process
        orchestrator = Orchestrator("../data/knowYourAi - Company Details.csv")
        result = orchestrator.run(company_name)

        if result:
            # Define report file path
            report_path = f"../reports/{company_name}_KYB_Report.txt"
            with open(report_path, "w") as file:
                file.write(result)

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
