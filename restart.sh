docker-compose restart zkevm-state-db
docker-compose restart zkevm-mock-l1-network
sleep 1
docker-compose restart zkevm-prover
sleep 3
docker-compose restart zkevm-sequencer
docker-compose restart zkevm-aggregator
docker-compose restart zkevm-json-rpc
docker-compose restart zkevm-sync
docker-compose restart zkevm-bridge-service
docker-compose restart zkevm-bridge-ui