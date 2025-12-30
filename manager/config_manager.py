"""
配置管理模块
负责配置文件的验证、加载、保存
"""

import json
import os
import socket
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    CONFIG_FILE = './data/config.json'

    def __init__(self):
        """初始化配置管理器"""
        self.config = {
            'share_dir': '',
            'port': 8088,
            'username': '',
            'password': '',
            'last_update': ''
        }
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    logger.info("配置文件加载成功")
            else:
                logger.info("配置文件不存在,使用默认配置")
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON解析失败: {e}")
            self.reset_config()
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            self.reset_config()

    def save_config(self):
        """保存配置到文件"""
        try:
            self.config['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("配置已保存")
            return True
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            return False

    def reset_config(self):
        """重置配置为默认值"""
        self.config = {
            'share_dir': '',
            'port': 8088,
            'username': '',
            'password': '',
            'last_update': ''
        }
        logger.warning("配置已重置为默认值")

    def validate_config(self):
        """
        验证配置的有效性
        返回: (是否有效, 错误消息列表)
        """
        errors = []

        # 验证共享目录
        share_dir = self.config.get('share_dir', '').strip()
        if not share_dir:
            errors.append("共享目录不能为空")
        elif not os.path.exists(share_dir):
            errors.append(f"共享目录不存在: {share_dir}")
        elif not os.path.isdir(share_dir):
            errors.append(f"共享路径不是目录: {share_dir}")
        else:
            # 检查读写权限
            if not os.access(share_dir, os.R_OK):
                errors.append(f"共享目录无读取权限: {share_dir}")
            if not os.access(share_dir, os.W_OK):
                errors.append(f"共享目录无写入权限: {share_dir}")

        # 验证端口
        try:
            port = int(self.config.get('port', 0))
            if port < 1025 or port > 65535:
                errors.append("端口必须在 1025-65535 范围内")
        except (ValueError, TypeError):
            errors.append("端口必须是有效的数字")

        # 验证用户名
        username = self.config.get('username', '').strip()
        if not username:
            errors.append("访问账号不能为空")

        # 验证密码
        password = self.config.get('password', '').strip()
        if not password:
            errors.append("访问密码不能为空")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("配置验证通过")
        else:
            logger.warning(f"配置验证失败: {'; '.join(errors)}")

        return is_valid, errors

    def check_port_available(self, port):
        """
        检查端口是否可用
        返回: (是否可用, 警告消息)
        """
        try:
            # 尝试绑定端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:
                logger.warning(f"端口 {port} 可能已被占用")
                return False, f"端口 {port} 可能已被占用,请尝试其他端口"
            else:
                return True, ""
        except Exception as e:
            logger.error(f"端口检查失败: {e}")
            return True, ""  # 检查失败时不阻止使用

    def create_directory(self, path):
        """
        创建目录
        返回: (是否成功, 错误消息)
        """
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"目录创建成功: {path}")
            return True, ""
        except Exception as e:
            error_msg = f"目录创建失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_config(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set_config(self, key, value):
        """设置配置项"""
        self.config[key] = value

    def get_all_config(self):
        """获取所有配置"""
        return self.config.copy()