import os
import matplotlib.pyplot as plt
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
        # Step 1: Download and load dataset
        self.data_handler.download_dataset()
        self.data_handler.load_data()

        # Step 2: Get billing summary
        bill_summary = self.data_handler.get_summary_for_customer(customer_id, billing_month)
        bill_summary['customer_name'] = customer_name

        # Step 3: Generate line chart (daily usage)
        dates = [row[0] for row in bill_summary['table_data']]
        units = [row[3] for row in bill_summary['table_data']]

        chart_file = os.path.join(self.output_path, f"chart_{customer_id}_{billing_month.replace(' ', '_')}.png")

        plt.figure(figsize=(10, 4))
        plt.plot(dates, units, marker='o', linestyle='-', color='blue')
        plt.xticks(rotation=45)
        plt.title("Daily Electricity Usage")
        plt.xlabel("Date")
        plt.ylabel("Units Consumed (kWh)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(chart_file)
        plt.close()

        # Step 4: Add chart path to summary
        bill_summary['chart_path'] = os.path.basename(chart_file)

        # Step 5: Render HTML
        template = self.env.get_template('report_template.html')
        rendered_html = template.render(summary=bill_summary)

        # Step 6: Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
        output_file = os.path.join(self.output_path, f"bill_{customer_id}_{billing_month.replace(' ', '_')}.pdf")

        # Step 7: Generate PDF
        HTML(string=rendered_html, base_url=self.output_path).write_pdf(output_file)
        print(f"PDF report generated: {output_file}")

# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate("CUST001", "Ankit Pal", "July 2007")