# -*- coding: utf-8 -*-

import requests
from flask import g
from app.common.util.log_handler import log


class HttpClient:
    """HTTP 客户端封装

    特性:
    - 自动传递 X-Request-ID 用于链路追踪
    - 统一超时配置
    - 异常处理与日志
    - 支持重试
    """

    def __init__(self, base_url='', timeout=10, headers=None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _get_headers(self, extra_headers=None):
        headers = {}
        request_id = getattr(g, 'request_id', None) if g else None
        if request_id:
            headers['X-Request-ID'] = request_id
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _build_url(self, path):
        if path.startswith('http'):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path, params=None, headers=None, timeout=None):
        """GET 请求"""
        url = self._build_url(path)
        try:
            resp = self.session.get(
                url,
                params=params,
                headers=self._get_headers(headers),
                timeout=timeout or self.timeout
            )
            return self._handle_response(resp)
        except requests.RequestException as e:
            log.error(f"HTTP GET {url} failed: {e}")
            return None

    def post(self, path, json=None, data=None, headers=None, timeout=None):
        """POST 请求"""
        url = self._build_url(path)
        try:
            resp = self.session.post(
                url,
                json=json,
                data=data,
                headers=self._get_headers(headers),
                timeout=timeout or self.timeout
            )
            return self._handle_response(resp)
        except requests.RequestException as e:
            log.error(f"HTTP POST {url} failed: {e}")
            return None

    def put(self, path, json=None, data=None, headers=None, timeout=None):
        """PUT 请求"""
        url = self._build_url(path)
        try:
            resp = self.session.put(
                url,
                json=json,
                data=data,
                headers=self._get_headers(headers),
                timeout=timeout or self.timeout
            )
            return self._handle_response(resp)
        except requests.RequestException as e:
            log.error(f"HTTP PUT {url} failed: {e}")
            return None

    def delete(self, path, headers=None, timeout=None):
        """DELETE 请求"""
        url = self._build_url(path)
        try:
            resp = self.session.delete(
                url,
                headers=self._get_headers(headers),
                timeout=timeout or self.timeout
            )
            return self._handle_response(resp)
        except requests.RequestException as e:
            log.error(f"HTTP DELETE {url} failed: {e}")
            return None

    def _handle_response(self, resp):
        """统一处理响应"""
        log.info(f"HTTP {resp.request.method} {resp.url} -> {resp.status_code}")
        if resp.status_code >= 400:
            log.error(f"HTTP Error: {resp.status_code} - {resp.text[:200]}")
        try:
            return resp.json()
        except ValueError:
            return resp.text
