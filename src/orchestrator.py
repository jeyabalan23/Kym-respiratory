from data_filler import DataFiller
from report_generator import ReportGenerator
import os



class Orchestrator:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def run(self, company_name):
        print("Starting AI-powered KYB process...")
        
        # Step 1: Fill missing data
        filler = DataFiller(self.dataset_path)
        filler.enrich_data()
        filler.save_updated_dataset(self.dataset_path)
        print("Data enrichment completed.")
        
        # Step 2: Generate KYB report
        generator = ReportGenerator(self.dataset_path)
        report = generator.generate_report(company_name)
        
        if report:
            reports_dir = "../reports"
            os.makedirs(reports_dir, exist_ok=True)  # Ensure the reports directory exists
            report_path = os.path.join(reports_dir, f"{company_name}_KYB_Report.txt")
            
            with open(report_path, "w", encoding="utf-8") as file:
                file.write(report)
            print(f"KYB report for {company_name} generated successfully at {report_path}!")
        else:
            print(f"Warning: No KYB report generated for {company_name}! Possible data issues.")
        
        return report  # Return the generated report for further processing

if __name__ == "__main__":
    company_name = input("Enter company name for KYB: ")
    orchestrator = Orchestrator("../data/knowYourAi - Company Details.csv")
    result = orchestrator.run(company_name)
    if not result:
        print("No valid report was generated. Please check your data.")