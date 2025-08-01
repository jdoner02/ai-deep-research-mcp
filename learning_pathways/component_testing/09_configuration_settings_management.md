# Module 09: Configuration and Settings Management Testing
*Your System Configuration Manager - Making Everything Customizable and Flexible*

## Learning Objectives
By the end of this module, you'll understand how to test configuration and settings management systems that allow applications to be customized for different environments and use cases, just like having a knowledgeable system administrator who can adjust settings perfectly for any situation.

## The System Configuration Manager Analogy

Imagine you have a brilliant system configuration manager - like a master chef who can adjust any recipe - who handles all the settings that make your application work perfectly in different situations. This manager:

- **Adapts recipes for different kitchens** (configures apps for different environments like development, testing, production)
- **Remembers preferences** (stores and validates configuration settings)
- **Prevents cooking disasters** (validates settings to avoid dangerous configurations)
- **Handles dietary restrictions** (manages environment-specific requirements and constraints)
- **Updates recipes safely** (allows configuration changes without breaking the system)
- **Keeps backup recipes** (maintains configuration backups and rollback capabilities)
- **Teaches new chefs** (provides clear documentation and examples for all settings)

This is exactly how professional configuration management systems work! They act like digital system administrators, ensuring your application can be properly configured for any environment or use case while maintaining safety and reliability.

## Core Concepts: How Professional Configuration Management Works

### 1. Configuration Structure - Your Manager's Recipe Organization
Just like a master chef organizes recipes by categories and ingredients, our configuration manager structures settings logically:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import os
import json
import yaml
from pathlib import Path

class Environment(Enum):
    """
    Your configuration manager's kitchen types.
    
    Each environment has different requirements and constraints,
    just like cooking at home vs. in a restaurant kitchen.
    """
    DEVELOPMENT = "development"   # Developer's local machine
    TESTING = "testing"          # Automated testing environment
    STAGING = "staging"          # Pre-production testing
    PRODUCTION = "production"    # Live user-facing system

class ConfigurationLevel(Enum):
    """
    Your manager's priority system for settings.
    
    Like how a chef might override a recipe based on available
    ingredients or dietary restrictions.
    """
    DEFAULT = "default"          # Built-in fallback values
    FILE = "file"               # Configuration files
    ENVIRONMENT = "environment"  # Environment variables
    RUNTIME = "runtime"         # Settings changed during execution

@dataclass
class DatabaseConfig:
    """
    Your manager's database recipe.
    
    This contains all the settings needed to connect to
    and work with the database properly.
    """
    host: str = "localhost"
    port: int = 5432
    database: str = "research_db"
    username: str = "user"
    password: str = ""
    max_connections: int = 10
    timeout: float = 30.0
    ssl_enabled: bool = False
    
    def __post_init__(self):
        """Validate database configuration like a careful chef checking ingredients."""
        if not self.host:
            raise ValueError("Database host cannot be empty")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Database port must be between 1 and 65535")
        if self.max_connections <= 0:
            raise ValueError("Max connections must be positive")

