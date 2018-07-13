import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(current_dir))
print(f'ROOT_PATH={ROOT_PATH}')
MAINNET_SETTINGS = os.path.join(ROOT_PATH, 'config', 'mainnet.json')


class Config:
    CONNECTED_MAX_PEER = 5
    SEED_LIST = None

    def setup(self, config_file):
        with open(config_file) as data_file:
            data = json.load(data_file)

        proto_conf = data['protocol_configuration']
        self.SEED_LIST = proto_conf['seed_list']

    def setup_mainnet(self):
        self.setup(MAINNET_SETTINGS)


config = Config()
