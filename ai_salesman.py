
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "AI Salesman for Business Loans is running"})

@app.route("/qualify", methods=["POST"])
def qualify():
    data = request.json
    
    revenue = data.get("monthly_revenue", 0)
    months_in_business = data.get("months_in_business", 0)
    credit_score = data.get("credit_score", 0)
    
    # Simple qualification logic
    qualified = revenue >= 10000 and months_in_business >= 6 and credit_score >= 650
    
    if qualified:
        loan_amount = int(revenue * 3)
        return jsonify({
            "qualified": True,
            "max_loan_amount": loan_amount,
            "message": f"You pre-qualify for up to ${loan_amount}. We'll contact you with next steps."
        })
    else:
        return jsonify({
            "qualified": False,
            "message": "You don't meet the minimum requirements yet. Need 6+ months in business, $10k+ monthly revenue, and 650+ credit score."
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
flask-cors
gunicorn
Then go back to Render and hit refresh. Let me know when the repo shows up and I’ll walk you through the deploy settings.
