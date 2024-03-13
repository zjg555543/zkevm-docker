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
    print('Upgrate fork6...')
    print(''''
            cp ../fork5/.openzeppelin . -r
            cp -r ../fork5/.openzeppelin . 
            pwd
            npm run compile
            npm i
            cd ../ 

            mkdir deployc && cd deployc
            npx hardhat #enter
            npm install --save-dev hardhat
            cp ../fork6/compiled-contracts/FflonkVerifier.json .
            cat FflonkVerifier.json 
            cd scripts
            vim deploy.js
            vim ../hardhat.config.js
            vim ../hardhat.config.js
            cd ../
            npx hardhat run scripts/deploy.js --network goerli

            cd ../fork6/upgrade/
            cp upgrade_parameters.json.example upgrade_parameters.json

            cp -r ../fork5/.openzeppelin .
            cp ../fork5/.env .
            vim upgrade/upgrade_parameters.json
            cat ../fork5/deployment/deploy_parameters.json
            vim upgrade/upgrade_parameters.json
            cat ../fork5/deployment/deploy_output.json 
            vim upgrade/upgrade_parameters.
            vim upgrade/upgrade_parameters.json
            vim hardhat.config.js
            HARDHAT_NETWORK=sepolia node upgrade/timeLockUpgrade.js

            HARDHAT_NETWORK=sepolia node upgrade/timeLockUpgrade.js
            yarn compile
            vim upgrade/upgrade_parameters.json
            HARDHAT_NETWORK=sepolia node upgrade/timeLockUpgrade.js
            cat  upgrade/upgrade_output_1710239287.245.json 
            cat ../fork5/deployment/deploy_output.json 



          ''')

