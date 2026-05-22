# -*- coding: utf-8 -*-

import os
from flask import Blueprint, request, current_app
from app.middleware.authMiddleware import token_required
from app.common.result.result import Result
from app.common.util.log_handler import log

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xlsx', 'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('', methods=['POST'])
@token_required
def upload_file():
    """文件上传"""
    if 'file' not in request.files:
        return Result.failed(400, '未选择文件')

    file = request.files['file']
    if file.filename == '':
        return Result.failed(400, '文件名为空')

    if not allowed_file(file.filename):
        return Result.failed(400, f'不支持的文件类型，允许: {", ".join(ALLOWED_EXTENSIONS)}')

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    from werkzeug.utils import secure_filename
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    original_name = secure_filename(file.filename)
    filename = f"{timestamp}_{original_name}"

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    file_size = os.path.getsize(filepath)
    log.info(f"文件上传成功: {filename}, 大小: {file_size} bytes")

    return Result.success({
        "filename": filename,
        "original_name": original_name,
        "size": file_size,
        "path": filepath
    })
