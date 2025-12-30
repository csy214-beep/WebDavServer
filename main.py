"""
WebDAV服务管理器 - 主程序入口
基于PySide6的可视化WebDAV服务管理工具
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 确保data目录存在
if not os.path.exists('./data'):
    os.makedirs('./data')

from manager.ui_manager import WebDAVManagerUI
from manager.config_manager import ConfigManager
from manager.service_manager import ServiceManager
from manager.notification_manager import NotificationManager
import logging

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('./data/webdav.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """主程序入口"""
    logger.info("=" * 60)
    logger.info("WebDAV服务管理器启动")
    logger.info("=" * 60)

    try:
        # 创建Qt应用
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion风格,跨平台一致

        # 初始化配置管理器
        config_manager = ConfigManager()

        # 初始化服务管理器
        service_manager = ServiceManager()

        # 创建主窗口
        window = WebDAVManagerUI(config_manager, service_manager)
        window.show()

        logger.info("主界面已显示")

        # 运行应用
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()