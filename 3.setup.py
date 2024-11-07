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
        docker-compose up -d xlayer-agg-db
        docker-compose up -d xlayer-state-db
        sleep 3
        docker-compose up -d xlayer-executor
        docker-compose up -d xlayer-prover
        docker-compose up -d xlayer-approve
        sleep 3
        docker-compose up -d xlayer-seq
        sleep 3
        docker-compose up -d xlayer-seqs
        sleep 3
        docker-compose up -d xlayer-agg
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")
