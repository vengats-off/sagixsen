"""
Report Module - Lightweight bridge, no heavy imports at module level
"""
from flask import request, jsonify, send_file
from datetime import datetime, timezone
import os
import traceback


def generate_report():
    try:
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({'success': False, 'message': 'Missing symbol'}), 400

        symbol = data['symbol'].strip().upper()
        days = data.get('days', 365)

        # Import heavy modules only when needed
        from data_collection.angel_one_api import AngelOneAPI
        from data_collection.scraper import StockScraper
        from data_collection.news_fetcher import NewsFetcher
        from aws.s3_handler import S3Handler
        from aws.rds_connection import RDSConnection
        from etl.transformations import DataTransformer
        from etl.technical_indicators import TechnicalIndicators
        from ml_models.price_predictor import PricePredictor
        from ml_models.sentiment_analyzer import SentimentAnalyzer
        from ml_models.risk_calculator import RiskCalculator
        from ml_models.trend_classifier import TrendClassifier
        from visualization.chart_generator import ChartGenerator
        from pdf_generator.report_builder import PDFReportBuilder
        from backend.app import StockReportPipeline

        pipeline = StockReportPipeline()
        result = pipeline.generate_report(symbol, days)

        if result['success']:
            filename = os.path.basename(result['pdf_path'])
            return jsonify({
                'success': True,
                'message': result['message'],
                'pdf_url': f'/api/download-report/{filename}',
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'message': result['message']}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


def download_report(filename):
    try:
        from backend.config import Config
        filepath = os.path.join(Config.REPORTS_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        return send_file(filepath, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'report-generator',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })