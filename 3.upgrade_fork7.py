import subprocess
import logging
import json
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(lineno)d: %(message)s', level=logging.DEBUG)

OKBAddress = "0xe223519d64C0A49e7C08303c2220251be6b70e1d"

def replace_file(file_path, key, value):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    data[key] = value

    # 保存更新后的数据回文件
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    print("两个新字段已添加并保存到文件.")

if __name__ == '__main__':
    print('Upgrade fork7...')

    # 编译合约
    # command = '''
    # rm -rf fork7;
    # mkdir fork7;
    # cd fork7;
    # git clone https://github.com/jiaji-wei/x1-contracts.git;
    # cd ./x1-contracts;
    # git checkout zkevm/v4.0.0-fork.7; 
    # cp ../../fork6/x1-contracts/deployment/deploy_parameters.json upgrade/upgradeToV2/;
    # cp ../../fork6/x1-contracts/deployment/deploy_output.json upgrade/upgradeToV2/;
    # cp -rf ../../fork6/x1-contracts/.openzeppelin .;
    # cp ../../fork6/x1-contracts/.env .;
    # cd upgrade/upgradeToV2/;
    # cp upgrade_parameters.json.example upgrade_parameters.json;
    # '''
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'consensusContract', "PolygonValidiumEtrogIsolated")
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/deploy_parameters.json', 'dataAvailabilityProtocol', "PolygonDataCommittee")
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/deploy_output.json', 'gasTokenAddress', OKBAddress)
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'realVerifier', True)
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockDelay', 360)
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'timelockSalt', "0x0000000000000000000000000000000000000000000000000000000000000000")
    # replace_file('./fork7/x1-contracts/upgrade/upgradeToV2/upgrade_parameters.json', 'polTokenAddress', OKBAddress)

    # 部署合约
    # command = '''
    # cd fork7/x1-contracts;
    # npm i;
    # npm run upgradev2:timelock:sepolia;
    # cat upgrade/upgradeToV2/upgrade_output.json
    # '''
    # result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # logging.info(result.stdout)

    # 编译节点
    command = '''
    cd fork7;
    git clone -b zjg/fork7-upgrade https://github.com/okx/x1-node.git;
    cd x1-node;
    docker build -t x1-node-fork7 -f ./Dockerfile .
    cd ../;
    git clone -b zjg/fork7-upgrade https://github.com/okx/x1-data-availability.git
    cd x1-data-availability;
    docker build -t x1-data-availability-fork7 -f ./Dockerfile .
    '''
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    logging.info(result.stdout)

    # 配置节点
    
