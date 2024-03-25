import subprocess
import logging
import json
import time
import psycopg2

conn = psycopg2.connect(
    dbname="state_db",
    user="state_user",
    password="state_password",
    host="127.0.0.1",
    port="5432"
)

#PGPASSWORD=test_password psql -h 127.0.0.1 -p 5434 -d test_db -U test_user;
conn_bridge = psycopg2.connect(
    dbname="test_db",
    user="test_user",
    password="test_password",
    host="127.0.0.1",
    port="5434"
)

OKBAddress = "0xe223519d64C0A49e7C08303c2220251be6b70e1d"

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

def replace_file(file_path, key, value):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    data[key] = value

    # 保存更新后的数据回文件
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    logging.info("两个新字段已添加并保存到文件.")

def zkevm_batchNumber():
    command = '''
    curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"zkevm_batchNumber","params":[],"id":83}' http://127.0.0.1:8123 | jq
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    parsed_data = json.loads(result.stdout)
    # 获取 result 的值并转换为十进制
    result_hex = parsed_data["result"]
    result_decimal = int(result_hex, 16)
    return result_decimal

def zkevm_verifiedBatchNumber():
    command = '''
    curl -X POST --data '{    "jsonrpc": "2.0",    "method": "zkevm_verifiedBatchNumber",    "params": [],    "id": 1}' -H "Content-Type: application/json" 127.0.0.1:8123 | jq
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    parsed_data = json.loads(result.stdout)
    # 获取 result 的值并转换为十进制
    result_hex = parsed_data["result"]
    result_decimal = int(result_hex, 16)
    return result_decimal

def send_tx():
    logging.info('Send tx...')

    account = loadAccount()
    command = "sleep 10; cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url http://127.0.0.1:8123 0xC949254d682D8c9ad5682521675b8F43b102aec4 --value 0.0001ether"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

   
def deploy_fork6():
    logging.info('Deploying fork6...')
    account = loadAccount()
    genAccount = account["address"]
    genPriveKey = account["private_key"]
    genMnemonic = account["mnemonic"]

    command = "docker stop $(docker ps -aq); docker rm $(docker ps -aq); docker ps -a;"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 编译合约
    command = '''
    rm -rf fork6; 
    mkdir fork6;
    cd fork6; 
    git clone -b release/v0.2.0 https://github.com/okx/xlayer-contracts.git; 
    cd ./xlayer-contracts; 
    cp ../../config/deployment/deploy_parameters.json deployment/deploy_parameters.json;  
    cp ../../config/deployment/.env .env;  
    cp ../../config/deployment/hardhat.config.js hardhat.config.js;  
    cp ../../config/deployment/1_createGenesis.js deployment/1_createGenesis.js
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_variable('./fork6/xlayer-contracts/.env', '{MNEMONIC}', genMnemonic)
    replace_variable('./fork6/xlayer-contracts/deployment/deploy_parameters.json', '{ADMIN}', genAccount)

    # 部署合约
    command = '''
    cd ./fork6/xlayer-contracts; 
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
    polygonZkEVMAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    dataCommitteeContract = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'dataCommitteeContract')
    deploymentBlockNumber = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    polygonZkEVMBridgeAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork6/xlayer-contracts/deployment/genesis.json')

    replace_variable('./config/fork6/test.da.toml', '{ZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork6/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMAddress}', polygonZkEVMAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork6/test.genesis.config.json', '{genesis}', genesisStr)
    replace_variable('./config/fork6/test.genesis.config.json', '{dataCommitteeContract}', dataCommitteeContract)

    replace_variable('./config/fork6/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork6/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork6/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)

    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS_FORK6}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS_FORK6}', polygonZkEVMAddress)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS_FORK6}', polygonZkEVMBridgeAddress)

    # 设置da地址
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://xlayer-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    command = command.replace("{genAccount}", genAccount)
    command = command.replace("{genPriveKey}", genPriveKey)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 50 -f | grep xlayer-sequencer")
    logging.info("Deploy fork6 done.")


