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
    print('Setup zkevm..')

    command = '''
        docker-compose up -d zkevm-state-db
        docker-compose up -d zkevm-pool-db
        docker-compose up -d zkevm-event-db
        docker-compose up -d zkevm-approve
        sleep 3
        docker-compose up -d zkevm-prover
        sleep 5
        docker-compose up -d zkevm-node
        sleep 5
        docker-compose up -d erigon-rpc
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")
