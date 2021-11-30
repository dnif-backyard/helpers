import yaml
import logging
import os


def load(file_path):
    try:
        if not os.path.isfile(file_path):
            logging.warning(f'file "{file_path}" does not exist')
            return {}
        with open(file_path, 'r') as yml_file:
            yml_config = yaml.safe_load(yml_file)
            return yml_config
    except Exception as e:
        logging.error(f'failed loading configuration file - {e}')


def dump(file_path, config_data):
    try:
        if os.path.isfile(file_path):
            logging.debug(f'file "{file_path}" already exist overwriting')

        with open(file_path, 'w') as yml_file:
            yml_data = yaml.safe_dump(config_data, yml_file)
    except Exception as e:
        logging.error(f'failed writing configuration file - {e}')
