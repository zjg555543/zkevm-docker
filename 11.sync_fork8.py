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
    print('Start fork8 sync...')

    command = '''
    docker-compose up -d x1-state-db-2;
    docker-compose up -d x1-pool-db-2;
    docker-compose up -d x1-event-db-2;
    sleep 1;
    docker-compose up -d x1-executor-fork8-2;
    sleep 5;
    docker-compose up -d x1-sync-fork8-2;

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 10 -f")
    
