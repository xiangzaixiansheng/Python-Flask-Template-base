# -*- coding: utf-8 -*-

from flask import Blueprint
from app.extension import db, rd
from app.common.util.log_handler import log

health_bp = Blueprint('health', __name__)


@health_bp.route('', methods=['GET'])
def health_check():
    """健康检查端点，用于容器探针和负载均衡"""
    status = {"status": "healthy", "services": {}}

    try:
        db.session.execute(db.text('SELECT 1'))
        status["services"]["database"] = "up"
    except Exception as e:
        status["services"]["database"] = "down"
        status["status"] = "degraded"
        log.error(f"Health check - DB failed: {e}")

    try:
        if rd and rd.ping():
            status["services"]["redis"] = "up"
        else:
            status["services"]["redis"] = "down"
            status["status"] = "degraded"
    except Exception as e:
        status["services"]["redis"] = "down"
        status["status"] = "degraded"
        log.error(f"Health check - Redis failed: {e}")

    http_status = 200 if status["status"] == "healthy" else 503
    from flask import jsonify
    return jsonify(status), http_status
