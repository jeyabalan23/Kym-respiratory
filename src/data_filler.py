import pandas as pd

class DataFiller:
    def __init__(self, dataset_path):
        self.dataset = pd.read_csv(dataset_path)

    def enrich_data(self):
        for col in self.dataset.columns:
            self.dataset[col].fillna("Estimated Value", inplace=True)  # Placeholder for AI/LLM logic

    def save_updated_dataset(self, output_path):
        self.dataset.to_csv(output_path, index=False)

if __name__ == "__main__":
    filler = DataFiller("./data/knowYourAi - Company Details.csv")
    filler.enrich_data()
    filler.save_updated_dataset("../data/enriched_dataset.csv")
    print("Data enrichment completed!")
