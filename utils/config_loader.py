import toml
import os

class ConfigLoader:
    def __init__(self, file_path='config/configuration.toml'):
        self.file_path = file_path
        self.config = self.load_config()

    def load_config(self):
        # Load the configuration from the TOML file
        config = toml.load(self.file_path)

        # Override the configuration with environment variables if they exist
        for section, values in config.items():
            for key, value in values.items():
                env_var_name = f"{section.upper()}_{key.upper()}"
                env_var_value = os.environ.get(env_var_name)
                config[section][key] = env_var_value or value

        # Change boolean values from strings to actual booleans
        for section, values in config.items():
            for key, value in values.items():
                if value == 'true':
                    config[section][key] = True
                elif value == 'false':
                    config[section][key] = False
                    
        return config

    def get_config(self):
        return self.config

    def get(self, key, section=None, default=None):
        """
        Retrieves a specific configuration value given its section and key.
        
        :param key: The key within the section.
        :param section: The section in the configuration file. (Optional)
        :param default: The default value to return if the section or key is not found.
        :return: The configuration value, or the default value if the section or key is not found.
        """
        # if no section is given, look for the key in all sections
        if section is None:
            for sec in self.config:
                if key in self.config[sec]:
                    return self.config[sec][key]
            return default
        return self.config.get(section, {}).get(key, default)

    def get_neo4j_config(self):
        return self.config.get('NEO4J', {})

    def get_openai_config(self):
        return self.config.get('OPENAI', {})

    def get_text_processing_config(self):
        return self.config.get('TEXT_PROCESSING', {})

    def get_spacy_config(self):
        return self.config.get('SPACY', {})

    def get_vector_index_config(self):
        return self.config.get('VECTOR_INDEX', {})
    
    def get_general_config(self):
        return self.config.get('GENERAL', {})

# Example usage
if __name__ == "__main__":
    config_loader = ConfigLoader('config/configuration.toml')
    config = config_loader.config
    print(config)

