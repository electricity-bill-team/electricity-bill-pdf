import pandas as pd
from datetime import datetime
import kagglehub
import os

class ElectricityDataHandler:
    def __init__(self):
        self.df = None
        self.dataset_path = None

    def download_dataset(self):
        """
        Use kagglehub to download dataset and set path to file.
        """
        print("Downloading dataset from Kaggle...")
        download_path = kagglehub.dataset_download("uciml/electric-power-consumption-data-set")
        self.dataset_path = os.path.join(download_path, "household_power_consumption.txt")

    def load_data(self):
        """
        Load and clean the electricity data from the downloaded file.
        """
        try:
            self.df = pd.read_csv(self.dataset_path, sep=';', low_memory=False, na_values=['?'])
            self.df.dropna(subset=['Global_active_power'], inplace=True)
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y')
            self.df['Global_active_power'] = self.df['Global_active_power'].astype(float)
        except Exception as e:
            print("Error loading data:", e)

    def get_summary_for_customer(self, customer_id: str, billing_month: str):
        """
        Simulate fetching consumption details for a customer based on billing month.
        This is mock logic since original dataset has no customer info.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() after download_dataset().")

        month_dt = datetime.strptime(billing_month, "%B %Y")
        month_data = self.df[
            (self.df['Date'].dt.month == month_dt.month) &
            (self.df['Date'].dt.year == month_dt.year)
        ]

        total_kwh = month_data['Global_active_power'].sum()
        units_consumed = round(total_kwh, 2)
        rate_per_unit = 7.5  # fixed
        fixed_charge = 50
        total_amount = round(units_consumed * rate_per_unit + fixed_charge, 2)

        return {
            'customer_id': customer_id,
            'billing_month': billing_month,
            'units_consumed': units_consumed,
            'rate_per_unit': rate_per_unit,
            'fixed_charge': fixed_charge,
            'total_amount': total_amount,
            'date': month_dt.strftime("%Y-%m-%d")
        }

# Example usage
if __name__ == "__main__":
    handler = ElectricityDataHandler()
    handler.download_dataset()
    handler.load_data()
    summary = handler.get_summary_for_customer("CUST001", "July 2007")
    print(summary)