def start_fork6():
    logging.info('Deploying fork6...')

    command = '''
    docker-compose up -d xlayer-state-db
    docker-compose up -d xlayer-pool-db
    docker-compose up -d xlayer-event-db
    docker-compose up -d xlayer-data-availability-db
    docker-compose up -d xlayer-bridge-db
    docker-compose up -d xlayer-bridge-redis

    docker-compose up -d xlayer-data-availability-fork6
    docker-compose up -d xlayer-executor-fork6
    docker-compose up -d xlayer-prover-fork6
    sleep 3
    docker-compose up -d xlayer-sync-fork6
    sleep 1
    docker-compose up -d xlayer-sequencer-fork6
    sleep 1
    docker-compose up -d xlayer-eth-tx-manager-fork6
    docker-compose up -d xlayer-sequence-sender-fork6
    docker-compose up -d xlayer-l2gaspricer-fork6
    docker-compose up -d xlayer-aggregator-fork6
    docker-compose up -d xlayer-json-rpc-fork6
    sleep 1
    docker-compose up -d kafka-zookeeper
    docker-compose up -d xlayer-bridge-coin-kafka
    docker-compose up -d xlayer-bridge-service-fork6
    docker-compose up -d xlayer-bridge-ui-fork6
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("docker-compose logs --tail 10 -f")

def upgrade_fork8():
    logging.info('Upgrade fork8...')

    # 编译合约
    command = '''
    rm -rf fork8;
    mkdir fork8;
    cd fork8;
    git clone -b release/v0.3.0 https://github.com/okx/xlayer-contracts.git;
    cd ./xlayer-contracts;
    cp ../../fork6/xlayer-contracts/deployment/deploy_parameters.json upgrade/upgradeToV2/;
    cp ../../fork6/xlayer-contracts/deployment/deploy_output.json upgrade/upgradeToV2/;
    cp -rf ../../fork6/xlayer-contracts/.openzeppelin .;
    cp ../../fork6/xlayer-contracts/.env .;
    cd upgrade/upgradeToV2/;
    cp upgrade_parameters.json.example upgrade_parameters.json;
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'consensusContract', "PolygonValidiumEtrogIsolated")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'dataAvailabilityProtocol', "PolygonDataCommittee")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_output.json', 'gasTokenAddress', OKBAddress)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'realVerifier', True)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockDelay', 125)
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockSalt', "0x0000000000000000000000000000000000000000000000000000000000000000")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'polTokenAddress', OKBAddress)

    # 部署合约
    command = '''
    cd fork8/xlayer-contracts;
    npm i;
    npm run upgradev2:timelock:sepolia;
    cat upgrade/upgradeToV2/upgrade_output.json
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 配置节点
    rollupmgr = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMAddress')
    polygonZkEVMGlobalExitRootAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMGlobalExitRootAddress')
    deploymentBlockNumber = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'deploymentBlockNumber')
    polygonZkEVMBridgeAddress = get_value('./fork6/xlayer-contracts/deployment/deploy_output.json', 'polygonZkEVMBridgeAddress')
    genesisStr = get_genesis('./fork6/xlayer-contracts/deployment/genesis.json')

    dataCommitteeContract = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'polygonDataCommittee')
    newPolygonZKEVM = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')

    replace_variable('./config/fork8/test.da.toml', '{PolygonValidiumAddress}', newPolygonZKEVM)
    replace_variable('./config/fork8/test.da.toml', '{DataCommitteeAddress}', dataCommitteeContract)

    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMAddress}', newPolygonZKEVM)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonRollupManagerAddress}', rollupmgr)
    replace_variable('./config/fork8/test.genesis.config.json', '{polygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesisBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/test.genesis.config.json', '{genesis}', genesisStr)

    replace_variable('./config/fork8/config.bridge.toml', '{GenBlockNumber}', deploymentBlockNumber)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonBridgeAddress}', polygonZkEVMBridgeAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEVMGlobalExitRootAddress}', polygonZkEVMGlobalExitRootAddress)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonRollupManagerAddress}', rollupmgr)
    replace_variable('./config/fork8/config.bridge.toml', '{PolygonZkEvmAddress}', newPolygonZKEVM)

    replace_variable('./docker-compose.yml', '{ETHEREUM_ROLLUP_MANAGER_ADDRESS_FORK8}', rollupmgr)
    replace_variable('./docker-compose.yml', '{ETHEREUM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)
    replace_variable('./docker-compose.yml', '{ETHEREUM_PROOF_OF_EFFICIENCY_CONTRACT_ADDRESS_FORK8}', newPolygonZKEVM)
    replace_variable('./docker-compose.yml', '{POLYGON_ZK_EVM_BRIDGE_CONTRACT_ADDRESS_FORK8}', polygonZkEVMBridgeAddress)


def set_da_fork8():
    logging.info('Set fork8 da...')

    # 设置da地址
    dataCommitteeContract = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'polygonDataCommittee')
    newPolygonZKEVM = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'newPolygonZKEVM')

    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {dataCommitteeContract} 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://xlayer-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    
    account = loadAccount()
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)


    # 设置newZKEVM合约
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {newZKEVM} 'setDataAvailabilityProtocol(address)'  {dataCommitteeContract}"

    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{newZKEVM}", newPolygonZKEVM)
    command = command.replace("{dataCommitteeContract}", dataCommitteeContract)

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def schedule_fork8():
    logging.info('schedule fork8 ...')
    scheduleData = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'scheduleData')
    timelockContractAdress = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'timelockContractAdress')

    account = loadAccount()
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662  {timelockContractAdress} '{scheduleData}'"
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{scheduleData}", scheduleData)
    command = command.replace("{timelockContractAdress}", timelockContractAdress)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def stop_fork6():
    logging.info('Stop fork6...')

    command = '''
    docker-compose stop xlayer-data-availability-fork6
    docker-compose stop xlayer-executor-fork6
    docker-compose stop xlayer-prover-fork6
    docker-compose stop xlayer-sync-fork6

    docker-compose stop xlayer-eth-tx-manager-fork6
    docker-compose stop xlayer-sequencer-fork6
    docker-compose stop xlayer-sequence-sender-fork6
    docker-compose stop xlayer-l2gaspricer-fork6
    docker-compose stop xlayer-aggregator-fork6
    docker-compose stop xlayer-json-rpc-fork6
    docker-compose stop xlayer-bridge-service-fork6
    docker-compose stop xlayer-bridge-ui-fork6
    sleep 3

    docker rm xlayer-data-availability
    docker rm xlayer-executor
    docker stop xlayer-prover
    sleep 3
    docker rm xlayer-prover
    docker rm xlayer-sync

    docker rm xlayer-eth-tx-manager
    docker rm xlayer-sequencer
    docker rm xlayer-sequence-sender
    docker rm xlayer-l2gaspricer
    docker rm xlayer-aggregator
    docker rm xlayer-json-rpc
    docker rm xlayer-bridge-service
    docker rm xlayer-bridge-ui

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def delete_db(batch_num):
    logging.info('Delete db...')

    # PGPASSWORD=state_password psql -h 127.0.0.1 -p 5432 -d state_db -U state_user;
    # select * from state.batch;
    # delete from state.batch where batch_num = '{batch_num}';

    command = '''
    delete from state.batch where batch_num = '{batch_num}';
    '''
    command = command.replace("{batch_num}", batch_num)
    # 执行 SQL 查询
    cur = conn.cursor()
    cur.execute(command)
    conn.commit()
    logging.info("command: " + command)
    # 关闭游标和连接
    cur.close()
    conn.close()

    logging.info('Delete db ok')

