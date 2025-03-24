import yfinance as yf
from flask import Flask, request, jsonify
import json
import pkg_resources

app = Flask(__name__)

@app.route('/cached')
def info():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/news')
def news():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/versions')
def versions():
    packages = {
        "Flask": pkg_resources.get_distribution("Flask").version,
        "Werkzeug": pkg_resources.get_distribution("Werkzeug").version,
        "yfinance": pkg_resources.get_distribution("yfinance").version,
        "gunicorn": pkg_resources.get_distribution("gunicorn").version
    }
    return jsonify(packages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
