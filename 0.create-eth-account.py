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