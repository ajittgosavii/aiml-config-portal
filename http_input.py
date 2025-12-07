# plugins/http_input.py
"""
HTTP Endpoint Input Plugin
Receives logs via HTTP POST requests
"""

import sys
sys.path.append('..')

from plugin_manager import InputPlugin, PluginMetadata, ConfigField, PluginType
from typing import Dict, List, Any, Optional
import time

class HTTPInputPlugin(InputPlugin):
    """HTTP endpoint for receiving logs"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="HTTP Endpoint",
            version="1.0.0",
            author="AI/ML Observability Platform",
            description="Receive logs via HTTP POST requests. Perfect for applications that can send logs directly to a REST endpoint.",
            category=PluginType.INPUT,
            documentation_url="https://docs.aiml-obs.com/plugins/http-input",
            icon_url="https://cdn.aiml-obs.com/icons/http.png",
            tags=["http", "api", "webhook", "rest"],
            pricing="free"
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="port",
                type="number",
                label="Listen Port",
                description="Port number to listen on (1024-65535)",
                required=True,
                default=8080,
                validation="^(102[4-9]|10[3-9]\\d|1[1-9]\\d{2}|[2-9]\\d{3}|[1-5]\\d{4}|6[0-4]\\d{3}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$"
            ),
            ConfigField(
                name="path",
                type="string",
                label="Endpoint Path",
                description="URL path for log ingestion",
                required=True,
                default="/logs",
                placeholder="/logs"
            ),
            ConfigField(
                name="auth_token",
                type="secret",
                label="Authentication Token",
                description="Bearer token required for requests (leave empty for no auth)",
                required=False,
                placeholder="your-secret-token-here"
            ),
            ConfigField(
                name="format",
                type="select",
                label="Expected Format",
                description="Format of incoming log data",
                required=True,
                default="json",
                options=["json", "text", "auto"]
            ),
            ConfigField(
                name="batch_size",
                type="number",
                label="Batch Size",
                description="Number of logs to collect before processing",
                required=False,
                default=100
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        # Validate port range
        port = config.get('port', 8080)
        if not (1024 <= port <= 65535):
            return False, "Port must be between 1024 and 65535"
        
        # Validate path
        path = config.get('path', '')
        if not path.startswith('/'):
            return False, "Path must start with /"
        
        # Validate batch size
        batch_size = config.get('batch_size', 100)
        if batch_size < 1 or batch_size > 10000:
            return False, "Batch size must be between 1 and 10000"
        
        return True, None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.buffer = []
        self.total_received = 0
        # In real implementation, start HTTP server here
        print(f"HTTP Input Plugin initialized on port {config['port']}, path {config['path']}")
    
    def test_connection(self) -> tuple[bool, Optional[str]]:
        # In real implementation, test if port is available
        return True, f"HTTP endpoint ready at :{self.config['port']}{self.config['path']}"
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        In real implementation, this would return logs from the buffer
        For demo, we'll simulate receiving logs
        """
        # Simulate some logs in buffer
        if len(self.buffer) < self.config.get('batch_size', 100):
            # Not enough logs yet
            return []
        
        # Return buffered logs
        events = self.buffer.copy()
        self.buffer = []
        return events
    
    def receive_log(self, data: Dict[str, Any]) -> bool:
        """Method called by HTTP server when log is received"""
        self.buffer.append({
            'timestamp': time.time(),
            'source': 'http_endpoint',
            'data': data,
            'metadata': {
                'port': self.config['port'],
                'path': self.config['path']
            }
        })
        self.total_received += 1
        return True
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "message": f"HTTP endpoint listening on :{self.config['port']}{self.config['path']}",
            "metrics": {
                "total_received": self.total_received,
                "buffer_size": len(self.buffer),
                "port": self.config['port']
            }
        }
