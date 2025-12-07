# plugins/webhook_output.py
"""
Webhook Output Plugin
Send logs to external HTTP endpoints
"""

import sys
sys.path.append('..')

from plugin_manager import OutputPlugin, PluginMetadata, ConfigField, PluginType
from typing import Dict, List, Any, Optional
import time

class WebhookOutputPlugin(OutputPlugin):
    """Send logs to HTTP webhook endpoint"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Webhook",
            version="1.0.0",
            author="AI/ML Observability Platform",
            description="Send logs to any HTTP endpoint via POST requests. Supports custom headers, retry logic, and batching.",
            category=PluginType.OUTPUT,
            documentation_url="https://docs.aiml-obs.com/plugins/webhook",
            icon_url="https://cdn.aiml-obs.com/icons/webhook.png",
            tags=["webhook", "http", "api", "integration"],
            pricing="free"
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="url",
                type="string",
                label="Webhook URL",
                description="Full URL of the webhook endpoint",
                required=True,
                placeholder="https://api.example.com/webhooks/logs"
            ),
            ConfigField(
                name="method",
                type="select",
                label="HTTP Method",
                description="HTTP method to use",
                required=True,
                default="POST",
                options=["POST", "PUT", "PATCH"]
            ),
            ConfigField(
                name="auth_header",
                type="secret",
                label="Authorization Header",
                description="Value for Authorization header (e.g., 'Bearer token123')",
                required=False,
                placeholder="Bearer your-token-here"
            ),
            ConfigField(
                name="custom_headers",
                type="string",
                label="Custom Headers (JSON)",
                description='Additional headers as JSON object, e.g., {"X-Custom": "value"}',
                required=False,
                placeholder='{"X-API-Key": "value"}'
            ),
            ConfigField(
                name="batch_size",
                type="number",
                label="Batch Size",
                description="Number of logs to send in single request (1 = no batching)",
                required=False,
                default=100
            ),
            ConfigField(
                name="timeout_seconds",
                type="number",
                label="Request Timeout (seconds)",
                description="Maximum time to wait for response",
                required=False,
                default=30
            ),
            ConfigField(
                name="retry_count",
                type="number",
                label="Retry Count",
                description="Number of retries on failure",
                required=False,
                default=3
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        url = config.get('url', '')
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        batch_size = config.get('batch_size', 100)
        if batch_size < 1 or batch_size > 10000:
            return False, "Batch size must be between 1 and 10000"
        
        return True, None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.success_count = 0
        self.error_count = 0
        print(f"Webhook Output Plugin initialized for {config['url']}")
    
    def send(self, event: Dict[str, Any]) -> bool:
        """Send single event"""
        return self.send_batch([event])['success_count'] == 1
    
    def send_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send batch of events"""
        # In real implementation, make HTTP request
        # For demo, simulate success
        try:
            # Simulate HTTP request
            time.sleep(0.01)  # Simulate network latency
            
            self.success_count += len(events)
            
            return {
                'success_count': len(events),
                'failed_count': 0,
                'errors': []
            }
        except Exception as e:
            self.error_count += len(events)
            return {
                'success_count': 0,
                'failed_count': len(events),
                'errors': [str(e)]
            }
    
    def health_check(self) -> Dict[str, Any]:
        total = self.success_count + self.error_count
        success_rate = (self.success_count / total * 100) if total > 0 else 100
        
        status = "healthy" if success_rate > 95 else ("degraded" if success_rate > 50 else "unhealthy")
        
        return {
            "status": status,
            "message": f"Success rate: {success_rate:.1f}%",
            "metrics": {
                "success_count": self.success_count,
                "error_count": self.error_count,
                "success_rate": success_rate,
                "endpoint": self.config['url']
            }
        }


# plugins/slack_alert.py
"""
Slack Alert Plugin
Send alert notifications to Slack channels
"""

from plugin_manager import AlertPlugin, PluginMetadata, ConfigField, PluginType

class SlackAlertPlugin(AlertPlugin):
    """Send alerts to Slack channels"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Slack Notifications",
            version="1.0.0",
            author="AI/ML Observability Platform",
            description="Send alert notifications to Slack channels using webhooks. Supports rich formatting, mentions, and custom colors.",
            category=PluginType.ALERT,
            documentation_url="https://docs.aiml-obs.com/plugins/slack",
            icon_url="https://cdn.aiml-obs.com/icons/slack.png",
            tags=["slack", "alerts", "notifications", "chat"],
            pricing="free"
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="webhook_url",
                type="secret",
                label="Slack Webhook URL",
                description="Incoming webhook URL from Slack workspace",
                required=True,
                placeholder="https://hooks.slack.com/services/XXX/YYY/ZZZ"
            ),
            ConfigField(
                name="channel",
                type="string",
                label="Default Channel",
                description="Channel to send alerts to (optional, webhook determines default)",
                required=False,
                placeholder="#alerts"
            ),
            ConfigField(
                name="username",
                type="string",
                label="Bot Username",
                description="Display name for the bot",
                required=False,
                default="AI/ML Observability",
                placeholder="AI/ML Observability"
            ),
            ConfigField(
                name="icon_emoji",
                type="string",
                label="Bot Icon Emoji",
                description="Emoji to use as bot avatar",
                required=False,
                default=":robot_face:",
                placeholder=":robot_face:"
            ),
            ConfigField(
                name="mention_users",
                type="string",
                label="Mention Users",
                description="Comma-separated list of users to @mention on critical alerts",
                required=False,
                placeholder="@user1, @user2"
            ),
            ConfigField(
                name="severity_colors",
                type="boolean",
                label="Use Severity Colors",
                description="Color-code messages by severity (red=critical, yellow=warning, green=info)",
                required=False,
                default=True
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        webhook_url = config.get('webhook_url', '')
        if not webhook_url.startswith('https://hooks.slack.com/'):
            return False, "Invalid Slack webhook URL format"
        
        return True, None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.alerts_sent = 0
        print(f"Slack Alert Plugin initialized for {config.get('channel', 'default channel')}")
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert to Slack"""
        try:
            # In real implementation, send to Slack webhook
            # For demo, simulate success
            
            severity = alert.get('severity', 'info')
            title = alert.get('title', 'Alert')
            message = alert.get('message', '')
            
            # Build Slack message
            slack_message = {
                'username': self.config.get('username', 'AI/ML Observability'),
                'icon_emoji': self.config.get('icon_emoji', ':robot_face:'),
                'text': f"*{title}*\n{message}"
            }
            
            # Add color based on severity
            if self.config.get('severity_colors', True):
                color_map = {
                    'critical': 'danger',
                    'warning': 'warning',
                    'info': 'good'
                }
                slack_message['attachments'] = [{
                    'color': color_map.get(severity, 'good'),
                    'text': message
                }]
            
            # Add mentions for critical alerts
            if severity == 'critical' and self.config.get('mention_users'):
                mentions = self.config['mention_users']
                slack_message['text'] = f"{mentions}\n{slack_message['text']}"
            
            # Simulate sending (in real implementation, use requests.post)
            time.sleep(0.01)
            
            self.alerts_sent += 1
            return True
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "message": f"Slack alerts configured for {self.config.get('channel', 'default channel')}",
            "metrics": {
                "alerts_sent": self.alerts_sent,
                "webhook_configured": bool(self.config.get('webhook_url'))
            }
        }