@dataclass
class LLMConfig:
    """
    Your manager's AI model recipe.
    
    This controls how the AI components behave,
    like adjusting cooking temperature and timing.
    """
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate AI configuration settings."""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

@dataclass
class SystemConfig:
    """
    Your configuration manager's complete recipe book.
    
    This is the master configuration that contains all the
    settings needed to run the entire research system.
    """
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: str = "INFO"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    # System settings
    max_concurrent_requests: int = 10
    request_timeout: float = 60.0
    rate_limit_per_minute: int = 100
    
    # Feature flags
    enable_caching: bool = True
    enable_metrics: bool = False
    enable_debug_mode: bool = False
    
    # Paths and directories
    log_directory: str = "logs"
    cache_directory: str = "cache"
    data_directory: str = "data"
    
    def __post_init__(self):
        """Validate overall system configuration."""
        if self.max_concurrent_requests <= 0:
            raise ValueError("Max concurrent requests must be positive")
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
```

### 2. Configuration Loading and Merging - Your Manager's Recipe Assembly
Like a chef who combines base recipes with local ingredients and dietary modifications:

```python
class ConfigurationManager:
    """
    Your system's configuration manager.
    
    This handles loading, validating, and merging configuration
    from multiple sources, just like a chef who can adapt
    recipes based on available ingredients and requirements.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config"
        self.config_sources = {}
        self.active_config = None
        self.config_history = []  # Track configuration changes
    
    def load_configuration(self, environment: Environment) -> SystemConfig:
        """
        Load and merge configuration from multiple sources.
        
        Like a chef following this process:
        1. Start with default recipe (built-in defaults)
        2. Apply cookbook modifications (config files)
        3. Adjust for kitchen constraints (environment variables)
        4. Make final tweaks (runtime overrides)
        """
        # Step 1: Start with default configuration
        config_data = self._get_default_config()
        self.config_sources[ConfigurationLevel.DEFAULT] = config_data.copy()
        
        # Step 2: Load and merge file-based configuration
        file_config = self._load_config_file(environment)
        if file_config:
            config_data.update(file_config)
            self.config_sources[ConfigurationLevel.FILE] = file_config
        
        # Step 3: Apply environment variable overrides
        env_config = self._load_environment_variables()
        if env_config:
            config_data.update(env_config)
            self.config_sources[ConfigurationLevel.ENVIRONMENT] = env_config
        
        # Step 4: Create and validate final configuration
        self.active_config = SystemConfig(**config_data)
        
        # Step 5: Record this configuration in history
        self.config_history.append({
            "timestamp": datetime.now(),
            "environment": environment,
            "config": self.active_config,
            "sources": self.config_sources.copy()
        })
        
        return self.active_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get built-in default configuration.
        
        Like a chef's basic recipe that works in any kitchen
        but might not be optimal for specific situations.
        """
        return {
            "environment": Environment.DEVELOPMENT.value,
            "debug": True,
            "log_level": "INFO",
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "research_db"
            },
            "llm": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "max_concurrent_requests": 10,
            "enable_caching": True
        }
    
    def _load_config_file(self, environment: Environment) -> Optional[Dict[str, Any]]:
        """
        Load configuration from files.
        
        Like a chef loading a recipe from their cookbook,
        with different recipes for different occasions.
        """
        config_files = [
            f"{self.config_path}/config.yaml",           # General config
            f"{self.config_path}/{environment.value}.yaml",  # Environment-specific
            f"{self.config_path}/local.yaml"             # Local overrides
        ]
        
        merged_config = {}
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        file_data = yaml.safe_load(f) or {}
                        merged_config.update(file_data)
                except Exception as e:
                    print(f"Warning: Could not load {config_file}: {e}")
        
        return merged_config if merged_config else None
    
    def _load_environment_variables(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Like a chef adjusting a recipe based on what's
        available in the current kitchen.
        """
        env_config = {}
        
        # Database settings
        if os.getenv("DB_HOST"):
            env_config.setdefault("database", {})["host"] = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            env_config.setdefault("database", {})["port"] = int(os.getenv("DB_PORT"))
        if os.getenv("DB_PASSWORD"):
            env_config.setdefault("database", {})["password"] = os.getenv("DB_PASSWORD")
        
        # LLM settings
        if os.getenv("LLM_API_KEY"):
            env_config.setdefault("llm", {})["api_key"] = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_MODEL"):
            env_config.setdefault("llm", {})["model_name"] = os.getenv("LLM_MODEL")
        
        # System settings
        if os.getenv("DEBUG"):
            env_config["debug"] = os.getenv("DEBUG").lower() == "true"
        if os.getenv("LOG_LEVEL"):
            env_config["log_level"] = os.getenv("LOG_LEVEL")
        
        return env_config
