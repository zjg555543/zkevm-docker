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
    print('Deploying fork6...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = '''
    docker stop $(docker ps -aq); 
    docker rm $(docker ps -aq);
    docker ps -a;
    docker rmi --force $(docker images -q);
    docker images
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译合约
    command = '''
    rm -rf fork6; 
    mkdir fork6;
    cd fork6; 
    git clone -b v3.0.0-fork.6 https://github.com/0xPolygonHermez/zkevm-contracts.git; 
    cd ./zkevm-contracts; 
    cp ../../config/deployment/deploy_parameters.json deployment/deploy_parameters.json;  
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/hardhat.config.js hardhat.config.js;  
    cp ../../config/deployment/1_createGenesis.js deployment/1_createGenesis.js
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork6/zkevm-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork6/zkevm-contracts/deployment/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork6/zkevm-contracts; 
    npm i; 
    npm run deploy:deployer:ZkEVM:sepolia; 
    npm run  deploy:ZkEVM:sepolia; 
    npm run  verify:ZkEVM:sepolia; 
    cat deployment/genesis.json; 
    cat deployment/deploy_output.json 
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译node
    command = '''
    cd fork6; 
    git clone -b release/v0.4.4 https://github.com/0xPolygonHermez/zkevm-node.git; 
    cd zkevm-node; 
    docker build -t zkevm-node-fork6 -f ./Dockerfile .
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 替换文件
    polygonZkEVMAddress = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    deploymentBlockNumber = get_value('./fork6/zkevm-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    genesisStr = get_genesis('./fork6/zkevm-contracts/deployment/genesis.json')

    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesis}', genesisStr)

    logging.info("docker-compose logs --tail 50 -f | grep zkevm-sequencer")
    logging.info("Deploy fork6 done.")

