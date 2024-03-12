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
    print('Deploying fork8...')

    command = '''
    docker-compose up -d x1-state-db
    docker-compose up -d x1-pool-db
    docker-compose up -d x1-event-db
    docker-compose up -d x1-data-availability-db
    docker-compose up -d x1-bridge-db
    docker-compose up -d x1-bridge-redis

    sleep 3
    docker-compose up -d x1-data-availability-fork8

    sleep 3
    docker-compose up -d x1-executor-fork8
    sleep 3
    docker-compose up -d x1-prover-fork8
    sleep 3
    docker-compose up -d x1-sync-fork8
    sleep 3
    docker-compose up -d x1-eth-tx-manager-fork8
    sleep 3
    docker-compose up -d x1-sequencer-fork8
    sleep 3
    docker-compose up -d x1-sequence-sender-fork8
    sleep 3
    docker-compose up -d x1-l2gaspricer-fork8
    sleep 3
    docker-compose up -d x1-aggregator-fork8
    sleep 3
    docker-compose up -d x1-json-rpc-fork8
    sleep 3
    docker-compose up -d kafka-zookeeper
    sleep 3
    docker-compose up -d x1-bridge-coin-kafka
    sleep 3
    docker-compose up -d x1-bridge-service-fork8
    sleep 3
    docker-compose up -d x1-bridge-ui-fork8

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")