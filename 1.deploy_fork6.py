import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

genAccount = "0xC7BfFA34425A7DE568a50519cA75193523bFef53"
genPriveKey = "0x7cef03307b6920714c776ed055f2d59792f77ad1a375a50644d628bdcdfbe8fd"
genMnemonic = "average citizen crumble myself garden bacon release banner repeat siege pear spare"

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

if __name__ == '__main__':
    print('Deploying fork6...')

    # command = "docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a;docker rmi --force $(docker images -q);docker images"
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # # 编译合约
    # command = "rm -rf x1-contracts; git clone -b release/v0.2.0 https://github.com/okx/x1-contracts.git; cd ./x1-contracts; cp ../config/deployment/deploy_parameters.json deployment/deploy_parameters.json;  cp ../config/deployment/.env .env;  cp ../config/deployment/hardhat.config.js hardhat.config.js;  cp ../config/deployment/1_createGenesis.js deployment/1_createGenesis.js"
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # replace_variable('./x1-contracts/.env', '{MNEMONIC}', genMnemonic)
    # replace_variable('./x1-contracts/deployment/deploy_parameters.json', '{ADMIN}', genAccount)

    # # 编译node
    # command = "rm -rf x1-node; git clone -b release/v0.2.0 https://github.com/okx/x1-node.git; cd x1-node; docker build -t x1-node-fork6 -f ./Dockerfile ."
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # # 编译da
    # command = "rm -rf x1-data-availability; git clone -b release/v0.2.0 https://github.com/okx/x1-data-availability.git; cd x1-data-availability; docker build -t x1-data-availability-fork6 -f ./Dockerfile ."
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # # 部署合约
    # command = "cd ./x1-contracts; npm i; npm run deploy:deployer:ZkEVM:sepolia; npm run  deploy:ZkEVM:sepolia; npm run  verify:ZkEVM:sepolia; cat deployment/genesis.json; cat deployment/deploy_output.json "
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # 替换文件
    polygonZkEVMAddress = get_value('./x1-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./x1-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    dataCommitteeContract = get_value('./x1-contracts/deployment/deploy_output.json', 'dataCommitteeContract')
    deploymentBlockNumber = get_value('./x1-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    genesisStr = get_genesis('./x1-contracts/deployment/genesis.json')

    replace_variable('./config/fork6/test.da.toml', '{ZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork6/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)
    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesis}', genesisStr)



    
