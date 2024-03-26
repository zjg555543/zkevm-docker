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

if __name__ == '__main__':
    print('Deploying fork9...')

    command = '''
    docker-compose up -d xlayer-state-db
    docker-compose up -d xlayer-pool-db
    docker-compose up -d xlayer-event-db
    docker-compose up -d xlayer-data-availability-db
    docker-compose up -d xlayer-bridge-db
    docker-compose up -d xlayer-bridge-redis

    sleep 3
    docker-compose up -d xlayer-data-availability-fork9

    sleep 3
    docker-compose up -d xlayer-executor-fork9
    sleep 3
    docker-compose up -d xlayer-prover-fork9
    sleep 3
    docker-compose up -d xlayer-sync-fork9
    sleep 3
    docker-compose up -d xlayer-eth-tx-manager-fork9
    sleep 3
    docker-compose up -d xlayer-sequencer-fork9
    sleep 3
    docker-compose up -d xlayer-sequence-sender-fork9
    sleep 3
    docker-compose up -d xlayer-l2gaspricer-fork9
    sleep 3
    docker-compose up -d xlayer-aggregator-fork9
    sleep 3
    docker-compose up -d xlayer-json-rpc-fork9
    sleep 3
    docker-compose up -d kafka-zookeeper
    sleep 3
    docker-compose up -d xlayer-bridge-coin-kafka
    sleep 3
    docker-compose up -d xlayer-bridge-service-fork9
    sleep 3
    docker-compose up -d xlayer-bridge-ui-fork9

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")
