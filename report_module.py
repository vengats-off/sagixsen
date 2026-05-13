"""
Report Module - Bridge between main.py and report pipeline
"""
from flask import request, jsonify, send_file
from datetime import datetime, timezone
import os
import traceback


def generate_report():
    try:
        from backend.config import Config
        from backend.app import StockReportPipeline

        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({'success': False, 'message': 'Missing symbol'}), 400

        symbol = data['symbol'].strip().upper()
        days = data.get('days', 365)

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