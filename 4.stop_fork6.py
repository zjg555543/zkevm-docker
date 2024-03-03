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
    docker-compose stop zkevm-executor-fork6
    docker-compose stop zkevm-prover-fork6
    docker-compose stop zkevm-sync-fork6

    docker-compose stop zkevm-eth-tx-manager-fork6
    docker-compose stop zkevm-sequencer-fork6
    docker-compose stop zkevm-sequence-sender-fork6
    docker-compose stop zkevm-l2gaspricer-fork6
    docker-compose stop zkevm-aggregator-fork6
    docker-compose stop zkevm-json-rpc-fork6

    docker rm zkevm-executor
    docker stop zkevm-prover
    docker rm zkevm-prover
    docker rm zkevm-sync

    docker rm zkevm-eth-tx-manager
    docker rm zkevm-sequencer
    docker rm zkevm-sequence-sender
    docker rm zkevm-l2gaspricer
    docker rm zkevm-aggregator
    docker rm zkevm-json-rpc

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