def execute_fork8():
    logging.info('execute fork8 ...')
    executeData = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'executeData')
    timelockContractAdress = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_output.json', 'timelockContractAdress')

    account = loadAccount()
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662  {timelockContractAdress} '{executeData}'"
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{executeData}", executeData)
    command = command.replace("{timelockContractAdress}", timelockContractAdress)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    

def start_fork8(batch):
    logging.info('Start fork8...')

    replace_variable('./config/fork8/test.node.config.toml', '{UpgradeEtrogBatchNumber}', batch)

    command = '''
    docker-compose up -d xlayer-executor-fork8
    sleep 3
    docker-compose up -d  xlayer-sync-fork8
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    command = '''
    docker-compose up -d xlayer-data-availability-fork8
    sleep 1
    docker-compose up -d xlayer-prover-fork8
    sleep 3
    docker-compose up -d xlayer-sequencer-fork8
    sleep 1
    docker-compose up -d xlayer-eth-tx-manager-fork8
    docker-compose up -d xlayer-sequence-sender-fork8
    docker-compose up -d xlayer-l2gaspricer-fork8
    docker-compose up -d xlayer-aggregator-fork8
    docker-compose up -d xlayer-json-rpc-fork8
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 10 -f")

def upgrade_fork8_l2contract():
    logging.info('Update L2 bridge contract...')

    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'gasTokenName', "OKB")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'gasTokenSymbol', "OKB")
    replace_file('./fork8/xlayer-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'gasTokenDecimals', 18)

    # 部署合约
    command = '''
    cd fork8/xlayer-contracts;
    npm run upgradev2L2:timelock:x1;
    cat upgrade/upgradeToV2/upgrade_outputL2.json;
    '''

    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)


    # schedule
    logging.info('schedule fork8 ...')
    scheduleData = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_outputL2.json', 'scheduleData')
    executeData = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_outputL2.json', 'executeData')
    timelockL2Address = get_value('./fork8/xlayer-contracts/upgrade/upgradeToV2/upgrade_outputL2.json', 'timelockL2Address')

    account = loadAccount()
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url http://127.0.0.1:8123 {timelockL2Address} '{scheduleData}' "
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{scheduleData}", scheduleData)
    command = command.replace("{timelockL2Address}", timelockL2Address)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)
    logging.info("Waiting for 180s...")
    time.sleep(180)

    # execute
    command = "cast send --legacy --from {genAccount} --private-key {genPriveKey} --rpc-url https://rpc.ankr.com/eth_sepolia/578c95407e7831f0ac1ef79cacae294dc9bf8307121ca9fffaf1e556a5cca662 {timelockL2Address} '{executeData}' "
    command = command.replace("{genAccount}", account["address"])
    command = command.replace("{genPriveKey}", account["private_key"])
    command = command.replace("{executeData}", executeData)
    command = command.replace("{timelockL2Address}", timelockL2Address)
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

