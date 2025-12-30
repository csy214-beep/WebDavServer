"""
服务管理模块
负责WebDAV服务的启动和停止
"""

import threading
import logging
from wsgidav.wsgidav_app import WsgiDAVApp
from wsgidav.fs_dav_provider import FilesystemProvider
from cheroot import wsgi

logger = logging.getLogger(__name__)


class ServiceManager:
    """WebDAV服务管理器"""

    def __init__(self):
        """初始化服务管理器"""
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.current_config = None

    def start_service(self, config):
        """
        启动WebDAV服务
        参数: config - 配置字典
        返回: (是否成功, 错误消息)
        """
        if self.is_running:
            return False, "服务已在运行中"

        try:
            logger.info("正在启动WebDAV服务...")

            # 保存配置
            self.current_config = config

            # 配置WebDAV
            provider = FilesystemProvider(config['share_dir'])

            webdav_config = {
                'provider_mapping': {'/': provider},
                'simple_dc': {
                    'user_mapping': {
                        '*': {
                            config['username']: {
                                'password': config['password'],
                                'description': 'WebDAV User',
                                'roles': []
                            }
                        }
                    }
                },
                'verbose': 1,
                'logging.enable_loggers': [],
                'property_manager': True,
                'lock_storage': True,
            }

            # 创建WSGI应用
            app = WsgiDAVApp(webdav_config)

            # 创建服务器
            self.server = wsgi.Server(
                bind_addr=('0.0.0.0', config['port']),
                wsgi_app=app,
                server_name='WebDAV-Manager'
            )

            # 在后台线程启动服务器
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()

            self.is_running = True

            logger.info(f"WebDAV服务已启动 - 端口: {config['port']}, 目录: {config['share_dir']}")
            return True, ""

        except Exception as e:
            error_msg = f"服务启动失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.is_running = False
            self.server = None
            return False, error_msg

    def _run_server(self):
        """运行服务器(在后台线程中)"""
        try:
            self.server.start()
        except Exception as e:
            logger.error(f"服务器运行异常: {e}", exc_info=True)
            self.is_running = False

    def stop_service(self):
        """
        停止WebDAV服务
        返回: (是否成功, 错误消息)
        """
        if not self.is_running:
            return False, "服务未运行"

        try:
            logger.info("正在停止WebDAV服务...")

            if self.server:
                self.server.stop()
                self.server = None

            self.is_running = False
            self.current_config = None

            logger.info("WebDAV服务已停止")
            return True, ""

        except Exception as e:
            error_msg = f"服务停止失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def get_status(self):
        """获取服务运行状态"""
        return self.is_running

    def get_access_url(self):
        """获取访问URL"""
        if self.current_config:
            port = self.current_config.get('port', 8088)
            return f"http://[您的IP地址]:{port}/"
        return ""