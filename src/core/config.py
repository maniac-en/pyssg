import json
import os
from typing import Dict, Any


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.getcwd(), "pyssg.config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get(self, key_path: str, default=None):
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_absolute_path(self, relative_path: str) -> str:
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(os.path.dirname(self.config_path), relative_path)
    
    @property
    def content_dir(self) -> str:
        return self.get_absolute_path(self.get('paths.content_dir', 'content'))
    
    @property
    def static_dir(self) -> str:
        return self.get_absolute_path(self.get('paths.static_dir', 'src/static'))
    
    @property
    def template_path(self) -> str:
        return self.get_absolute_path(self.get('paths.template_path', 'template.html'))
    
    @property
    def build_dir(self) -> str:
        return self.get_absolute_path(self.get('paths.build_dir', 'docs'))
    
    @property
    def base_path(self) -> str:
        return self.get('build.base_path', '/')
    
    @property
    def css_path(self) -> str:
        return self.get('build.css_path', '/index.css')
    
    @property
    def enable_hot_reload(self) -> bool:
        return self.get('server.enable_hot_reload', True)
    
    @property
    def server_port(self) -> int:
        return self.get('server.port', 8000)
    
    @property
    def project_title(self) -> str:
        return self.get('project.title', 'Static Site')