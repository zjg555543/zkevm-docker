git clone -b zjg/ut-validium https://github.com/okx/xlayer-erigon.git 
git clone -b zjg/ut-validium https://github.com/okx/xlayer-aggregator.git
git clone -b zjg/ut-validium https://github.com/okx/xlayer-synchronizer-l1.git
git clone -b zjg/ut-validium https://github.com/okx/xlayer-ethtx-manager.git
git clone -b zjg/ut-validium https://github.com/okx/xlayer-sequence-sender.git


echo -e "\nreplace (\n\tgithub.com/0xPolygonHermez/zkevm-ethtx-manager => ../xlayer-ethtx-manager\n\tgithub.com/0xPolygonHermez/zkevm-synchronizer-l1 => ../xlayer-synchronizer-l1\n)" >> xlayer-aggregator/go.mod

echo -e "\nreplace (\n\tgithub.com/0xPolygonHermez/zkevm-ethtx-manager => ../xlayer-ethtx-manager\n\tgithub.com/0xPolygonHermez/zkevm-synchronizer-l1 => ../xlayer-synchronizer-l1\n)" >> xlayer-sequence-sender/go.mod


docker build -t zkevm-aggregator -f ./Dockerfile.aggregator .
docker build -t zkevm-seqsender -f ./Dockerfile.seqsender .
