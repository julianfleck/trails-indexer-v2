import os
import unittest
from utils.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        self.config_loader = ConfigLoader()

    def test_load_config(self):
        # Load the configuration
        config = self.config_loader.load_config()

        # Assert that the configuration is loaded (i.e., it is not None or empty)
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        self.assertNotEqual(config, {})

        # Assert that specific sections are present in the configuration
        self.assertIn('NEO4J', config)
        self.assertIn('OPENAI', config)

    def test_environment_variable_override(self):
        # Set an environment variable
        os.environ['NEO4J_PASSWORD'] = 'env_password'
        
        # Load the configuration
        config = self.config_loader.load_config()

        # Assert that the environment variable has overridden the configuration file value
        self.assertEqual(config['NEO4J']['PASSWORD'], 'env_password')

        # Clean up by removing the environment variable
        del os.environ['NEO4J_PASSWORD']

if __name__ == '__main__':
    unittest.main()
