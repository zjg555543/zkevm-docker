import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

def replace_variable(file_path, variable_name, new_value):
    # logging.info("file_path: " + file_path + " variable_name: " + variable_name + " new_value: " + new_value)
    with open(file_path, 'r') as file:
        file_content = file.read()

    new_content = file_content.replace(variable_name, new_value)

    with open(file_path, 'w') as file:
        file.write(new_content)

def get_value(file_path, key):
    # 读取JSON文件
    with open(file_path, 'r') as file:
        data = json.load(file)

    # 获取 "polygonZkEVMAddress" 的值
    value = data.get(key, None)
    return str(value)

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
    print('Deploying ...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = '''
    docker stop $(docker ps -aq); 
    docker rm $(docker ps -aq);
    docker ps -a;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译合约
    command = '''
    rm -rf fork9; 
    mkdir fork9;
    cd fork9; 
    git clone https://github.com/0xPolygonHermez/zkevm-contracts.git; 
    cd ./zkevm-contracts; 
    git checkout v6.0.0-rc.1-fork.9;
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/create_rollup_parameters.json deployment/v2/create_rollup_parameters.json;
    cp ../../config/deployment/deploy_parameters.json deployment/v2/deploy_parameters.json;  
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork9/zkevm-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork9/zkevm-contracts/deployment/v2/create_rollup_parameters.json', '{ADMIN}', genAccount)
    replace_variable('./fork9/zkevm-contracts/deployment/v2/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork9/zkevm-contracts; 
    npm i; 
    npm run deploy:v2:sepolia; 
    npm run  verify:v2:sepolia; 
    cat deployment/v2/create_rollup_output.json;
    cat deployment/v2/deploy_output.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
