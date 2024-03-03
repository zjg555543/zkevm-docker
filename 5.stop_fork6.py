import subprocess
import logging
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
    print('Stop fork6...')

    command = '''
    docker-compose stop x1-data-availability-fork6
    docker-compose stop x1-executor-fork6
    docker-compose stop x1-prover-fork6
    docker-compose stop x1-sync-fork6

    docker-compose stop x1-eth-tx-manager-fork6
    docker-compose stop x1-sequencer-fork6
    docker-compose stop x1-sequence-sender-fork6
    docker-compose stop x1-l2gaspricer-fork6
    docker-compose stop x1-aggregator-fork6
    docker-compose stop x1-json-rpc-fork6

    docker rm x1-data-availability
    docker rm x1-executor
    docker rm x1-prover
    docker rm x1-sync

    docker rm x1-eth-tx-manager
    docker rm x1-sequencer
    docker rm x1-sequence-sender
    docker rm x1-l2gaspricer
    docker rm x1-aggregator
    docker rm x1-json-rpc

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
