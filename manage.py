# -*- coding: utf-8 -*-

import os
import sys

from dotenv import load_dotenv
load_dotenv()

from apscheduler.schedulers.background import BackgroundScheduler

from app import create_app
from app.common.util.env_validator import print_env_status

config_name = os.environ.get('FLASK_ENV', 'development')

if config_name != 'testing':
    print_env_status()
app = create_app(config_name)


def start_scheduler():
    """创建并启动后台定时任务调度器"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(func=your_task, trigger="interval", seconds=60)
    scheduler.start()


if __name__ == '__main__':
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(current_file)
    if base_dir not in sys.path:
        sys.path.append(base_dir)

    # 避免 reloader 子进程重复启动 scheduler
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        start_scheduler()

    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=3000,
    )
