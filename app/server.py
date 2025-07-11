from flask import Flask, render_template, request, send_file, abort
from datetime import datetime
from generate_report import ReportGenerator

app = Flask(__name__, template_folder="../templates")


@app.route('/', methods=['GET'])
def index():
    # Generate billing months from Dec 2006 to Dec 2008
    start_date = datetime(2006, 12, 1)
    end_date = datetime(2008, 12, 1)

    months = []
    current = start_date
    while current <= end_date:
        months.append(current.strftime('%B %Y'))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return render_template('form.html', months=months)


@app.route('/generate-bill', methods=['POST'])
def generate_bill():
    customer_id = request.form.get('customer_id')
    customer_name = request.form.get('customer_name')
    billing_month = request.form.get('billing_month')

    try:
        generator = ReportGenerator()
        pdf_path = generator.generate(customer_id, customer_name, billing_month)
        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
    except Exception as e:
        print(f"Error generating bill: {e}")
        return abort(500, description="Failed to generate bill. Please check your inputs and try again.")


if __name__ == '__main__':
    app.run(debug=True)
