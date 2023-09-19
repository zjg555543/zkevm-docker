
## requirements

* x86
* `go` <https://go.dev/doc/install>
* `docker` <https://www.docker.com/get-started>
* `docker-compose` <https://docs.docker.com/compose/install/>


## build

```
mkdir zkevm
cd zkevm
git clone -b zjg/validium https://github.com/zjg555543/zkevm-docker.git
cd zkevm-docker

docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a

# download the code
cd ../
git clone https://github.com/0xPolygon/cdk-validium-node
git clone https://github.com/0xPolygon/cdk-validium-contracts.git
git clone https://github.com/0xPolygon/cdk-data-availability.git

cd ./cdk-validium-node
make build-docker
cd -

cd cdk-data-availability
make build-docker
cd -

cd ./cdk-validium-contracts
rm deployment/deploy_output.json 
git reset --hard
cp ../zkevm-docker/config/deploy_parameters.json.example deployment/deploy_parameters.json
cp ../zkevm-docker/config/contract_env_example .env
cp ../zkevm-docker/config/1_createGenesis.js deployment/1_createGenesis.js 

cd -
cd zkevm-docker 
docker-compose up -d cdk-validium-state-db
docker-compose up -d cdk-validium-pool-db
docker-compose up -d cdk-validium-event-db
docker-compose up -d cdk-data-availability-db
docker-compose up -d cdk-validium-mock-l1-network
sleep 3


# with metamask
transfer 0x2ecf31ece36ccac2d3222a303b1409233ecbb225 100ETH from 0xFABB0ac9d68B0B445fB7357272Ff202C5651694a（0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b1） on L1

cd ../cdk-validium-contracts
npm i
npm run deploy:testnet:CDKValidium:localhost


cast call --rpc-url http://127.0.01:8545 0x4eBfE2aC5eC9E2ac20e81aF97C726b8f1E07485a 'function getAmountOfMembers() public returns (uint256)'

cast send --legacy --from 0x2ECF31eCe36ccaC2d3222A303b1409233ECBB225 --private-key 0xde3ca643a52f5543e84ba984c4419ff40dbabd0e483c31c1d09fee8168d68e38 --rpc-url http://127.0.0.1:8545 0x4eBfE2aC5eC9E2ac20e81aF97C726b8f1E07485a 'function setupCommittee(uint256 _requiredAmountOfSignatures, string[] urls, bytes addrsBytes) returns()' 1 [http://cdk-data-availability:8444] 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266


cat deployment/genesis.json
cat deployment/deploy_output.json 
cd -


# modify genesisBlockNumber
config/test.genesis.config.json -> genesisBlockNumber

docker-compose up -d cdk-data-availability
docker-compose up -d cdk-validium-approve 
docker-compose up -d cdk-validium-prover
sleep 3
docker-compose up -d cdk-validium-sync
sleep 3

docker-compose up -d cdk-validium-eth-tx-manager
docker-compose up -d cdk-validium-sequencer
docker-compose up -d cdk-validium-sequence-sender
docker-compose up -d cdk-validium-l2gaspricer
docker-compose up -d cdk-validium-aggregator
docker-compose up -d cdk-validium-json-rpc

# you can send some txs by 0x2ECF31eCe36ccaC2d3222A303b1409233ECBB225 on L2


```

## Accounts
| Address | Private Key |
|---|---|
| 0x2ECF31eCe36ccaC2d3222A303b1409233ECBB225 | 0xde3ca643a52f5543e84ba984c4419ff40dbabd0e483c31c1d09fee8168d68e38 |
| 0xFABB0ac9d68B0B445fB7357272Ff202C5651694a | 0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b1 |


## Metamask

> Metamask requires the network to be running while configuring it, so make sure your network is running before starting.

To configure your Metamask to use your local environment, follow these steps:

1. Log in to your Metamask wallet
2. Click on your account picture and then on Settings
3. On the left menu, click on Networks
4. Click on `Add Network` button
5. Fill up the L2 network information
    1. `Network Name:` Polygon zkEVM - Local
    2. `New RPC URL:` <http://localhost:8123>
    3. `ChainID:` 1001
    4. `Currency Symbol:` ETH
    5. `Block Explorer URL:` <http://localhost:4000>
6. Click on Save
7. Click on `Add Network` button
8. Fill up the L1 network information
    1. `Network Name:` Geth - Local
    2. `New RPC URL:` <http://localhost:8545>
    3. `ChainID:` 1337
    4. `Currency Symbol:` ETH
9. Click on Save

bridge ui <http://localhost:8090/>  
