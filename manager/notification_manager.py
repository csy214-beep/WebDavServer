"""
通知管理模块
提供Windows风格的Toast通知
"""

from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtGui import QPalette, QColor
import logging

logger = logging.getLogger(__name__)


class ToastNotification(QLabel):
    """Toast通知组件"""

    # 通知类型配置
    TYPES = {
        'success': {'icon': '✓', 'bg': '#d4edda', 'border': '#c3e6cb', 'text': '#155724'},
        'error': {'icon': '✗', 'bg': '#f8d7da', 'border': '#f5c6cb', 'text': '#721c24'},
        'warning': {'icon': '!', 'bg': '#fff3cd', 'border': '#ffeaa7', 'text': '#856404'},
        'info': {'icon': 'i', 'bg': '#d1ecf1', 'border': '#bee5eb', 'text': '#0c5460'}
    }

    def __init__(self, parent=None):
        """初始化Toast通知"""
        super().__init__(parent)

        # 设置基本属性
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)

        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # 定时器
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.fade_out)

        # 动画
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")

        # 初始隐藏
        self.hide()

    def show_message(self, message, msg_type='info', duration=3000):
        """
        显示通知消息
        参数:
            message: 消息内容
            msg_type: 消息类型 (success/error/warning/info)
            duration: 显示时长(毫秒)
        """
        if msg_type not in self.TYPES:
            msg_type = 'info'

        config = self.TYPES[msg_type]

        # 设置样式
        style = f"""
            QLabel {{
                background-color: {config['bg']};
                border: 2px solid {config['border']};
                border-radius: 8px;
                padding: 12px 16px;
                color: {config['text']};
                font-size: 14px;
                font-weight: bold;
            }}
        """
        self.setStyleSheet(style)

        # 设置文本
        full_message = f"{config['icon']}  {message}"
        self.setText(full_message)

        # 调整大小
        self.adjustSize()

        # 重新定位(右下角)
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - 20
            y = parent_rect.height() - self.height() - 20
            self.move(x, y)

        # 停止之前的动画和定时器
        self.fade_in_animation.stop()
        self.fade_out_animation.stop()
        self.hide_timer.stop()

        # 显示并淡入
        self.show()
        self.fade_in()

        # 设置自动隐藏
        if duration > 0:
            self.hide_timer.start(duration)

        logger.info(f"Toast通知 [{msg_type}]: {message}")

    def fade_in(self):
        """淡入动画"""
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_in_animation.start()

    def fade_out(self):
        """淡出动画"""
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.hide)
        self.fade_out_animation.start()

    def mousePressEvent(self, event):
        """点击通知时立即隐藏"""
        self.hide_timer.stop()
        self.fade_out()


class NotificationManager:
    """通知管理器"""

    def __init__(self, parent_widget):
        """
        初始化通知管理器
        参数: parent_widget - 父窗口部件
        """
        self.toast = ToastNotification(parent_widget)

    def show_success(self, message, duration=3000):
        """显示成功通知"""
        self.toast.show_message(message, 'success', duration)

    def show_error(self, message, duration=3000):
        """显示错误通知"""
        self.toast.show_message(message, 'error', duration)

    def show_warning(self, message, duration=3000):
        """显示警告通知"""
        self.toast.show_message(message, 'warning', duration)

    def show_info(self, message, duration=3000):
        """显示信息通知"""
        self.toast.show_message(message, 'info', duration)