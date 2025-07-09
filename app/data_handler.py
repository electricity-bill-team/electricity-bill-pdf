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
        Return both daily usage table and summary for a specific customer and billing month.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() after download_dataset().")

        month_dt = datetime.strptime(billing_month, "%B %Y")
        month_data = self.df[
            (self.df['Date'].dt.month == month_dt.month) &
            (self.df['Date'].dt.year == month_dt.year)
        ].copy()

        if month_data.empty:
            return None

        # Aggregate data to daily level
        month_data['DateOnly'] = month_data['Date'].dt.date
        daily_summary = month_data.groupby('DateOnly').agg(
            Start_Unit=('Global_active_power', 'first'),
            End_Unit=('Global_active_power', 'last'),
            Units_Consumed=('Global_active_power', lambda x: round(x.sum() / 60, 2))  # convert to kWh
        ).reset_index()

        # Build table headers and data for HTML template
        table_headers = ["Date", "Start Unit (kW)", "End Unit (kW)", "Units Consumed (kWh)"]
        table_data = [
            [
                row['DateOnly'].strftime('%Y-%m-%d'),
                round(row['Start_Unit'], 3),
                round(row['End_Unit'], 3),
                row['Units_Consumed']
            ]
            for _, row in daily_summary.iterrows()
        ]

        total_units = round(daily_summary['Units_Consumed'].sum(), 2)
        rate_per_unit = 7.5
        fixed_charge = 50
        total_amount = round(total_units * rate_per_unit + fixed_charge, 2)

        return {
            'customer_id': customer_id,
            'billing_month': billing_month,
            'date': month_dt.strftime("%Y-%m-%d"),
            'table_headers': table_headers,
            'table_data': table_data,
            'summary': {
                'total_units': total_units,
                'rate_per_unit': rate_per_unit,
                'fixed_charge': fixed_charge,
                'total_amount': total_amount
            }
        }

# Example usage
if __name__ == "__main__":
    handler = ElectricityDataHandler()
    handler.download_dataset()
    handler.load_data()
    result = handler.get_summary_for_customer("CUST001", "July 2007")
    print(result)