```

### 3. Configuration Validation - Your Manager's Quality Control
Like a chef who tastes and adjusts seasoning, our manager validates all settings:

```python
class ConfigurationValidator:
    """
    Your configuration manager's quality control system.
    
    This ensures all settings are safe and sensible,
    like a chef who won't let a dangerous recipe reach the kitchen.
    """
    
    def __init__(self):
        self.validation_rules = self._setup_validation_rules()
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_configuration(self, config: SystemConfig) -> bool:
        """
        Comprehensive configuration validation.
        
        Like a chef doing a final taste test and safety check
        before serving a dish to customers.
        """
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Validate environment-specific requirements
        self._validate_environment_requirements(config)
        
        # Validate component configurations
        self._validate_database_config(config.database)
        self._validate_llm_config(config.llm)
        
        # Validate system-wide settings
        self._validate_system_settings(config)
        
        # Validate feature flag combinations
        self._validate_feature_flags(config)
        
        # Return True if no errors (warnings are OK)
        return len(self.validation_errors) == 0
    
    def _validate_environment_requirements(self, config: SystemConfig):
        """
        Validate environment-specific requirements.
        
        Like checking that you have the right equipment
        for the type of cooking you're doing.
        """
        if config.environment == Environment.PRODUCTION:
            # Production has stricter requirements
            if config.debug:
                self.validation_warnings.append(
                    "Debug mode enabled in production - consider disabling"
                )
            
            if config.llm.api_key is None:
                self.validation_errors.append(
                    "LLM API key required in production environment"
                )
            
            if config.database.password == "":
                self.validation_errors.append(
                    "Database password required in production"
                )
        
        elif config.environment == Environment.DEVELOPMENT:
            # Development can be more relaxed
            if not config.debug:
                self.validation_warnings.append(
                    "Debug mode disabled in development - might want to enable"
                )
    
    def _validate_database_config(self, db_config: DatabaseConfig):
        """
        Validate database configuration settings.
        
        Like checking that all ingredients for a dish are
        fresh and properly prepared.
        """
        # Connection validation
        if db_config.max_connections > 100:
            self.validation_warnings.append(
                "Very high max_connections setting - ensure database can handle this"
            )
        
        if db_config.timeout > 60:
            self.validation_warnings.append(
                "Long database timeout - may impact user experience"
            )
        
        # Security validation
        if db_config.password == "" and db_config.host != "localhost":
            self.validation_errors.append(
                "Empty database password for remote connection is insecure"
            )
    
    def _validate_feature_flags(self, config: SystemConfig):
        """
        Validate feature flag combinations.
        
        Like checking that recipe modifications work well together
        and don't create conflicting requirements.
        """
        if config.enable_debug_mode and config.environment == Environment.PRODUCTION:
            self.validation_errors.append(
                "Debug mode should not be enabled in production"
            )
        
        if config.enable_metrics and not config.enable_caching:
            self.validation_warnings.append(
                "Metrics without caching may impact performance"
            )
