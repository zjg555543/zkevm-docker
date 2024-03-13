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
    print('Deploying fork5...')
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
    rm -rf fork5; 
    mkdir fork5;
    cd fork5; 
    git clone -b release/v0.1.0 https://github.com/okx/x1-contracts.git; 
    cd ./x1-contracts; 
    cp ../../config/deployment/deploy_parameters.json deployment/deploy_parameters.json;  
    cp -r ../../config/deployment/hardhat.config.js hardhat.config.js;
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/1_createGenesis.js deployment/1_createGenesis.js
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork5/x1-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork5/x1-contracts/deployment/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork5/x1-contracts; 
    npm i; 
    npm run deploy:deployer:ZkEVM:sepolia; 
    npm run  deploy:ZkEVM:sepolia; 
    npm run  verify:ZkEVM:sepolia; 
    cat deployment/genesis.json; 
    cat deployment/deploy_output.json 
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 替换文件
    polygonZkEVMAddress = get_value('./fork5/x1-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork5/x1-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    dataCommitteeContract = get_value('./fork5/x1-contracts/deployment/deploy_output.json', 'dataCommitteeContract')
    deploymentBlockNumber = get_value('./fork5/x1-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    polygonZkEVMBridgeAddress = get_value('./fork5/x1-contracts/deployment/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork5/x1-contracts/deployment/genesis.json')

    replace_variable('./config/fork5/test.da.toml', '{ZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork5/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork5/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork5/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork5/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork5/test.genesis.config.json', '{genesis}', genesisStr)
    replace_variable('./config/fork5/test.genesis.config.json', '{dataCommitteeContract}', dataCommitteeContract)

    replace_variable('./config/fork5/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork5/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork5/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)

    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS_FORK5}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS_FORK5}', polygonZkEVMAddress)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS_FORK5}', polygonZkEVMBridgeAddress)

    # 设置da地址
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://x1-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    command = command.replace("{genAccount}", genAccount)
    command = command.replace("{genPriveKey}", genPriveKey)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 50 -f | grep x1-sequencer")
    logging.info("Deploy fork5 done.")

    print('Deploying fork5...')

    command = '''
    docker-compose up -d x1-state-db
    docker-compose up -d x1-pool-db
    docker-compose up -d x1-event-db
    docker-compose up -d x1-data-availability-db
    docker-compose up -d x1-bridge-db
    docker-compose up -d x1-bridge-redis

    sleep 3
    docker-compose up -d x1-data-availability-fork5

    sleep 3
    docker-compose up -d x1-executor-fork5
    sleep 3
    docker-compose up -d x1-prover-fork5
    sleep 3
    docker-compose up -d x1-sync-fork5
    sleep 3
    docker-compose up -d x1-eth-tx-manager-fork5
    sleep 3
    docker-compose up -d x1-sequencer-fork5
    sleep 3
    docker-compose up -d x1-sequence-sender-fork5
    sleep 3
    docker-compose up -d x1-l2gaspricer-fork5
    sleep 3
    docker-compose up -d x1-aggregator-fork5
    sleep 3
    docker-compose up -d x1-json-rpc-fork5
    sleep 3
    docker-compose up -d kafka-zookeeper
    sleep 3
    docker-compose up -d x1-bridge-coin-kafka
    sleep 3
    docker-compose up -d x1-bridge-service-fork5
    sleep 3
    docker-compose up -d x1-bridge-ui-fork5

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")

