import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def get_genesis(file_path):
    # 读取JSON文件
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 删除第一行和最后一行
    lines = lines[1:-1]

    new_json_data = ''.join(lines)

    return str(new_json_data)

def loadAccount():
    # 读取JSON文件
    with open("account_info.json", 'r') as json_file:
        account_info = json.load(json_file)
    return account_info


if __name__ == '__main__':
    print('Deploying fork6...')

    command = '''
    docker-compose up -d x1-state-db
    docker-compose up -d x1-pool-db
    docker-compose up -d x1-event-db
    docker-compose up -d x1-data-availability-db

    sleep 3
    docker-compose up -d x1-data-availability-fork6

    sleep 3
    docker-compose up -d x1-executor-fork6
    sleep 3
    docker-compose up -d x1-prover-fork6
    sleep 3
    docker-compose up -d x1-sync-fork6
    sleep 3
    docker-compose up -d x1-eth-tx-manager-fork6
    sleep 3
    docker-compose up -d x1-sequencer-fork6
    sleep 3
    docker-compose up -d x1-sequence-sender-fork6
    sleep 3
    docker-compose up -d x1-l2gaspricer-fork6
    sleep 3
    docker-compose up -d x1-aggregator-fork6
    sleep 3
    docker-compose up -d x1-json-rpc-fork6
    sleep 3

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    command = "sleep 30; cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url http://127.0.0.1:8123 0xC949254d682D8c9ad5682521675b8F43b102aec4 --value 0.0001ether"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
