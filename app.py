import yfinance as yf
from flask import Flask, request, jsonify
import json
import pkg_resources
import redis

app = Flask(__name__)
cache = redis.Redis(host='dwg8ccsc488cw8wc4o0c080c', password='8BZU1DMvRP2jgkPTdLBnJhGLdAgEK7kbLVIGs8Ys3kZH1v7yErcRRuQR9s5B5Nth', port=6379)
redis_ttl = 900


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

@app.route('/cachetest')
def cached():
    ticker = request.args.get('ticker')
    cached_info = cache.get(ticker)
    if cached_info is not None:
        info = json.loads(cached_info)
        info['x-cache'] = True
    else:
        try: 
            stock = yf.Ticker(ticker)
            cache.set(ticker, json.dumps(stock.info))
            cache.expire(ticker, redis_ttl)
            info = stock.info
            info['x-cache'] = False
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
