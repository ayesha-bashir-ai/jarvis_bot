import logging
import importlib
import pkgutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.config import settings

logger = logging.getLogger(__name__)

class PluginService:
    """Plugin management service"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugins_dir = Path(settings.PLUGINS_DIR)
        
        if settings.PLUGINS_ENABLED:
            self.load_plugins()
    
    def load_plugins(self):
        """Load all plugins from plugins directory"""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
        
        # Import all plugin modules
        for module_info in pkgutil.iter_modules([str(self.plugins_dir)]):
            try:
                module = importlib.import_module(f"backend.plugins.{module_info.name}")
                
                # Look for plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'is_plugin') and attr.is_plugin:
                        plugin_instance = attr()
                        self.plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Loaded plugin: {plugin_instance.name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {module_info.name}: {e}")
    
    async def execute_plugin(self, plugin_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plugin action"""
        if plugin_name not in self.plugins:
            return {
                "success": False,
                "error": f"Plugin '{plugin_name}' not found"
            }
        
        plugin = self.plugins[plugin_name]
        return await plugin.execute(action, parameters)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [
            {
                "name": plugin.name,
                "version": getattr(plugin, 'version', '1.0.0'),
                "description": getattr(plugin, 'description', '')
            }
            for plugin in self.plugins.values()
        ]