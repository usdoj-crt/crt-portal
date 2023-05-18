import logging
from typing import Optional

from django.apps import AppConfig
from jupyter_client.manager import KernelManager


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def __init__(self, *args, **kwargs):
        self._kernel_manager: Optional[KernelManager] = None
        super().__init__(*args, **kwargs)

    def _get_kernel_manager(self):
        if not self._kernel_manager or not self._kernel_manager.is_alive():
            logging.warning('Starting a new Kernel Manager (existing Jupyter context will be lost).')
            self._kernel_manager = KernelManager()
        return self._kernel_manager

    @property
    def kernel_manager(self):
        return self._get_kernel_manager()

    def ready(self):
        super().ready()
