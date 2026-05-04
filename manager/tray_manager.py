"""
托盘管理模块
负责系统托盘功能
"""

import os
import sys
import socket
import subprocess
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class TrayManager:
    """系统托盘管理器"""

    def __init__(self, window, config_manager, service_manager):
        """初始化托盘管理器"""
        self.window = window
        self.config_manager = config_manager
        self.service_manager = service_manager

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()

        # 尝试设置图标
        self._set_tray_icon()

        # 创建菜单
        self.tray_menu = QMenu()
        self._create_menu()

        # 设置右键菜单
        self.tray_icon.setContextMenu(self.tray_menu)

        # 双击托盘图标显示主窗口
        self.tray_icon.activated.connect(self._on_tray_activated)

        # 显示托盘图标
        self.tray_icon.show()

        logger.info("Tray manager initialized")

    def _set_tray_icon(self):
        """设置托盘图标"""
        # 尝试使用应用图标，如果没有则使用默认图标
        try:
            # 这里可以使用自定义图标，暂时使用系统默认
            self.tray_icon.setIcon(QIcon("assets/icon.ico"))
        except:
            pass

    def _create_menu(self):
        """创建托盘菜单"""
        # 打开主界面
        self.open_action = QAction("Open Main Window")
        self.open_action.triggered.connect(self._show_window)
        self.tray_menu.addAction(self.open_action)

        # 分隔线
        self.tray_menu.addSeparator()

        # 启动停止服务
        self.toggle_service_action = QAction("Start Service")
        self.toggle_service_action.triggered.connect(self._toggle_service)
        self.tray_menu.addAction(self.toggle_service_action)

        # 分隔线
        self.tray_menu.addSeparator()

        # 复制访问地址
        self.copy_url_action = QAction("Copy Access URL")
        self.copy_url_action.triggered.connect(self._copy_url)
        self.tray_menu.addAction(self.copy_url_action)

        # 打开共享目录
        self.open_dir_action = QAction("Open Share Directory")
        self.open_dir_action.triggered.connect(self._open_directory)
        self.tray_menu.addAction(self.open_dir_action)

        # 查看日志
        self.view_log_action = QAction("View Log")
        self.view_log_action.triggered.connect(self._view_log)
        self.tray_menu.addAction(self.view_log_action)

        # 分隔线
        self.tray_menu.addSeparator()

        # 退出程序
        self.quit_action = QAction("Exit")
        self.quit_action.triggered.connect(self._quit_app)
        self.tray_menu.addAction(self.quit_action)

        # 更新菜单状态
        self.update_menu_state()

    def _on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        """显示主窗口"""
        self.window.show()
        self.window.activateWindow()
        self.window.raise_()

    def _toggle_service(self):
        """切换服务状态"""
        if self.service_manager.get_status():
            # 停止服务
            success, error_msg = self.service_manager.stop_service()
            if success:
                self.show_toast("Service stopped")
        else:
            # 启动服务
            config = self.config_manager.get_all_config()
            is_valid, errors = self.config_manager.validate_config()
            if not is_valid:
                self.show_toast(f"Invalid config: {errors[0]}")
                return

            success, error_msg = self.service_manager.start_service(config)
            if success:
                self.show_toast("WebDAV service started")
            else:
                self.show_toast(f"Failed to start WebDAV service: {error_msg}")

        self.update_menu_state()
        # 更新主界面按钮状态
        if hasattr(self.window, 'update_button_states'):
            self.window.update_button_states()
        # 更新主界面状态标签
        if hasattr(self.window, 'status_label'):
            if self.service_manager.get_status():
                self.window.status_label.setText(f"Status: Service running - Port {self.config_manager.get_config('port')}")
                self.window.status_label.setStyleSheet("color: #28a745; font-size: 12px; font-weight: bold;")
            else:
                self.window.status_label.setText("Status: Service not running")
                self.window.status_label.setStyleSheet("color: #666; font-size: 12px;")

    def _copy_url(self):
        """复制访问地址"""
        if not self.service_manager.get_status():
            self.show_toast("Service not running")
            return

        # 获取本机IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"

        port = self.config_manager.get_config('port')
        url = f"http://{local_ip}:{port}/"

        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        self.show_toast(f"Copied: {url}")

    def _open_directory(self):
        """打开共享目录"""
        share_dir = self.config_manager.get_config('share_dir', '')
        if not share_dir or not os.path.exists(share_dir):
            self.show_toast("Share directory does not exist")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(share_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', share_dir])
            else:
                subprocess.run(['xdg-open', share_dir])
            self.show_toast("Directory opened")
        except Exception as e:
            self.show_toast("Failed to open directory")
            logger.error(f"Failed to open directory: {e}")

    def _view_log(self):
        """查看日志"""
        log_file = './data/webdav.log'
        if not os.path.exists(log_file):
            self.show_toast("Log file does not exist")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(log_file)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_file])
            else:
                subprocess.run(['xdg-open', log_file])
            self.show_toast("Log opened")
        except Exception as e:
            self.show_toast("Failed to open log")
            logger.error(f"Failed to open log: {e}")

    def _quit_app(self):
        """退出应用"""
        # 先停止服务
        if self.service_manager.get_status():
            self.service_manager.stop_service()

        logger.info("Program exit")
        QApplication.quit()

    def update_menu_state(self):
        """更新菜单状态"""
        is_running = self.service_manager.get_status()

        # 更新启动停止服务按钮
        self.toggle_service_action.setText("Stop Service" if is_running else "Start Service")

        # 更新复制地址按钮状态
        self.copy_url_action.setEnabled(is_running)

        # 更新打开目录按钮状态
        share_dir = self.config_manager.get_config('share_dir', '')
        self.open_dir_action.setEnabled(bool(share_dir) and os.path.exists(share_dir))

    def show_toast(self, message):
        """显示通知"""
        self.tray_icon.showMessage(
            "WebDAV Service Manager",
            message,
            QSystemTrayIcon.Information,
            2000
        )

    def hide(self):
        """隐藏托盘图标"""
        self.tray_icon.hide()

    def show(self):
        """显示托盘图标"""
        self.tray_icon.show()
