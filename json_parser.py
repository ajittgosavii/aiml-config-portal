# plugins/json_parser.py
"""
JSON Parser Processing Plugin
Parses JSON log messages and extracts fields
"""

import sys
sys.path.append('..')

from plugin_manager import ProcessingPlugin, PluginMetadata, ConfigField, PluginType
from typing import Dict, List, Any, Optional
import json

class JSONParserPlugin(ProcessingPlugin):
    """Parse JSON log messages and extract structured fields"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="JSON Parser",
            version="1.0.0",
            author="AI/ML Observability Platform",
            description="Parse JSON-formatted log messages and extract fields into structured format. Handles nested JSON and arrays.",
            category=PluginType.PROCESSING,
            documentation_url="https://docs.aiml-obs.com/plugins/json-parser",
            icon_url="https://cdn.aiml-obs.com/icons/json.png",
            tags=["parser", "json", "transform"],
            pricing="free"
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="source_field",
                type="string",
                label="Source Field",
                description="Field containing JSON string to parse (e.g., 'message', 'data')",
                required=True,
                default="message",
                placeholder="message"
            ),
            ConfigField(
                name="target_field",
                type="string",
                label="Target Field",
                description="Where to store parsed JSON (leave empty to merge into root)",
                required=False,
                default="",
                placeholder="parsed"
            ),
            ConfigField(
                name="flatten",
                type="boolean",
                label="Flatten Nested Objects",
                description="Convert nested JSON to flat structure with dot notation (e.g., user.name)",
                required=False,
                default=False
            ),
            ConfigField(
                name="prefix",
                type="string",
                label="Field Prefix",
                description="Add prefix to all extracted fields (e.g., 'json_')",
                required=False,
                default="",
                placeholder="json_"
            ),
            ConfigField(
                name="keep_original",
                type="boolean",
                label="Keep Original Field",
                description="Retain the original source field after parsing",
                required=False,
                default=True
            ),
            ConfigField(
                name="on_error",
                type="select",
                label="On Parse Error",
                description="What to do when JSON parsing fails",
                required=True,
                default="keep",
                options=["keep", "drop", "mark"]
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if not config.get('source_field'):
            return False, "Source field is required"
        
        on_error = config.get('on_error', 'keep')
        if on_error not in ['keep', 'drop', 'mark']:
            return False, "on_error must be one of: keep, drop, mark"
        
        return True, None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.parse_success = 0
        self.parse_errors = 0
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single event"""
        source_field = self.config['source_field']
        target_field = self.config.get('target_field', '')
        
        # Get source value
        if source_field not in event:
            # Source field doesn't exist, pass through
            return event
        
        source_value = event[source_field]
        
        try:
            # Parse JSON
            if isinstance(source_value, str):
                parsed = json.loads(source_value)
            elif isinstance(source_value, dict):
                parsed = source_value
            else:
                # Not a string or dict, can't parse
                return self._handle_error(event)
            
            # Flatten if requested
            if self.config.get('flatten', False):
                parsed = self._flatten_dict(parsed)
            
            # Add prefix if specified
            prefix = self.config.get('prefix', '')
            if prefix:
                parsed = {f"{prefix}{k}": v for k, v in parsed.items()}
            
            # Store result
            if target_field:
                # Store in specific field
                event[target_field] = parsed
            else:
                # Merge into root
                event.update(parsed)
            
            # Remove original field if requested
            if not self.config.get('keep_original', True):
                del event[source_field]
            
            self.parse_success += 1
            return event
            
        except json.JSONDecodeError as e:
            self.parse_errors += 1
            return self._handle_error(event, str(e))
    
    def _handle_error(self, event: Dict[str, Any], error: str = "Not valid JSON") -> Optional[Dict[str, Any]]:
        """Handle parsing error according to config"""
        on_error = self.config.get('on_error', 'keep')
        
        if on_error == 'drop':
            # Drop the event
            return None
        elif on_error == 'mark':
            # Mark as parse error
            event['_parse_error'] = error
            event['_parser'] = 'json_parser'
            return event
        else:  # 'keep'
            # Keep as-is
            return event
    
    def process_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process batch of events"""
        processed = []
        for event in events:
            result = self.process(event)
            if result is not None:
                processed.append(result)
        return processed
    
    def health_check(self) -> Dict[str, Any]:
        total = self.parse_success + self.parse_errors
        success_rate = (self.parse_success / total * 100) if total > 0 else 0
        
        status = "healthy"
        if success_rate < 50:
            status = "degraded"
        if self.parse_errors > 1000:
            status = "unhealthy"
        
        return {
            "status": status,
            "message": f"Parse success rate: {success_rate:.1f}%",
            "metrics": {
                "parse_success": self.parse_success,
                "parse_errors": self.parse_errors,
                "success_rate": success_rate
            }
        }
