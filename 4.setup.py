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
    print('Setup sequencer..')

    command = '''
        docker-compose up -d erigon-aggregator-db
        docker-compose up -d erigon-state-db
        sleep 3
        docker-compose up -d erigon-stateless-executor
        docker-compose up -d erigon-prover
        docker-compose up -d erigon-approve
        sleep 3
        docker-compose up -d erigon-seq
        sleep 3
        docker-compose up -d erigon-seqsender
        sleep 3
        docker-compose up -d erigon-aggregator
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")
