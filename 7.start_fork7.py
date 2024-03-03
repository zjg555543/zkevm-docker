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
    print('Start fork7...')

    command = '''
    docker-compose up -d zkevm-executor-fork7
    docker-compose up -d  zkevm-sync-fork7

    # docker-compose up -d zkevm-prover-fork7
    # docker-compose up -d zkevm-sequencer-fork7

    # docker-compose up -d zkevm-eth-tx-manager-fork7
    # docker-compose up -d zkevm-sequence-sender-fork7
    # docker-compose up -d zkevm-l2gaspricer-fork7
    # docker-compose up -d zkevm-aggregator-fork7
    # docker-compose up -d zkevm-json-rpc-fork7

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    
