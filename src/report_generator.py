import os
import pandas as pd

class ReportGenerator:
    def __init__(self, dataset_path):
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        self.dataset = pd.read_csv(dataset_path)

    def generate_report(self, company_name):
        company_data = self.dataset[self.dataset["Company Name"].str.lower() == company_name.lower()]
        if company_data.empty:
            print(f"No data found for {company_name}.")
            return None
        
        report = f"KYB Report for {company_name}\n\n"
        report += company_data.to_string(index=False)
        return report

    def save_report(self, company_name, report):
        reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports"))
        os.makedirs(reports_dir, exist_ok=True)  # Ensure directory exists
        
        report_path = os.path.join(reports_dir, f"{company_name}_KYB_Report.txt")
        with open(report_path, "w", encoding="utf-8") as file:
            file.write(report)
        
        print(f"Report saved at: {report_path}")

if __name__ == "__main__":
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/enriched_dataset.csv"))
    generator = ReportGenerator(dataset_path)
    
    company = input("Enter company name: ").strip()
    report = generator.generate_report(company)
    
    if report:
        generator.save_report(company, report)
