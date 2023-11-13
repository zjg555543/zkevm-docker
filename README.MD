
## requirements

* x86
* `go` <https://go.dev/doc/install>
* `docker` <https://www.docker.com/get-started>
* `docker-compose` <https://docs.docker.com/compose/install/>


## build

```
docker stop $(docker ps -aq); docker rm $(docker ps -aq);docker ps -a


cd ../

#rm -rf ./x1-contracts

git clone -b v0.1.2 https://github.com/0xPolygonHermez/x1-node.git
git clone -b v0.1.0 https://github.com/0xPolygonHermez/x1-bridge-service.git
git clone -b v1.1.0-fork.4 https://github.com/0xPolygonHermez/x1-contracts

cd ./x1-node
make build-docker
cd -

cd ./x1-bridge-service
make build-docker

cd-
cd x1-bridge-ui
cp ../x1-docker/ui/tokens.context.tsx src/contexts/tokens.context.tsx
docker build . -t x1-bridge-ui

cd -
cd ./x1-contracts
rm deployment/deploy_output.json 
git reset  --hard

cp ../x1-docker/config/deploy_parameters.json deployment/deploy_parameters.json
cp ../x1-docker/config/contract_env_example .env
# cp ../x1-docker/config/1_createGenesis.js deployment/1_createGenesis.js 

cd -
cd x1-docker  

docker-compose up -d x1-state-db
docker-compose up -d x1-pool-db
docker-compose up -d x1-event-db
docker-compose up -d x1-bridge-db
docker-compose up -d x1-mock-l1-network
sleep 3


## TODO trans eth on L1, 0x2ecf31ece36ccac2d3222a303b1409233ecbb225

cd ../x1-contracts
npm i
npm run deploy:testnet:ZkEVM:localhost

cat deployment/deploy_output.json 
cat deployment/genesis.json

### TODO respace GenBlockNumber, genesisBlockNumber by block chain

cd -

#need start after 
docker-compose up -d x1-approve 
docker-compose up -d x1-prover
sleep 3
docker-compose up -d x1-sync
sleep 3

docker-compose up -d x1-eth-tx-manager
docker-compose up -d x1-sequencer
docker-compose up -d x1-sequence-sender
docker-compose up -d x1-l2gaspricer
docker-compose up -d x1-aggregator
docker-compose up -d x1-json-rpc

docker-compose up -d x1-explorer-json-rpc
docker-compose up -d x1-explorer-l1
docker-compose up -d x1-explorer-l2
docker-compose up -d x1-bridge-service
docker-compose up -d x1-bridge-ui

docker ps -a

docker-compose logs --tail 10 -f

# 安装 cast call
https://book.getfoundry.sh/getting-started/installation

# 查看是否支持branch
cast call --rpc-url http://127.0.0.1:8545 0xa44006fb08EA248cEd6355d596372Ba05e93463a 'function isForcedBatchDisallowed() view returns(bool)'

# 设置为false
cast send --legacy --from 0x2ECF31eCe36ccaC2d3222A303b1409233ECBB225 --private-key 0xde3ca643a52f5543e84ba984c4419ff40dbabd0e483c31c1d09fee8168d68e38  --rpc-url http://127.0.0.1:8545 0xa44006fb08EA248cEd6355d596372Ba05e93463a 'function activateForceBatches() returns()'

# 启动approve设置金额
Provide L1 ETH to the Bridge

# 质押初始化
https://x1.polygon.technology/docs/setup-x1/#provide-l1-eth-to-the-bridge

# clamim 质押
https://x1.polygon.technology/docs/setup-x1/#claim-your-l2-zketh


```

## Deployer Account

| Address | Private Key |
|---|---|
| 0x2ECF31eCe36ccaC2d3222A303b1409233ECBB225 | 0xde3ca643a52f5543e84ba984c4419ff40dbabd0e483c31c1d09fee8168d68e38 |

## Sequencer Account

| Address | Private Key |
|---|---|
| 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 | 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 |

## Sequencer Account

| Address | Private Key |
|---|---|
| 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 | 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d |

## Accounts

| Address | Private Key |
|---|---|
| 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC | 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a |
| 0x90F79bf6EB2c4f870365E785982E1f101E93b906 | 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6 |
| 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65 | 0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a |
| 0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc | 0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba |
| 0x976EA74026E726554dB657fA54763abd0C3a0aa9 | 0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e |
| 0x14dC79964da2C08b23698B3D3cc7Ca32193d9955 | 0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356 |
| 0x23618e81E3f5cdF7f54C3d65f7FBc0aBf5B21E8f | 0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97 |
| 0xa0Ee7A142d267C1f36714E4a8F75612F20a79720 | 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 |
| 0xBcd4042DE499D14e55001CcbB24a551F3b954096 | 0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897 |
| 0x71bE63f3384f5fb98995898A86B02Fb2426c5788 | 0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82 |
| 0xFABB0ac9d68B0B445fB7357272Ff202C5651694a | 0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b1 |
| 0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec | 0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd |
| 0xdF3e18d64BC6A983f673Ab319CCaE4f1a57C7097 | 0xc526ee95bf44d8fc405a158bb884d9d1238d99f0612e9f33d006bb0789009aaa |
| 0xcd3B766CCDd6AE721141F452C550Ca635964ce71 | 0x8166f546bab6da521a8369cab06c5d2b9e46670292d85c875ee9ec20e84ffb61 |
| 0x2546BcD3c84621e976D8185a91A922aE77ECEc30 | 0xea6c44ac03bff858b476bba40716402b03e41b8e97e276d1baec7c37d42484a0 |
| 0xbDA5747bFD65F08deb54cb465eB87D40e51B197E | 0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd |
| 0xdD2FD4581271e230360230F9337D5c0430Bf44C0 | 0xde9be858da4a475276426320d5e9262ecfc3ba460bfac56360bfa6c4c28b4ee0 |
| 0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199 | 0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e |


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
