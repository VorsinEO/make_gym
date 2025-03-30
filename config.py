import os
import yaml

# Default configuration
DEFAULT_CONFIG = {
    'webhook_url': 'https://hook.eu2.make.com/g06cmor51yt154js78btaty67ssr5i8l',  # Replace with your webhook URL
    'local_file': 'training_log.csv',
    'required_fields': ['workout_name', 'exercise_name', 'set_number', 'weight_kg', 'reps'],
    'optional_fields': ['rpe', 'rest_sec', 'notes'],
    'log_level': 'INFO',  # Possible values: DEBUG, INFO, WARNING, ERROR
    'log_format': '%(asctime)s - %(levelname)s - %(message)s'
}

def load_config():
    """Load configuration from config.yaml if it exists, otherwise use defaults."""
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = DEFAULT_CONFIG
        # Save default config to file
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f)
    return config 