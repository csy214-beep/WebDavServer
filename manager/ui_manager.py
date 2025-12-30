"""
UI管理模块
负责创建和管理用户界面
"""

import os
import sys
import socket
import subprocess
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QGroupBox, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIntValidator, QClipboard
from .notification_manager import NotificationManager
import logging

logger = logging.getLogger(__name__)


class WebDAVManagerUI(QMainWindow):
    """WebDAV管理器主界面"""

    def __init__(self, config_manager, service_manager):
        """初始化主界面"""
        super().__init__()

        self.config_manager = config_manager
        self.service_manager = service_manager
        self.notification = None  # 延迟初始化

        self.init_ui()
        self.load_config_to_ui()
        self.update_button_states()

        # 初始化通知管理器(在UI创建后)
        self.notification = NotificationManager(self.centralWidget())

    def init_ui(self):
        """初始化UI界面"""
        # 设置窗口属性
        self.setWindowTitle("WebDAV 服务管理器")
        self.setFixedSize(550, 480)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 配置区域
        config_group = self.create_config_group()
        main_layout.addWidget(config_group)

        # 控制按钮区域
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)

        # 辅助功能区域
        helper_layout = self.create_helper_buttons()
        main_layout.addLayout(helper_layout)

        # 状态标签
        self.status_label = QLabel("状态: 服务未启动")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        # 添加弹性空间
        main_layout.addStretch()

    def create_config_group(self):
        """创建配置区域"""
        group = QGroupBox("服务配置")
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # 共享目录
        dir_layout = QHBoxLayout()
        dir_label = QLabel("共享目录:")
        dir_label.setFixedWidth(80)
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("选择要共享的文件夹")
        self.dir_browse_btn = QPushButton("浏览")
        self.dir_browse_btn.setFixedWidth(80)
        self.dir_browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.dir_browse_btn)
        layout.addLayout(dir_layout)

        # 服务端口
        port_layout = QHBoxLayout()
        port_label = QLabel("服务端口:")
        port_label.setFixedWidth(80)
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("1025-65535")
        self.port_edit.setValidator(QIntValidator(1025, 65535))
        self.port_edit.setFixedWidth(120)
        port_hint = QLabel("(建议: 8088-8099)")
        port_hint.setStyleSheet("color: #999; font-size: 11px;")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        port_layout.addWidget(port_hint)
        port_layout.addStretch()
        layout.addLayout(port_layout)

        # 访问账号
        user_layout = QHBoxLayout()
        user_label = QLabel("访问账号:")
        user_label.setFixedWidth(80)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("设置登录账号")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_edit)
        layout.addLayout(user_layout)

        # 访问密码
        pass_layout = QHBoxLayout()
        pass_label = QLabel("访问密码:")
        pass_label.setFixedWidth(80)
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setPlaceholderText("设置登录密码")
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_edit)
        layout.addLayout(pass_layout)

        group.setLayout(layout)
        return group

    def create_control_buttons(self):
        """创建控制按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # 应用配置按钮
        self.apply_btn = QPushButton("应用配置")
        self.apply_btn.setFixedHeight(40)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_config)

        # 启动服务按钮
        self.start_btn = QPushButton("启动服务")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_service)

        # 停止服务按钮
        self.stop_btn = QPushButton("停止服务")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_service)

        layout.addWidget(self.apply_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        return layout

    def create_helper_buttons(self):
        """创建辅助功能按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # 复制地址按钮
        self.copy_url_btn = QPushButton("复制访问地址")
        self.copy_url_btn.clicked.connect(self.copy_url)

        # 打开目录按钮
        self.open_dir_btn = QPushButton("打开共享目录")
        self.open_dir_btn.clicked.connect(self.open_directory)

        # 查看日志按钮
        self.view_log_btn = QPushButton("查看日志")
        self.view_log_btn.clicked.connect(self.view_log)

        # 统一样式
        button_style = """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """

        self.copy_url_btn.setStyleSheet(button_style)
        self.open_dir_btn.setStyleSheet(button_style)
        self.view_log_btn.setStyleSheet(button_style)

        layout.addWidget(self.copy_url_btn)
        layout.addWidget(self.open_dir_btn)
        layout.addWidget(self.view_log_btn)

        return layout

    def browse_directory(self):
        """浏览选择目录"""
        current_dir = self.dir_edit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self, "选择共享目录", current_dir
        )
        if directory:
            self.dir_edit.setText(directory)
            logger.info(f"用户选择目录: {directory}")

    def load_config_to_ui(self):
        """加载配置到UI"""
        config = self.config_manager.get_all_config()
        self.dir_edit.setText(config.get('share_dir', ''))
        self.port_edit.setText(str(config.get('port', 8088)))
        self.user_edit.setText(config.get('username', ''))
        self.pass_edit.setText(config.get('password', ''))
        logger.info("配置已加载到界面")

    def save_ui_to_config(self):
        """保存UI配置到配置管理器"""
        self.config_manager.set_config('share_dir', self.dir_edit.text().strip())
        try:
            port = int(self.port_edit.text())
        except:
            port = 8088
        self.config_manager.set_config('port', port)
        self.config_manager.set_config('username', self.user_edit.text().strip())
        self.config_manager.set_config('password', self.pass_edit.text().strip())

    def apply_config(self):
        """应用配置"""
        # 保存UI到配置
        self.save_ui_to_config()

        # 验证配置
        is_valid, errors = self.config_manager.validate_config()

        if not is_valid:
            error_msg = "\n".join(errors)
            if self.notification:
                self.notification.show_error(f"配置验证失败:\n{errors[0]}")
            QMessageBox.warning(self, "配置验证失败", error_msg)
            logger.warning(f"配置验证失败: {error_msg}")
            return

        # 检查端口
        port = self.config_manager.get_config('port')
        available, warning = self.config_manager.check_port_available(port)
        if not available and self.notification:
            self.notification.show_warning(warning)

        # 保存配置
        if self.config_manager.save_config():
            if self.notification:
                self.notification.show_success("配置已保存")
            self.update_button_states()
        else:
            if self.notification:
                self.notification.show_error("配置保存失败")

    def start_service(self):
        """启动服务"""
        # 先应用配置
        self.save_ui_to_config()
        is_valid, errors = self.config_manager.validate_config()

        if not is_valid:
            if self.notification:
                self.notification.show_error(f"配置无效: {errors[0]}")
            return

        # 保存配置
        self.config_manager.save_config()

        # 显示启动提示
        if self.notification:
            self.notification.show_info("正在启动服务...", duration=2000)

        # 启动服务
        config = self.config_manager.get_all_config()
        success, error_msg = self.service_manager.start_service(config)

        # 延迟显示结果(等待启动提示消失)
        QTimer.singleShot(2000, lambda: self._show_start_result(success, error_msg))

    def _show_start_result(self, success, error_msg):
        """显示启动结果"""
        if success:
            if self.notification:
                self.notification.show_success("服务已启动")
            self.status_label.setText(f"状态: 服务运行中 - 端口 {self.config_manager.get_config('port')}")
            self.status_label.setStyleSheet("color: #28a745; font-size: 12px; font-weight: bold;")
        else:
            if self.notification:
                self.notification.show_error(f"服务启动失败")
            QMessageBox.critical(self, "启动失败", error_msg)

        self.update_button_states()

    def stop_service(self):
        """停止服务"""
        if self.notification:
            self.notification.show_info("正在停止服务...", duration=1500)

        success, error_msg = self.service_manager.stop_service()

        QTimer.singleShot(1500, lambda: self._show_stop_result(success, error_msg))

    def _show_stop_result(self, success, error_msg):
        """显示停止结果"""
        if success:
            if self.notification:
                self.notification.show_success("服务已停止")
            self.status_label.setText("状态: 服务未启动")
            self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        else:
            if self.notification:
                self.notification.show_error("服务停止失败")

        self.update_button_states()

    def copy_url(self):
        """复制访问URL到剪贴板"""
        if not self.service_manager.get_status():
            if self.notification:
                self.notification.show_warning("服务未启动")
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

        app = QApplication.instance()
        if app is None:  # 防止无QApplication实例的情况
            app = QApplication([])

        # 2. 获取剪贴板实例
        clipboard = app.clipboard()
        clipboard.setText(url)

        if self.notification:
            self.notification.show_success(f"已复制: {url}")

    def open_directory(self):
        """打开共享目录"""
        share_dir = self.dir_edit.text().strip()
        if not share_dir or not os.path.exists(share_dir):
            if self.notification:
                self.notification.show_warning("共享目录不存在")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(share_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', share_dir])
            else:
                subprocess.run(['xdg-open', share_dir])

            if self.notification:
                self.notification.show_success("已打开目录")
        except Exception as e:
            if self.notification:
                self.notification.show_error("打开目录失败")
            logger.error(f"打开目录失败: {e}")

    def view_log(self):
        """查看日志文件"""
        log_file = './data/webdav.log'
        if not os.path.exists(log_file):
            if self.notification:
                self.notification.show_warning("日志文件不存在")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(log_file)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_file])
            else:
                subprocess.run(['xdg-open', log_file])

            if self.notification:
                self.notification.show_success("已打开日志")
        except Exception as e:
            if self.notification:
                self.notification.show_error("打开日志失败")
            logger.error(f"打开日志失败: {e}")

    def update_button_states(self):
        """更新按钮状态"""
        is_running = self.service_manager.get_status()

        # 配置相关按钮
        self.apply_btn.setEnabled(not is_running)
        self.dir_browse_btn.setEnabled(not is_running)
        self.dir_edit.setReadOnly(is_running)
        self.port_edit.setReadOnly(is_running)
        self.user_edit.setReadOnly(is_running)
        self.pass_edit.setReadOnly(is_running)

        # 服务控制按钮
        self.start_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)

        # 辅助功能按钮
        self.copy_url_btn.setEnabled(is_running)
        share_dir = self.dir_edit.text().strip()
        self.open_dir_btn.setEnabled(bool(share_dir) and os.path.exists(share_dir))