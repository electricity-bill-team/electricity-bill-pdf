import os
import base64
import matplotlib.pyplot as plt
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from data_handler import ElectricityDataHandler

class ReportGenerator:
    def __init__(self):
        self.data_handler = ElectricityDataHandler()
        self.template_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.output_path = os.path.join(os.path.dirname(__file__), '..', 'reports')
        self.env = Environment(loader=FileSystemLoader(self.template_path))

    def generate(self, customer_id: str, customer_name: str, billing_month: str):
        # Step 1: Load data
        self.data_handler.download_dataset()
        self.data_handler.load_data()

        # Step 2: Fetch processed summary
        bill_summary = self.data_handler.get_summary_for_customer(customer_id, billing_month)

        # Step 3: Validate
        if not bill_summary:
            print("⚠ No data available for the selected month.")
            return

        # Step 4: Generate usage chart as base64
        dates = [row[0] for row in bill_summary['table_data']]
        units = [row[3] for row in bill_summary['table_data']]

        plt.figure(figsize=(10, 4))
        plt.plot(dates, units, marker='o', linestyle='-', color='blue')
        plt.xticks(rotation=45, fontsize=8)
        plt.title("Daily Electricity Usage")
        plt.xlabel("Date")
        plt.ylabel("Units Consumed (kWh)")
        plt.grid(True)
        plt.tight_layout()

        img_stream = BytesIO()
        plt.savefig(img_stream, format='png')
        plt.close()
        img_stream.seek(0)
        chart_base64 = base64.b64encode(img_stream.read()).decode('utf-8')

        # Step 5: Prepare data for template
        summary = bill_summary['summary']
        summary.update({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'billing_month': billing_month,
            'date': bill_summary['date'],
            'chart_base64': chart_base64
        })

        # Step 6: Render and export
        template = self.env.get_template('report_template.html')
        rendered_html = template.render(
            summary=summary,
            table_headers=bill_summary['table_headers'],
            table_data=bill_summary['table_data']
        )

        os.makedirs(self.output_path, exist_ok=True)
        output_file = os.path.join(
            self.output_path,
            f"bill_{customer_id}_{billing_month.replace(' ', '_')}.pdf"
        )
        HTML(string=rendered_html, base_url=self.output_path).write_pdf(output_file)
        print(f"✅ PDF report generated at: {output_file}")

# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate("CUST001", "Ankit Pal", "December 2006")
