import json
from eth_account import Account

Account.enable_unaudited_hdwallet_features()
account, mnemonic = Account.create_with_mnemonic()

# 获取账户地址
address = account.address

# 获取账户的私钥（注意：私钥非常敏感，请妥善保管）
private_key = account._private_key.hex()

# 打印结果
print("\n")
print(f"Address:        {address}")
print(f"Private Key:    {private_key}")
print(f"Mnemonic:       {mnemonic}")
print("\n")

# 构建包含账户信息的字典
account_info = {
    "address": address,
    "private_key": private_key,
    "mnemonic": mnemonic
}

# 将字典保存为 JSON 文件
json_file_path = 'account_info.json'  # 替换为你的实际 JSON 文件路径
with open(json_file_path, 'w') as json_file:
    json.dump(account_info, json_file, indent=2)