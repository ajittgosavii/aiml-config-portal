# plugin_manager.py
"""
Plugin Manager for AI/ML Observability Platform
Handles plugin registration, configuration, and execution
"""

import json
import importlib
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PluginType(Enum):
    INPUT = "input"
    PROCESSING = "processing"
    OUTPUT = "output"
    ALERT = "alert"
    ANALYTICS = "analytics"

@dataclass
class PluginMetadata:
    """Plugin metadata for marketplace"""
    name: str
    version: str
    author: str
    description: str
    category: PluginType
    documentation_url: str
    icon_url: str
    tags: List[str]
    pricing: str  # "free", "paid", "enterprise"
    
    def to_dict(self):
        data = asdict(self)
        data['category'] = self.category.value
        return data

@dataclass
class ConfigField:
    """Configuration field definition"""
    name: str
    type: str  # string, number, boolean, select, multiselect, secret
    label: str
    description: str
    required: bool = False
    default: Any = None
    options: Optional[List[str]] = None
    validation: Optional[str] = None
    placeholder: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class PluginRegistry:
    """Central registry for all plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Type] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        
    def register(self, plugin_class: Type) -> None:
        """Register a plugin class"""
        try:
            # Instantiate to get metadata
            instance = plugin_class()
            metadata = instance.metadata
            
            plugin_id = f"{metadata.category.value}:{metadata.name}"
            self.plugins[plugin_id] = plugin_class
            self.plugin_metadata[plugin_id] = metadata
            
            logger.info(f"Registered plugin: {plugin_id}")
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
    
    def get_plugin(self, plugin_id: str) -> Optional[Type]:
        """Get plugin class by ID"""
        return self.plugins.get(plugin_id)
    
    def list_plugins(self, category: Optional[PluginType] = None) -> List[Dict]:
        """List all registered plugins"""
        plugins = []
        for plugin_id, metadata in self.plugin_metadata.items():
            if category is None or metadata.category == category:
                plugin_info = metadata.to_dict()
                plugin_info['id'] = plugin_id
                plugins.append(plugin_info)
        return plugins
    
    def auto_discover(self, plugin_dir: str = "plugins") -> None:
        """Auto-discover and register plugins from directory"""
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            logger.warning(f"Plugin directory {plugin_dir} does not exist")
            return
        
        for py_file in plugin_path.glob("**/*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Import module
                module_name = str(py_file.relative_to(plugin_path).with_suffix("")).replace("/", ".")
                module = importlib.import_module(f"{plugin_dir}.{module_name}")
                
                # Find plugin classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, 'metadata') and hasattr(obj, 'config_schema'):
                        self.register(obj)
                        
            except Exception as e:
                logger.error(f"Failed to import {py_file}: {e}")

class PluginManager:
    """Manages plugin instances and execution"""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.instances: Dict[str, Any] = {}
        self.configurations: Dict[str, Dict] = {}
    
    def create_instance(self, plugin_id: str, instance_id: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Create and configure a plugin instance
        Returns: (success, error_message)
        """
        try:
            # Get plugin class
            plugin_class = self.registry.get_plugin(plugin_id)
            if not plugin_class:
                return False, f"Plugin {plugin_id} not found"
            
            # Create instance
            instance = plugin_class()
            
            # Validate configuration
            is_valid, error = instance.validate_config(config)
            if not is_valid:
                return False, error
            
            # Initialize plugin
            instance.initialize(config)
            
            # Store instance and config
            self.instances[instance_id] = instance
            self.configurations[instance_id] = config
            
            logger.info(f"Created plugin instance: {instance_id} ({plugin_id})")
            return True, None
            
        except Exception as e:
            logger.error(f"Failed to create plugin instance {instance_id}: {e}")
            return False, str(e)
    
    def get_instance(self, instance_id: str) -> Optional[Any]:
        """Get plugin instance by ID"""
        return self.instances.get(instance_id)
    
    def remove_instance(self, instance_id: str) -> bool:
        """Remove plugin instance"""
        if instance_id in self.instances:
            del self.instances[instance_id]
            del self.configurations[instance_id]
            logger.info(f"Removed plugin instance: {instance_id}")
            return True
        return False
    
    def health_check(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Check health of plugin instance"""
        instance = self.get_instance(instance_id)
        if instance:
            return instance.health_check()
        return None
    
    def list_instances(self) -> List[Dict[str, Any]]:
        """List all plugin instances"""
        instances = []
        for instance_id, instance in self.instances.items():
            metadata = instance.metadata
            health = instance.health_check()
            
            instances.append({
                'instance_id': instance_id,
                'plugin_name': metadata.name,
                'plugin_category': metadata.category.value,
                'status': health.get('status'),
                'config': self.configurations[instance_id]
            })
        return instances

class Pipeline:
    """Data processing pipeline"""
    
    def __init__(self, name: str, plugin_manager: PluginManager):
        self.name = name
        self.plugin_manager = plugin_manager
        self.input_instances: List[str] = []
        self.processing_instances: List[str] = []
        self.output_instances: List[str] = []
        self.enabled = True
    
    def add_input(self, instance_id: str) -> None:
        """Add input plugin to pipeline"""
        self.input_instances.append(instance_id)
    
    def add_processor(self, instance_id: str) -> None:
        """Add processing plugin to pipeline"""
        self.processing_instances.append(instance_id)
    
    def add_output(self, instance_id: str) -> None:
        """Add output plugin to pipeline"""
        self.output_instances.append(instance_id)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute pipeline once
        Returns: Execution statistics
        """
        stats = {
            'events_collected': 0,
            'events_processed': 0,
            'events_sent': 0,
            'errors': []
        }
        
        if not self.enabled:
            return stats
        
        try:
            # Collect from all inputs
            all_events = []
            for input_id in self.input_instances:
                input_plugin = self.plugin_manager.get_instance(input_id)
                if input_plugin:
                    events = input_plugin.collect()
                    all_events.extend(events)
                    stats['events_collected'] += len(events)
            
            # Process events
            processed_events = all_events
            for processor_id in self.processing_instances:
                processor = self.plugin_manager.get_instance(processor_id)
                if processor:
                    processed_events = processor.process_batch(processed_events)
            
            stats['events_processed'] = len(processed_events)
            
            # Send to outputs
            for output_id in self.output_instances:
                output_plugin = self.plugin_manager.get_instance(output_id)
                if output_plugin:
                    result = output_plugin.send_batch(processed_events)
                    stats['events_sent'] += result.get('success_count', 0)
                    if result.get('errors'):
                        stats['errors'].extend(result['errors'])
            
        except Exception as e:
            logger.error(f"Pipeline {self.name} execution failed: {e}")
            stats['errors'].append(str(e))
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Export pipeline configuration"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'inputs': self.input_instances,
            'processors': self.processing_instances,
            'outputs': self.output_instances
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], plugin_manager: PluginManager) -> 'Pipeline':
        """Import pipeline from configuration"""
        pipeline = cls(data['name'], plugin_manager)
        pipeline.enabled = data.get('enabled', True)
        pipeline.input_instances = data.get('inputs', [])
        pipeline.processing_instances = data.get('processors', [])
        pipeline.output_instances = data.get('outputs', [])
        return pipeline

# Global registry instance
plugin_registry = PluginRegistry()