def start_fork8_bridge():
    logging.info('Start fork8 bridge...')

    command = '''
    docker-compose up -d xlayer-bridge-service-fork8
    sleep 3
    docker-compose up -d xlayer-bridge-ui-fork8
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 删除数据库
    # PGPASSWORD=test_password psql -h 127.0.0.1 -p 5434 -d test_db -U test_user;
    # select * from public.gorp_migrations;
    # delete from public.gorp_migrations where id = '0010.sql';
    # delete from public.gorp_migrations where id = '0009.sql';
    # delete from public.gorp_migrations where id = '0008.sql';
    # delete from public.gorp_migrations where id = '0007.sql';

    command = '''
    delete from public.gorp_migrations where id = '0010.sql';
    delete from public.gorp_migrations where id = '0009.sql';
    delete from public.gorp_migrations where id = '0008.sql';
    delete from public.gorp_migrations where id = '0007.sql';
    '''
    # 执行 SQL 查询
    cur = conn_bridge.cursor()
    cur.execute(command)
    conn_bridge.commit()
    logging.info("command: " + command)
    # 关闭游标和连接
    cur.close()
    conn_bridge.close()

    logging.info('Delete db ok')

    command = '''
    docker-compose up -d xlayer-bridge-service-fork8
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 10 -f")


def sync_fork8():
    logging.info('Start fork8 sync...')

    command = '''
    docker-compose up -d xlayer-state-db-2;
    docker-compose up -d xlayer-pool-db-2;
    docker-compose up -d xlayer-event-db-2;
    sleep 1;
    docker-compose up -d xlayer-executor-fork8-2;
    sleep 5;
    docker-compose up -d xlayer-sync-fork8-2;

    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    logging.info("docker-compose logs --tail 10 -f")


    
if __name__ == '__main__':
    # deploy fork6
    deploy_fork6()
    start_fork6()
    for i in range(0, 3):
        logging.info("Waiting for 2s...")
        time.sleep(1)
        send_tx()

    # upgrade fork8
    upgrade_fork8()
    schedule_fork8()
    logging.info("Waiting for 180s...")
    time.sleep(180)

    # 需要确保不再出块
    while True:
        batch = zkevm_batchNumber()
        verifyBatch = zkevm_verifiedBatchNumber()
        logging.info("batch: " + str(batch) + " verifyBatch: " + str(verifyBatch))
        time.sleep(2)
        if verifyBatch + 1 == batch:
            break 
        else:
            logging.info("wating...")
    
    batch = zkevm_batchNumber()
    # 停止fork6所有节点
    stop_fork6()

    # 删除数据库
    delete_db(str(batch))
    
    # 执行 execute
    execute_fork8()

    # 设置da
    set_da_fork8()

    # 启动 fork8 程序
    start_fork8(str(batch))

    # 升级 L2 合约
    upgrade_fork8_l2contract()

    start_fork8_bridge()
    sync_fork8()


 