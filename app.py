import yfinance as yf
from flask import Flask, request, jsonify
import json
import pkg_resources
import redis
import os

app = Flask(__name__)

# Load Redis configuration from environment variables
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_password = os.environ.get('REDIS_PASSWORD', '')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_ttl = int(os.environ.get('REDIS_TTL', 900))

# Initialize Redis client with environment variables
cache = redis.Redis(
    host=redis_host,
    password=redis_password,
    port=redis_port
)


@app.route('/health')
def health():
    return jsonify({"state": "healthy"}), 200


@app.route('/')
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

@app.route('/cached')
def cached():
    ticker = request.args.get('ticker')
    cached_info = cache.get(ticker)
    if cached_info is not None:
        # Get the remaining TTL for the cached key
        remaining_ttl = cache.ttl(ticker)
        
        info = json.loads(cached_info)
        info['x-cache'] = True
        info['x-cache-ttl'] = remaining_ttl
    else:
        try: 
            stock = yf.Ticker(ticker)
            cache.set(ticker, json.dumps(stock.info))
            cache.expire(ticker, redis_ttl)
            info = stock.info
            info['x-cache'] = False
            info['x-cache-ttl'] = redis_ttl
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify(info)


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