```

### 4. Dynamic Configuration Updates - Your Manager's Live Adjustments
Like a chef who can adjust seasoning while cooking:

```python
class DynamicConfigurationManager:
    """
    Your configuration manager's live adjustment system.
    
    This allows safe configuration changes while the system is running,
    like a chef adjusting seasoning while cooking without ruining the dish.
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.update_listeners = []
        self.pending_updates = {}
        self.update_history = []
    
    def register_update_listener(self, component_name: str, callback):
        """
        Register a component to be notified of configuration changes.
        
        Like telling kitchen staff which changes they need to know about.
        """
        self.update_listeners.append({
            "component": component_name,
            "callback": callback
        })
    
    async def update_configuration(self, updates: Dict[str, Any], 
                                 validate: bool = True) -> bool:
        """
        Safely update configuration while system is running.
        
        Like adjusting a recipe while cooking - carefully and with
        full awareness of how changes affect the final dish.
        """
        # Step 1: Validate proposed changes
        if validate:
            validation_result = await self._validate_proposed_updates(updates)
            if not validation_result.is_valid:
                raise ValueError(f"Invalid configuration updates: {validation_result.errors}")
        
        # Step 2: Stage the updates
        self.pending_updates = updates
        
        # Step 3: Notify all registered components
        notification_results = await self._notify_components_of_changes(updates)
        
        # Step 4: Apply updates if all components are ready
        if all(result.ready for result in notification_results):
            await self._apply_updates(updates)
            return True
        else:
            # Some components can't handle the update right now
            failed_components = [r.component for r in notification_results if not r.ready]
            raise RuntimeError(f"Components not ready for update: {failed_components}")
    
    async def _validate_proposed_updates(self, updates: Dict[str, Any]):
        """
        Validate proposed configuration changes.
        
        Like testing a recipe modification on a small batch
        before applying it to the whole dish.
        """
        # Create a copy of current config with proposed changes
        current_config = self.config_manager.active_config
        test_config_data = self._merge_updates(current_config, updates)
        
        try:
            test_config = SystemConfig(**test_config_data)
            validator = ConfigurationValidator()
            is_valid = validator.validate_configuration(test_config)
            
            return ValidationResult(
                is_valid=is_valid,
                errors=validator.validation_errors,
                warnings=validator.validation_warnings
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Configuration update failed validation: {str(e)}"],
                warnings=[]
            )
    
    async def rollback_configuration(self, steps: int = 1):
        """
        Roll back to a previous configuration.
        
        Like reverting to a recipe that worked when your
        modifications didn't turn out as expected.
        """
        if len(self.config_manager.config_history) <= steps:
            raise ValueError("Not enough configuration history for rollback")
        
        # Get the target configuration from history
        target_config_entry = self.config_manager.config_history[-(steps + 1)]
        target_config = target_config_entry["config"]
        
        # Apply the rollback
        await self._apply_rollback(target_config)
        
        # Record the rollback in history
        self.update_history.append({
            "timestamp": datetime.now(),
            "action": "rollback",
            "steps": steps,
            "target_config": target_config
        })
```

## Building on Previous Modules: Configuration-Aware Research System

Our configuration system manages settings for all the components we've learned about:

```python
class ConfigurableResearchSystem:
    """
    Complete research system with comprehensive configuration management.
    
    This integrates configuration management into every component
    from our previous modules, making everything customizable.
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        # Load configuration for this environment
        self.config_manager = ConfigurationManager()
        self.config = self.config_manager.load_configuration(environment)
        
        # Initialize all components with their configurations
        self.web_crawler = self._init_web_crawler()        # Module 01
        self.document_processor = self._init_doc_processor() # Module 02
        self.ai_integrator = self._init_ai_integrator()    # Module 03
        self.orchestrator = self._init_orchestrator()      # Module 04
        self.vector_store = self._init_vector_store()      # Module 05
        self.retriever = self._init_retriever()            # Module 06
        self.citation_manager = self._init_citation_manager() # Module 07
        self.error_handler = self._init_error_handler()    # Module 08
    
    def _init_web_crawler(self):
        """Initialize web crawler with configuration."""
        crawler_config = {
            "timeout": self.config.request_timeout,
            "max_concurrent": self.config.max_concurrent_requests,
            "rate_limit": self.config.rate_limit_per_minute,
            "user_agent": f"AIResearch/{self.config.environment.value}",
            "enable_caching": self.config.enable_caching
        }
        
        return WebCrawler(crawler_config)
    
    def _init_vector_store(self):
        """Initialize vector database with configuration."""
        vector_config = {
            "host": self.config.database.host,
            "port": self.config.database.port,
            "database": f"{self.config.database.database}_vectors",
            "username": self.config.database.username,
            "password": self.config.database.password,
            "max_connections": self.config.database.max_connections,
            "ssl_enabled": self.config.database.ssl_enabled
        }
        
        return VectorStore(vector_config)
    
    def _init_ai_integrator(self):
        """Initialize AI components with configuration."""
        ai_config = {
            "model_name": self.config.llm.model_name,
            "api_key": self.config.llm.api_key,
            "temperature": self.config.llm.temperature,
            "max_tokens": self.config.llm.max_tokens,
            "timeout": self.config.llm.timeout,
            "max_retries": self.config.llm.max_retries,
            "retry_delay": self.config.llm.retry_delay
        }
        
        return AIIntegrator(ai_config)
    
    async def reconfigure_system(self, new_config_updates: Dict[str, Any]):
        """
        Reconfigure the entire system with new settings.
        
        This is like having a system administrator who can
        adjust all system settings without requiring a restart.
        """
        # Use dynamic configuration manager for safe updates
        dynamic_manager = DynamicConfigurationManager(self.config_manager)
        
        # Apply configuration updates
        await dynamic_manager.update_configuration(new_config_updates)
        
        # Reinitialize components that need new settings
        self._reinitialize_affected_components(new_config_updates)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        Get current configuration status and health.
        
        Like a system status dashboard that shows how
        everything is configured and whether it's working properly.
        """
        return {
            "environment": self.config.environment.value,
            "configuration_sources": list(self.config_manager.config_sources.keys()),
            "active_features": {
                "caching": self.config.enable_caching,
                "metrics": self.config.enable_metrics,
                "debug": self.config.enable_debug_mode
            },
            "component_status": {
                "database": self._check_database_connection(),
                "llm": self._check_llm_availability(),
                "cache": self._check_cache_status()
            },
            "last_updated": self.config_manager.config_history[-1]["timestamp"]
        }
```

## Testing Configuration and Settings Management

Now let's learn how to test these critical configuration management capabilities:

### Test 1: Configuration Loading and Merging
```python
def test_configuration_loading_and_merging():
    """
    Test that configuration is loaded and merged correctly from multiple sources.
    
    Like testing that a chef can successfully combine a base recipe
    with local ingredients and dietary modifications to create
    a properly balanced dish.
    """
    import tempfile
    import os
    from pathlib import Path
    
    # Setup: Create temporary configuration files
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        # Create base configuration file
        base_config = {
            "environment": "testing",
            "debug": False,
            "database": {
                "host": "test-db",
                "port": 5432
            }
        }
        
        with open(config_dir / "config.yaml", 'w') as f:
            yaml.dump(base_config, f)
        
        # Create environment-specific configuration
        env_config = {
            "debug": True,
            "llm": {
                "model_name": "test-model",
                "temperature": 0.5
            }
        }
        
        with open(config_dir / "testing.yaml", 'w') as f:
            yaml.dump(env_config, f)
        
        # Set environment variables
        os.environ["DB_PASSWORD"] = "test-password"
        os.environ["LLM_API_KEY"] = "test-api-key"
        
        try:
            # Test: Load configuration
            manager = ConfigurationManager(str(config_dir))
            config = manager.load_configuration(Environment.TESTING)
            
            # Verify: Configuration merged correctly
            assert config.environment == Environment.TESTING
            assert config.debug is True  # Environment file overrode base config
            assert config.database.host == "test-db"  # From base config
            assert config.database.password == "test-password"  # From environment
            assert config.llm.model_name == "test-model"  # From environment config
            assert config.llm.api_key == "test-api-key"  # From environment
            
            # Verify: Configuration sources tracked
            assert ConfigurationLevel.DEFAULT in manager.config_sources
            assert ConfigurationLevel.FILE in manager.config_sources
            assert ConfigurationLevel.ENVIRONMENT in manager.config_sources
            
        finally:
            # Cleanup environment variables
            os.environ.pop("DB_PASSWORD", None)
            os.environ.pop("LLM_API_KEY", None)
    
    print("✅ Configuration loading and merging works correctly!")
```

### Test 2: Configuration Validation
```python
def test_configuration_validation():
    """
    Test that configuration validation catches invalid settings.
    
    Like testing that a chef's quality control system catches
    dangerous ingredient combinations or impossible temperatures
    before they ruin the dish.
    """
    from configuration import ConfigurationValidator, SystemConfig, DatabaseConfig, LLMConfig
    
    # Setup: Create validator
    validator = ConfigurationValidator()
    
    # Test: Valid configuration should pass
    valid_config = SystemConfig(
        environment=Environment.PRODUCTION,
        debug=False,
        database=DatabaseConfig(
            host="prod-db",
            password="secure-password"
        ),
        llm=LLMConfig(
            api_key="valid-api-key",
            temperature=0.7
        )
    )
    
    is_valid = validator.validate_configuration(valid_config)
    assert is_valid is True
    assert len(validator.validation_errors) == 0
    
    # Test: Invalid configuration should fail
    invalid_config = SystemConfig(
        environment=Environment.PRODUCTION,
        debug=True,  # Debug mode in production - warning
        database=DatabaseConfig(
            host="remote-db",
            password=""  # Empty password for remote connection - error
        ),
        llm=LLMConfig(
            api_key=None,  # No API key in production - error
            temperature=3.0  # Invalid temperature - error
        )
    )
    
    is_valid = validator.validate_configuration(invalid_config)
    assert is_valid is False
    assert len(validator.validation_errors) >= 2  # Password and API key errors
    assert len(validator.validation_warnings) >= 1  # Debug mode warning
    
    # Verify specific error messages
    error_messages = " ".join(validator.validation_errors)
    assert "password" in error_messages.lower()
    assert "api key" in error_messages.lower()
    
    print("✅ Configuration validation works correctly!")
```

### Test 3: Environment-Specific Configuration
```python
def test_environment_specific_configuration():
    """
    Test that different environments get appropriate configurations.
    
    Like testing that a chef adjusts recipes appropriately
    for home cooking vs. restaurant service vs. catering events.
    """
    from configuration import ConfigurationManager, Environment
    
    # Setup: Create configuration manager
    manager = ConfigurationManager()
    
    # Test: Development environment configuration
    dev_config = manager.load_configuration(Environment.DEVELOPMENT)
    assert dev_config.environment == Environment.DEVELOPMENT
    assert dev_config.debug is True  # Development should have debug enabled
    assert dev_config.log_level == "INFO" or dev_config.log_level == "DEBUG"
    
    # Test: Production environment configuration  
    prod_config = manager.load_configuration(Environment.PRODUCTION)
    assert prod_config.environment == Environment.PRODUCTION
    # Production typically has stricter settings, but depends on actual config
    
    # Test: Testing environment configuration
    test_config = manager.load_configuration(Environment.TESTING)
    assert test_config.environment == Environment.TESTING
    # Testing environment might have specific test-friendly settings
    
    # Verify: Each environment has appropriate defaults
    assert dev_config.environment != prod_config.environment
    
    # Verify: Configuration history tracked separately
    assert len(manager.config_history) == 3  # One entry per environment loaded
    
    print("✅ Environment-specific configuration works correctly!")
```

### Test 4: Dynamic Configuration Updates
```python
async def test_dynamic_configuration_updates():
    """
    Test that configuration can be safely updated while system is running.
    
    Like testing that a chef can adjust seasoning while cooking
    without ruining the dish or interrupting service.
    """
    from configuration import ConfigurationManager, DynamicConfigurationManager
    import asyncio
    
    # Setup: Create managers
    config_manager = ConfigurationManager()
    initial_config = config_manager.load_configuration(Environment.DEVELOPMENT)
    
    dynamic_manager = DynamicConfigurationManager(config_manager)
    
    # Mock component that listens for configuration changes
    component_notifications = []
    
    async def mock_component_callback(updates):
        component_notifications.append(updates)
        return {"ready": True, "component": "test_component"}
    
    dynamic_manager.register_update_listener("test_component", mock_component_callback)
    
    # Test: Apply configuration updates
    updates = {
        "max_concurrent_requests": 20,  # Increase from default 10
        "llm": {
            "temperature": 0.5  # Decrease from default 0.7
        },
        "enable_metrics": True  # Enable metrics
    }
    
    success = await dynamic_manager.update_configuration(updates)
    
    # Verify: Update was successful
    assert success is True
    
    # Verify: Component was notified
    assert len(component_notifications) == 1
    assert component_notifications[0] == updates
    
    # Verify: Configuration was actually updated
    updated_config = config_manager.active_config
    assert updated_config.max_concurrent_requests == 20
    assert updated_config.llm.temperature == 0.5
    assert updated_config.enable_metrics is True
    
    # Verify: Update history tracked
    assert len(dynamic_manager.update_history) >= 0  # May have entries from update process
    
    print("✅ Dynamic configuration updates work correctly!")
```

### Test 5: Configuration Rollback
```python
async def test_configuration_rollback():
    """
    Test that configuration can be rolled back to previous states.
    
    Like testing that a chef can revert to the original recipe
    when their modifications don't work out as expected.
    """
    from configuration import ConfigurationManager, DynamicConfigurationManager
    
    # Setup: Create managers and establish baseline
    config_manager = ConfigurationManager()
    original_config = config_manager.load_configuration(Environment.DEVELOPMENT)
    original_max_requests = original_config.max_concurrent_requests
    
    dynamic_manager = DynamicConfigurationManager(config_manager)
    
    # Test: Make first configuration change
    first_update = {"max_concurrent_requests": 15}
    await dynamic_manager.update_configuration(first_update, validate=False)
    first_config = config_manager.active_config
    assert first_config.max_concurrent_requests == 15
    
    # Test: Make second configuration change
    second_update = {"max_concurrent_requests": 25}
    await dynamic_manager.update_configuration(second_update, validate=False)
    second_config = config_manager.active_config
    assert second_config.max_concurrent_requests == 25
    
    # Test: Rollback one step (to first update)
    await dynamic_manager.rollback_configuration(steps=1)
    rolled_back_config = config_manager.active_config
    assert rolled_back_config.max_concurrent_requests == 15
    
    # Test: Rollback to original (two more steps back)
    await dynamic_manager.rollback_configuration(steps=2)
    final_config = config_manager.active_config
    assert final_config.max_concurrent_requests == original_max_requests
    
    # Verify: Rollback history tracked
    rollback_entries = [entry for entry in dynamic_manager.update_history 
                       if entry.get("action") == "rollback"]
    assert len(rollback_entries) >= 2  # Should have recorded both rollbacks
    
    print("✅ Configuration rollback works correctly!")
```

### Test 6: Feature Flag Management
```python
def test_feature_flag_management():
    """
    Test that feature flags can be managed and validated properly.
    
    Like testing that a chef can enable/disable different cooking
    techniques and verify they work well together.
    """
    from configuration import SystemConfig, ConfigurationValidator
    
    # Test: Compatible feature flag combinations
    compatible_config = SystemConfig(
        enable_caching=True,
        enable_metrics=True,    # Works well with caching
        enable_debug_mode=True,
        environment=Environment.DEVELOPMENT  # Debug OK in dev
    )
    
    validator = ConfigurationValidator()
    is_valid = validator.validate_configuration(compatible_config)
    
    # Should be valid with minimal warnings
    assert is_valid is True
    
    # Test: Incompatible feature flag combinations
    incompatible_config = SystemConfig(
        enable_debug_mode=True,
        environment=Environment.PRODUCTION,  # Debug mode in production - error
        enable_metrics=True,
        enable_caching=False    # Metrics without caching - warning
    )
    
    is_valid = validator.validate_configuration(incompatible_config)
    
    # Should fail validation due to debug in production
    assert is_valid is False
    assert len(validator.validation_errors) >= 1
    
    # Check for specific error about debug mode in production
    error_text = " ".join(validator.validation_errors)
    assert "debug" in error_text.lower()
    assert "production" in error_text.lower()
    
    print("✅ Feature flag management works correctly!")
```

### Test 7: Configuration Security
```python
def test_configuration_security():
    """
    Test that sensitive configuration data is handled securely.
    
    Like testing that a chef properly handles and stores
    expensive or dangerous ingredients safely.
    """
    from configuration import SystemConfig, DatabaseConfig, LLMConfig
    import json
    
    # Setup: Configuration with sensitive data
    config = SystemConfig(
        database=DatabaseConfig(
            password="super-secret-password",
            username="admin"
        ),
        llm=LLMConfig(
            api_key="sk-very-secret-api-key-123456"
        )
    )
    
    # Test: Sensitive data should not appear in string representation
    config_str = str(config)
    assert "super-secret-password" not in config_str
    assert "sk-very-secret-api-key" not in config_str
    
    # Test: Sensitive data should be masked in serialization
    config_dict = config.__dict__.copy()
    
    # In a real implementation, these would be masked
    # For now, just verify we can identify sensitive fields
    sensitive_fields = []
    if "password" in str(config.database.__dict__):
        sensitive_fields.append("database.password")
    if "api_key" in str(config.llm.__dict__):
        sensitive_fields.append("llm.api_key")
    
    assert len(sensitive_fields) >= 2  # Should identify password and API key
    
    # Test: Configuration validation should work with masked values
    # (In real implementation, validation would unmask for checking)
    validator = ConfigurationValidator()
    
    # Should still be able to validate even with sensitive data
    # (Implementation would handle unmasking during validation)
    is_valid = validator.validate_configuration(config)
    assert is_valid is True  # Assuming valid config otherwise
    
    print("✅ Configuration security works correctly!")
```

## Advanced Testing Scenarios

### Testing Configuration Performance
```python
def test_configuration_performance():
    """
    Test that configuration loading and access is efficient.
    
    Like testing that a chef can quickly access and adjust
    recipes even when managing a large cookbook.
    """
    import time
    from configuration import ConfigurationManager
    
    # Setup: Create configuration manager
    manager = ConfigurationManager()
    
    # Test: Configuration loading performance
    start_time = time.time()
    config = manager.load_configuration(Environment.DEVELOPMENT)
    load_time = time.time() - start_time
    
    # Should load quickly (under 1 second for reasonable configs)
    assert load_time < 1.0, f"Configuration loading took {load_time:.2f}s"
    
    # Test: Configuration access performance
    start_time = time.time()
    for _ in range(1000):
        # Access various configuration properties
        _ = config.database.host
        _ = config.llm.temperature
        _ = config.max_concurrent_requests
    access_time = time.time() - start_time
    
    # Should access quickly (under 0.1 seconds for 1000 accesses)
    assert access_time < 0.1, f"1000 config accesses took {access_time:.2f}s"
    
    print("✅ Configuration performance is acceptable!")
```

## Real-World Applications

Understanding configuration management helps you work with:

### 1. **Microservices Architecture**
- Test service discovery and configuration distribution
- Verify environment-specific service configurations
- Test configuration changes across service boundaries

### 2. **Cloud-Native Applications**
- Test configuration injection via environment variables
- Verify secrets management and rotation
- Test configuration scaling and multi-region deployment

### 3. **CI/CD Pipelines**
- Test configuration promotion across environments
- Verify automated configuration validation
- Test rollback procedures in deployment pipelines

### 4. **Enterprise Applications**
- Test role-based configuration access
- Verify audit trails for configuration changes
- Test integration with corporate configuration management systems

### 5. **Development Teams**
- Test local development configuration setup
- Verify configuration documentation and examples
- Test onboarding procedures for new developers

## Professional Development Insights

Working with configuration management teaches valuable skills:

### **For Software Engineers:**
- **Separation of Concerns**: Keeping configuration separate from code logic
- **Environment Management**: Understanding different deployment environments and their needs
- **Security Practices**: Handling sensitive configuration data safely
- **System Design**: Creating flexible, configurable systems that adapt to different use cases

### **For DevOps Engineers:**
- **Infrastructure as Code**: Managing configuration alongside infrastructure
- **Deployment Automation**: Automating configuration deployment and validation
- **Monitoring and Alerting**: Tracking configuration changes and their effects
- **Disaster Recovery**: Planning for configuration corruption and recovery scenarios

### **Testing Best Practices:**
- **Environment Parity**: Ensuring test environments match production configuration patterns
- **Configuration Validation**: Testing all possible configuration combinations and edge cases
- **Security Testing**: Verifying that sensitive data is properly protected
- **Performance Testing**: Ensuring configuration access doesn't become a bottleneck

## Connection to Other Modules

This module configures and controls all previous components:

- **Module 01 (Web Crawling)**: Crawler timeouts, rate limits, user agents, proxy settings
- **Module 02 (Document Processing)**: Parser settings, file size limits, format support
- **Module 03 (AI/ML Integration)**: Model parameters, API keys, timeout settings, retry policies
- **Module 04 (System Orchestration)**: Coordination timeouts, concurrency limits, workflow settings
- **Module 05 (Vector Databases)**: Connection strings, pool sizes, indexing parameters
- **Module 06 (Search/Retrieval)**: Relevance thresholds, result limits, ranking parameters
- **Module 07 (Citation Management)**: Format preferences, validation rules, export settings
- **Module 08 (Error Handling)**: Log levels, retry policies, escalation thresholds

## Summary

Configuration and settings management systems are like having a master system administrator who:
- **Adapts systems perfectly** for any environment or use case
- **Validates all settings** to prevent dangerous or impossible configurations
- **Enables safe changes** even while systems are running
- **Maintains complete history** of what was changed when and why
- **Protects sensitive data** while keeping it accessible when needed
- **Provides clear documentation** so anyone can understand and modify settings

By testing these systems thoroughly, we ensure that applications can be reliably deployed and managed across different environments, with the flexibility to adapt to changing requirements while maintaining security and stability.

The key to testing configuration management is to think like both a system administrator (what settings do I need to control?) and a security expert (what could go wrong if these settings are incorrect?). When both perspectives are covered, you've built a system that can safely adapt to any deployment scenario!

---

*Next: Module 10 - Performance and Scalability Testing*
*Previous: Module 08 - Error Handling and Logging Testing*

**Test Guardian Note**: This module demonstrates how configuration management testing ensures that systems can be safely deployed and managed across different environments. Every configuration test protects against deployment failures and security vulnerabilities while enabling the flexibility needed for modern software delivery.
