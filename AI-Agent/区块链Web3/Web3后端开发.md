---
title: Web3后端开发
aliases:
  - Web3 Backend Development
  - ethers.js
  - web3.py
  - The Graph
  - 区块链后端
tags:
  - blockchain
  - web3
  - ethersjs
  - web3py
  - the-graph
  - ipfs
  - backend
  - indexing
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: 原创
difficulty: intermediate
project: AI-Agent
---

# Web3 后端开发

## 概述

Web3 后端开发是连接区块链与前端应用的桥梁。本指南涵盖 ethers.js（JavaScript/TypeScript）、web3.py（Python）、The Graph（链上数据索引）和 IPFS（去中心化存储）的集成。

---

## 一、ethers.js v6

### 1.1 Provider 与 Signer

```javascript
const { ethers } = require("ethers");

// === Provider（只读连接） ===

// JSON-RPC Provider
const provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_API_KEY");

// WebSocket Provider（实时监听）
const wsProvider = new ethers.WebSocketProvider("wss://mainnet.infura.io/ws/v3/YOUR_API_KEY");

// 使用浏览器注入的 MetaMask
// 浏览器中: const provider = new ethers.BrowserProvider(window.ethereum);

// === Signer（签名交易） ===

// 从私钥创建（后端服务）
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// 从助记词创建
const mnemonicWallet = ethers.HDNodeWallet.fromMnemonic(
    ethers.Mnemonic.fromPhrase(process.env.MNEMONIC),
    "m/44'/60'/0'/0/0" // 第一个账户
);

// 浏览器中从 MetaMask 获取
// const signer = await provider.getSigner();

// === 基本查询 ===
async function basicQueries() {
    // 获取区块号
    const blockNumber = await provider.getBlockNumber();
    console.log("Current block:", blockNumber);

    // 获取 Gas 价格
    const feeData = await provider.getFeeData();
    console.log("Gas price:", ethers.formatUnits(feeData.gasPrice, "gwei"), "gwei");
    console.log("Max fee:", ethers.formatUnits(feeData.maxFeePerGas, "gwei"), "gwei");

    // 获取余额
    const balance = await provider.getBalance("0x742d35Cc6634C0532925a3b844Bc454e4438f44e");
    console.log("Balance:", ethers.formatEther(balance), "ETH");

    // 获取网络信息
    const network = await provider.getNetwork();
    console.log("Chain ID:", network.chainId.toString());
    console.log("Network name:", network.name);

    // 获取交易
    const tx = await provider.getTransaction("0x...");
    console.log("TX:", tx);

    // 获取交易回执
    const receipt = await provider.getTransactionReceipt("0x...");
    console.log("Status:", receipt?.status);
    console.log("Gas used:", receipt?.gasUsed.toString());
}

// === 监听事件 ===
async function listenToEvents() {
    // 监听新区块
    wsProvider.on("block", (blockNumber) => {
        console.log("New block:", blockNumber);
    });

    // 监听 pending 交易
    wsProvider.on("pending", (txHash) => {
        console.log("Pending TX:", txHash);
    });

    // 监听特定地址的事件
    const contract = new ethers.Contract(contractAddress, abi, wsProvider);
    contract.on("Transfer", (from, to, value, event) => {
        console.log(`Transfer: ${ethers.formatEther(value)} ETH from ${from} to ${to}`);
        console.log("Block:", event.log.blockNumber);
    });

    // 一次性过滤器
    const filter = contract.filters.Transfer(null, "0x742d35Cc6634C0532925a3b844Bc454e4438f44e");
    const events = await contract.queryFilter(filter, -1000); // 最近 1000 个区块
    console.log(`Found ${events.length} Transfer events`);
}
```

### 1.2 合约交互

```javascript
const { ethers } = require("ethers");

const provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_API_KEY");
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// ERC-20 ABI
const erc20Abi = [
    "function name() view returns (string)",
    "function symbol() view returns (string)",
    "function decimals() view returns (uint8)",
    "function totalSupply() view returns (uint256)",
    "function balanceOf(address) view returns (uint256)",
    "function transfer(address to, uint256 amount) returns (bool)",
    "function approve(address spender, uint256 amount) returns (bool)",
    "function allowance(address owner, address spender) view returns (uint256)",
    "event Transfer(address indexed from, address indexed to, uint256 value)",
    "event Approval(address indexed owner, address indexed spender, uint256 value)",
];

// 只读合约实例（Provider）
const tokenRead = new ethers.Contract(tokenAddress, erc20Abi, provider);

// 可写合约实例（Signer）
const tokenWrite = new ethers.Contract(tokenAddress, erc20Abi, wallet);

async function interactWithContract() {
    // 读取数据
    const name = await tokenRead.name();
    const symbol = await tokenRead.symbol();
    const decimals = await tokenRead.decimals();
    const totalSupply = await tokenRead.totalSupply();
    const balance = await tokenRead.balanceOf(wallet.address);

    console.log(`${name} (${symbol})`);
    console.log("Decimals:", decimals);
    console.log("Total supply:", ethers.formatUnits(totalSupply, decimals));
    console.log("Balance:", ethers.formatUnits(balance, decimals));

    // 写入数据（需要 Signer）
    const amount = ethers.parseUnits("100", decimals);

    // 转账
    const tx = await tokenWrite.transfer("0xRecipient...", amount);
    console.log("TX hash:", tx.hash);

    // 等待确认
    const receipt = await tx.wait();
    console.log("Confirmed in block:", receipt.blockNumber);
    console.log("Gas used:", receipt.gasUsed.toString());

    // Approve
    const approveTx = await tokenWrite.approve(spenderAddress, amount);
    await approveTx.wait();
}

// === 估算 Gas ===
async function estimateGas() {
    const amount = ethers.parseUnits("100", 18);

    // 估算 gas limit
    const gasEstimate = await tokenWrite.transfer.estimateGas(recipientAddress, amount);
    console.log("Estimated gas:", gasEstimate.toString());

    // 获取当前 gas 价格
    const feeData = await provider.getFeeData();

    // EIP-1559 交易
    const tx = await tokenWrite.transfer(recipientAddress, amount, {
        maxFeePerGas: feeData.maxFeePerGas,
        maxPriorityFeePerGas: feeData.maxPriorityFeePerGas,
        gasLimit: gasEstimate,
    });

    console.log("TX:", tx.hash);
}
```

### 1.3 使用 TypeScript 类型化合约

```typescript
import { ethers, Contract, BrowserProvider, JsonRpcProvider } from "ethers";
import type { TypedContract, EventLog } from "ethers";

// ABI 定义（使用 human-readable ABI）
const tokenAbi = [
    "function name() view returns (string)",
    "function symbol() view returns (string)",
    "function balanceOf(address owner) view returns (uint256)",
    "function transfer(address to, uint256 amount) returns (bool)",
    "event Transfer(address indexed from, address indexed to, uint256 value)",
] as const;

interface TokenContract extends TypedContract {
    name(): Promise<string>;
    symbol(): Promise<string>;
    balanceOf(owner: string): Promise<bigint>;
    transfer(to: string, amount: bigint): Promise<ContractTransactionResponse>;
    filters: {
        Transfer(from?: string | null, to?: string | null): TypedEventFilter;
    };
}

class TokenService {
    private contract: TokenContract;
    private provider: JsonRpcProvider;

    constructor(address: string, provider: JsonRpcProvider) {
        this.provider = provider;
        this.contract = new ethers.Contract(address, tokenAbi, provider) as unknown as TokenContract;
    }

    async getBalance(address: string): Promise<string> {
        const balance = await this.contract.balanceOf(address);
        return ethers.formatEther(balance);
    }

    async getTransferHistory(address: string, fromBlock: number = -10000): Promise<TransferEvent[]> {
        const filter = this.contract.filters.Transfer(null, address);
        const events = await this.contract.queryFilter(filter, fromBlock);

        return events.map((event) => {
            const log = event as EventLog;
            return {
                from: log.args[0],
                to: log.args[1],
                value: ethers.formatEther(log.args[2]),
                blockNumber: log.blockNumber,
                txHash: log.transactionHash,
            };
        });
    }

    onTransfer(callback: (from: string, to: string, value: bigint) => void) {
        this.contract.on("Transfer", (from, to, value) => {
            callback(from, to, value);
        });
    }
}

interface TransferEvent {
    from: string;
    to: string;
    value: string;
    blockNumber: number;
    txHash: string;
}
```

---

## 二、web3.py（Python）

### 2.1 基本使用

```python
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
import json
import os

# 连接到以太坊节点
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_API_KEY"))

# 连接到本地节点（如 Hardhat / Ganache）
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# 连接到 WebSocket
# w3 = Web3(Web3.WebSocketProvider("wss://mainnet.infura.io/ws/v3/YOUR_API_KEY"))

# 检查连接
print("Connected:", w3.is_connected())
print("Chain ID:", w3.eth.chain_id)
print("Latest block:", w3.eth.block_number)

# === 地址与余额 ===
address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
balance = w3.eth.get_balance(address)
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")

# 地址校验与转换
checksum_addr = Web3.to_checksum_address("0x742d35cc6634c0532925a3b844bc454e4438f44e")
print("Valid:", Web3.is_checksum_address(checksum_addr))

# === Gas 价格 ===
gas_price = w3.eth.gas_price
print(f"Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")

# EIP-1559 fee data
block = w3.eth.get_block("latest")
base_fee = block["baseFeePerGas"]
print(f"Base fee: {w3.from_wei(base_fee, 'gwei')} gwei")

# === 交易 ===
# 发送原生 ETH
private_key = os.getenv("PRIVATE_KEY")
account = Account.from_key(private_key)

tx = {
    "to": "0xRecipientAddress",
    "value": w3.to_wei(0.1, "ether"),
    "gas": 21000,
    "gasPrice": gas_price,
    "nonce": w3.eth.get_transaction_count(account.address),
    "chainId": w3.eth.chain_id,
}

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"TX Hash: {tx_hash.hex()}")
print(f"Status: {receipt['status']}")  # 1 = success, 0 = failure
print(f"Gas used: {receipt['gasUsed']}")
```

### 2.2 合约交互

```python
from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_API_KEY"))

# 加载 ABI
with open("abis/ERC20.json", "r") as f:
    erc20_abi = json.load(f)["abi"]

# 合约实例
token_address = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0CE3606eB48")  # USDC
token = w3.eth.contract(address=token_address, abi=erc20_abi)

# 读取数据
name = token.functions.name().call()
symbol = token.functions.symbol().call()
decimals = token.functions.decimals().call()
total_supply = token.functions.totalSupply().call()

print(f"{name} ({symbol})")
print(f"Decimals: {decimals}")
print(f"Total supply: {total_supply / 10**decimals}")

# 查询余额
balance = token.functions.balanceOf(
    Web3.to_checksum_address("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
).call()
print(f"Balance: {balance / 10**decimals} {symbol}")

# === 发送交易 ===
private_key = os.getenv("PRIVATE_KEY")
account = Account.from_key(private_key)

def send_token(to_address, amount):
    to_address = Web3.to_checksum_address(to_address)
    amount_in_wei = int(amount * 10**decimals)

    # 构建交易
    nonce = w3.eth.get_transaction_count(account.address)
    tx = token.functions.transfer(
        to_address,
        amount_in_wei
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 100000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id,
    })

    # 签名并发送
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "tx_hash": tx_hash.hex(),
        "status": receipt["status"],
        "gas_used": receipt["gasUsed"],
    }

# === 事件日志 ===
def get_transfer_events(from_block, to_block="latest"):
    # 创建事件过滤器
    transfer_filter = token.events.Transfer.create_filter(
        from_block=from_block,
        to_block=to_block,
    )

    events = transfer_filter.get_all_entries()
    results = []

    for event in events:
        results.append({
            "from": event["args"]["from"],
            "to": event["args"]["to"],
            "value": event["args"]["value"] / 10**decimals,
            "block": event["blockNumber"],
            "tx_hash": event["transactionHash"].hex(),
        })

    return results

# === 监听新事件 ===
def listen_to_transfers():
    transfer_filter = token.events.Transfer.create_filter(
        from_block="latest"
    )

    print("Listening for Transfer events...")
    while True:
        for event in transfer_filter.get_new_entries():
            print(f"Transfer: {event['args']['value'] / 10**decimals} {symbol} "
                  f"from {event['args']['from']} to {event['args']['to']}")
        time.sleep(2)
```

### 2.3 使用 web3.py 开发 API 服务

```python
# FastAPI + Web3 后端服务
from fastapi import FastAPI, HTTPException
from web3 import Web3
from pydantic import BaseModel
import json, os

app = FastAPI(title="Web3 API Service")

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

with open("abis/Token.json") as f:
    token_abi = json.load(f)["abi"]

TOKEN_ADDRESS = Web3.to_checksum_address(os.getenv("TOKEN_ADDRESS"))
token = w3.eth.contract(address=TOKEN_ADDRESS, abi=token_abi)

class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    private_key: str

@app.get("/api/balance/{address}")
async def get_balance(address: str):
    if not Web3.is_address(address):
        raise HTTPException(status_code=400, detail="Invalid address")

    addr = Web3.to_checksum_address(address)
    eth_balance = w3.eth.get_balance(addr)
    token_balance = token.functions.balanceOf(addr).call()
    decimals = token.functions.decimals().call()

    return {
        "address": addr,
        "eth_balance": w3.from_wei(eth_balance, "ether"),
        "token_balance": token_balance / 10**decimals,
    }

@app.post("/api/transfer")
async def transfer_tokens(req: TransferRequest):
    try:
        account = Account.from_key(req.private_key)
        decimals = token.functions.decimals().call()
        amount_wei = int(req.amount * 10**decimals)

        nonce = w3.eth.get_transaction_count(account.address)
        tx = token.functions.transfer(
            Web3.to_checksum_address(req.to_address),
            amount_wei
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id,
        })

        signed = w3.eth.account.sign_transaction(tx, req.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "tx_hash": tx_hash.hex(),
            "status": "success" if receipt["status"] == 1 else "failed",
            "gas_used": receipt["gasUsed"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/token/info")
async def token_info():
    return {
        "name": token.functions.name().call(),
        "symbol": token.functions.symbol().call(),
        "decimals": token.functions.decimals().call(),
        "total_supply": token.functions.totalSupply().call(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 三、The Graph（链上数据索引）

### 3.1 创建 Subgraph

```bash
# 安装 Graph CLI
npm install -g @graphprotocol/graph-cli

# 初始化 Subgraph
graph init --product hosted-service \
  --node https://api.thegraph.com/deploy/ \
  --network mainnet \
  your-username/my-subgraph

# 目录结构
# my-subgraph/
# ├── abis/
# │   └── Token.json
# ├── src/
# │   └── mapping.ts
# ├── schema.graphql
# ├── subgraph.yaml
# └── package.json
```

### 3.2 Schema 定义

```graphql
# schema.graphql

type Token @entity {
  id: ID!  # 合约地址
  name: String!
  symbol: String!
  decimals: Int!
  totalSupply: BigInt!
}

type Account @entity {
  id: ID!  # 钱包地址
  balances: [AccountToken!]! @derivedFrom(field: "account")
  totalTransfersIn: BigInt!
  totalTransfersOut: BigInt!
  firstSeenAt: Int!
  lastActiveAt: Int!
}

type AccountToken @entity {
  id: ID!  # accountId-tokenId
  account: Account!
  token: Token!
  amount: BigInt!
  amountFormatted: BigDecimal!
}

type Transfer @entity {
  id: ID!  # txHash-logIndex
  from: Account!
  to: Account!
  token: Token!
  amount: BigInt!
  amountFormatted: BigDecimal!
  blockNumber: Int!
  blockTimestamp: Int!
  transactionHash: String!
}

type TransferCounter @entity {
  id: ID!  # token address
  count: BigInt!
  totalVolume: BigInt!
}
```

### 3.3 Subgraph 配置

```yaml
# subgraph.yaml
specVersion: 1.0.0
description: Token Transfer Subgraph
repository: https://github.com/your-username/my-subgraph
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum
    name: Token
    network: mainnet
    source:
      address: "0xA0b86991c6218b36c1d19D4a2e9Eb0CE3606eB48"
      abi: Token
      startBlock: 6081276
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities:
        - Token
        - Account
        - Transfer
      abis:
        - name: Token
          file: ./abis/Token.json
      eventHandlers:
        - event: Transfer(indexed address,indexed address,uint256)
          handler: handleTransfer
      file: ./src/mapping.ts
```

### 3.4 Mapping（AssemblyScript）

```typescript
// src/mapping.ts
import {
  ERC20,
  Transfer as TransferEvent,
} from "../generated/Token/ERC20";
import {
  Token,
  Account,
  AccountToken,
  Transfer,
  TransferCounter,
} from "../generated/schema";
import { BigInt, BigDecimal } from "@graphprotocol/graph-ts";

const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";

function getOrCreateToken(event: TransferEvent): Token {
  let token = Token.load(event.address.toHex());
  if (token == null) {
    let contract = ERC20.bind(event.address);
    token = new Token(event.address.toHex());
    token.name = contract.name();
    token.symbol = contract.symbol();
    token.decimals = contract.decimals();
    token.totalSupply = contract.totalSupply();
    token.save();
  }
  return token;
}

function getOrCreateAccount(address: string, timestamp: i32): Account {
  let account = Account.load(address);
  if (account == null) {
    account = new Account(address);
    account.totalTransfersIn = BigInt.fromI32(0);
    account.totalTransfersOut = BigInt.fromI32(0);
    account.firstSeenAt = timestamp;
    account.lastActiveAt = timestamp;
    account.save();
  }
  return account;
}

function getOrCreateAccountToken(
  accountId: string,
  tokenId: string,
  decimals: number
): AccountToken {
  let id = accountId + "-" + tokenId;
  let accountToken = AccountToken.load(id);
  if (accountToken == null) {
    accountToken = new AccountToken(id);
    accountToken.account = accountId;
    accountToken.token = tokenId;
    accountToken.amount = BigInt.fromI32(0);
    accountToken.amountFormatted = BigDecimal.fromString("0");
    accountToken.save();
  }
  return accountToken;
}

export function handleTransfer(event: TransferEvent): void {
  let token = getOrCreateToken(event);
  let decimals = token.decimals;

  let fromAddress = event.params.from.toHex();
  let toAddress = event.params.to.toHex();

  let fromAccount = getOrCreateAccount(fromAddress, event.block.timestamp);
  let toAccount = getOrCreateAccount(toAddress, event.block.timestamp);

  fromAccount.totalTransfersOut = fromAccount.totalTransfersOut.plus(
    BigInt.fromI32(1)
  );
  fromAccount.lastActiveAt = event.block.timestamp;
  fromAccount.save();

  toAccount.totalTransfersIn = toAccount.totalTransfersIn.plus(
    BigInt.fromI32(1)
  );
  toAccount.lastActiveAt = event.block.timestamp;
  toAccount.save();

  // 更新余额
  if (fromAddress != ZERO_ADDRESS) {
    let fromBalance = getOrCreateAccountToken(fromAddress, token.id, decimals);
    fromBalance.amount = fromBalance.amount.minus(event.params.value);
    fromBalance.amountFormatted = fromBalance.amount.toBigDecimal() /
      BigInt.fromI32(10).pow(decimals as i32).toBigDecimal();
    fromBalance.save();
  }

  if (toAddress != ZERO_ADDRESS) {
    let toBalance = getOrCreateAccountToken(toAddress, token.id, decimals);
    toBalance.amount = toBalance.amount.plus(event.params.value);
    toBalance.amountFormatted = toBalance.amount.toBigDecimal() /
      BigInt.fromI32(10).pow(decimals as i32).toBigDecimal();
    toBalance.save();
  }

  // 保存 Transfer 实体
  let transferId = event.transaction.hash.toHex() + "-" +
    event.logIndex.toString();
  let transfer = new Transfer(transferId);
  transfer.from = fromAddress;
  transfer.to = toAddress;
  transfer.token = token.id;
  transfer.amount = event.params.value;
  transfer.amountFormatted = event.params.value.toBigDecimal() /
    BigInt.fromI32(10).pow(decimals as i32).toBigDecimal();
  transfer.blockNumber = event.block.number.toI32();
  transfer.blockTimestamp = event.block.timestamp.toI32();
  transfer.transactionHash = event.transaction.hash.toHex();
  transfer.save();

  // 更新计数器
  let counterId = token.id;
  let counter = TransferCounter.load(counterId);
  if (counter == null) {
    counter = new TransferCounter(counterId);
    counter.count = BigInt.fromI32(0);
    counter.totalVolume = BigInt.fromI32(0);
  }
  counter.count = counter.count.plus(BigInt.fromI32(1));
  counter.totalVolume = counter.totalVolume.plus(event.params.value);
  counter.save();
}
```

### 3.5 部署与查询

```bash
# 生成代码
graph codegen

# 构建
graph build

# 部署到 Hosted Service（已弃用，请使用 Decentralized Network）
graph deploy --node https://api.thegraph.com/deploy/ \
  your-username/my-subgraph

# 部署到 Decentralized Network
graph create --node http://localhost:8020/ your-username/my-subgraph
graph deploy --node http://localhost:8020/ --ipfs http://localhost:5001/ \
  your-username/my-subgraph
```

```javascript
// 前端查询 GraphQL API
const { graphql } = require("@graphprotocol/graph-ts");

const GRAPHQL_ENDPOINT = "https://api.thegraph.com/subgraphs/name/your-username/my-subgraph";

// 获取某地址的所有转账
async function getTransfersByAddress(address) {
    const query = `
        query GetTransfers($address: ID!) {
            transfers(
                where: { or: [{ from: $address }, { to: $address }] }
                orderBy: blockTimestamp
                orderDirection: desc
                first: 100
            ) {
                id
                from { id }
                to { id }
                amount
                amountFormatted
                blockNumber
                blockTimestamp
                transactionHash
            }
        }
    `;

    const response = await fetch(GRAPHQL_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables: { address } }),
    });

    const { data } = await response.json();
    return data.transfers;
}

// 获取 Top 持有者
async function getTopHolders(tokenAddress, limit = 100) {
    const query = `
        query GetTopHolders($tokenAddress: ID!, $limit: Int) {
            accountTokens(
                where: { token: $tokenAddress, amount_gt: 0 }
                orderBy: amount
                orderDirection: desc
                first: $limit
            ) {
                account { id }
                amount
                amountFormatted
            }
        }
    `;

    const response = await fetch(GRAPHQL_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables: { tokenAddress, limit } }),
    });

    const { data } = await response.json();
    return data.accountTokens;
}

// 获取每日交易量
async function getDailyVolume(tokenAddress) {
    const query = `
        query GetDailyVolume($tokenAddress: ID!) {
            transferEntities: transferCounters(
                where: { id: $tokenAddress }
            ) {
                count
                totalVolume
            }
        }
    `;

    const response = await fetch(GRAPHQL_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables: { tokenAddress } }),
    });

    const { data } = await response.json();
    return data.transferEntities[0];
}
```

---

## 四、IPFS 集成

### 4.1 使用 Helia（IPFS JavaScript 实现）

```javascript
// 使用 Helia（新版 IPFS JavaScript 实现，替代旧版 js-ipfs）
const { helia } = require("helia");
const { unixfs } = require("@helia/unixfs");
const { CID } = require("multiformats/cid");

async function ipfsExample() {
    // 创建 Helia 节点
    const node = await helia();
    const fs = unixfs(node);

    // === 添加文件 ===
    const fileContent = new TextEncoder().encode("Hello, IPFS!");
    const cid = await fs.addFile({
        path: "hello.txt",
        content: fileContent,
    });
    console.log("CID:", cid.toString());

    // === 读取文件 ===
    const text = await fs.cat(cid);
    console.log("Content:", new TextDecoder().decode(text));

    // === 添加目录 ===
    const entries = [
        { path: "my-folder/file1.txt", content: new TextEncoder().encode("Content 1") },
        { path: "my-folder/file2.txt", content: new TextEncoder().encode("Content 2") },
        { path: "my-folder/subfolder/file3.txt", content: new TextEncoder().encode("Content 3") },
    ];

    for await (const entry of fs.addAll(entries)) {
        console.log(`Added ${entry.path}: ${entry.cid}`);
    }

    // === Pin 文件 ===
    await node.pins.add(cid);
    console.log("Pinned:", cid.toString());

    await node.stop();
}

// === 通过 Gateway 访问 ===
function getGatewayURL(cid, gateway = "https://ipfs.io") {
    return `${gateway}/ipfs/${cid}`;
}

// 常用 Gateway
const GATEWAYS = [
    "https://ipfs.io",
    "https://cloudflare-ipfs.com",
    "https://gateway.pinata.cloud",
    "https://dweb.link",
];
```

### 4.2 使用 kubo-rpc-client

```javascript
// 使用 kubo (go-ipfs) RPC 客户端
const { KuboRPCClient } = require("kubo-rpc-client");

// 连接到本地 IPFS 节点
const ipfs = KuboRPCClient.create({ url: "http://127.0.0.1:5001" });

async function kuboExample() {
    // 添加文件
    const result = await ipfs.add({
        path: "hello.txt",
        content: "Hello from Kubo!",
    });
    console.log("CID:", result.cid.toString());

    // 读取文件
    const chunks = [];
    for await (const chunk of ipfs.cat(result.cid)) {
        chunks.push(chunk);
    }
    const content = Buffer.concat(chunks).toString();
    console.log("Content:", content);

    // 添加 JSON
    const jsonData = JSON.stringify({ name: "Token #1", attributes: [] });
    const jsonResult = await ipfs.add(jsonData);
    console.log("JSON CID:", jsonResult.cid.toString());

    // Pin
    await ipfs.pin.add(result.cid);

    // 列出 pinned 内容
    for await (const { cid } of ipfs.pin.ls()) {
        console.log("Pinned:", cid.toString());
    }
}
```

---

## 五、完整 DApp 后端架构

### 5.1 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Next.js)                  │
├────────────┬─────────────┬──────────────┬───────────────────────┤
│  ethers.js │  wagmi      │  Apollo      │  REST API             │
│  (链交互)  │  (Hooks)    │  GraphQL     │  (业务逻辑)           │
├────────────┴─────────────┴──────────────┴───────────────────────┤
│                     Backend Service (Node.js)                    │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ ethers   │  │ The Graph │  │  IPFS      │  │  Database    │ │
│  │ Provider │  │  Client   │  │  Client    │  │  (Postgres)  │ │
│  └──────────┘  └───────────┘  └────────────┘  └──────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┤
│  │                    Message Queue (Redis)                      │
│  │         Event Listener ───→ Job Processor                    │
│  └──────────────────────────────────────────────────────────────┘
├──────────────────────────────────────────────────────────────────┤
│                    Blockchain Infrastructure                     │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Ethereum │  │  IPFS     │  │ The Graph  │  │  Alchemy/    │ │
│  │ Node     │  │  Network  │  │  Node      │  │  Infura      │ │
│  └──────────┘  └───────────┘  └────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 事件监听微服务

```javascript
// services/eventListener.js
const { ethers } = require("ethers");
const Redis = require("ioredis");
const { Pool } = require("pg");

// 配置
const provider = new ethers.WebSocketProvider(process.env.WS_RPC_URL);
const redis = new Redis(process.env.REDIS_URL);
const pg = new Pool({ connectionString: process.env.DATABASE_URL });

// 合约 ABI
const contractAbi = [
    "event Transfer(address indexed from, address indexed to, uint256 value)",
    "event Approval(address indexed owner, address indexed spender, uint256 value)",
];

const contract = new ethers.Contract(process.env.CONTRACT_ADDRESS, contractAbi, provider);

// 从上次处理的区块继续
async function getLastProcessedBlock() {
    const result = await redis.get("lastProcessedBlock");
    return result ? parseInt(result) : await provider.getBlockNumber() - 10;
}

// 处理 Transfer 事件
async function handleTransferEvent(from, to, value, event) {
    const job = {
        type: "TRANSFER",
        data: {
            from,
            to,
            value: value.toString(),
            txHash: event.log.transactionHash,
            blockNumber: event.log.blockNumber,
            logIndex: event.log.index,
        },
    };

    // 推送到 Redis 队列
    await redis.lpush("eventQueue", JSON.stringify(job));
    console.log(`Queued: Transfer ${ethers.formatEther(value)} from ${from} to ${to}`);
}

// 主循环
async function startEventListener() {
    let lastBlock = await getLastProcessedBlock();

    // 使用过滤器批量获取事件（更可靠）
    setInterval(async () => {
        try {
            const currentBlock = await provider.getBlockNumber();

            if (currentBlock > lastBlock) {
                const events = await contract.queryFilter("Transfer", lastBlock + 1, currentBlock);

                for (const event of events) {
                    const decoded = contract.interface.parseLog(event);
                    await handleTransferEvent(
                        decoded.args.from,
                        decoded.args.to,
                        decoded.args.value,
                        { log: event }
                    );
                }

                lastBlock = currentBlock;
                await redis.set("lastProcessedBlock", lastBlock);
                console.log(`Processed up to block ${currentBlock}, ${events.length} events`);
            }
        } catch (error) {
            console.error("Event listener error:", error);
        }
    }, 5000); // 每 5 秒检查一次

    // 实时监听（补充）
    contract.on("Transfer", (from, to, value, event) => {
        handleTransferEvent(from, to, value, event);
    });
}

// Job Processor（消费者）
async function processJobs() {
    while (true) {
        try {
            const jobData = await redis.brpop("eventQueue", 0);
            if (!jobData) continue;

            const job = JSON.parse(jobData[1]);

            // 写入数据库
            await pg.query(
                `INSERT INTO transfers (tx_hash, from_addr, to_addr, value, block_number, log_index)
                 VALUES ($1, $2, $3, $4, $5, $6)
                 ON CONFLICT (tx_hash, log_index) DO NOTHING`,
                [
                    job.data.txHash,
                    job.data.from,
                    job.data.to,
                    job.data.value,
                    job.data.blockNumber,
                    job.data.logIndex,
                ]
            );

            console.log(`Processed job: ${job.type} ${job.data.txHash}`);
        } catch (error) {
            console.error("Job processing error:", error);
            // 重新入队
            await redis.lpush("eventQueue", JSON.stringify(job));
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
}

startEventListener();
processJobs();
```

---

## 六、最佳实践

### 6.1 错误处理与重试

```javascript
// 带指数退避的重试机制
async function withRetry(fn, maxRetries = 5, baseDelay = 1000) {
    let lastError;

    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            // 不可重试的错误
            if (error.code === "CALL_EXCEPTION" || error.code === "NONCE_EXPIRED") {
                throw error;
            }

            // 指数退避
            const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
            console.warn(`Retry ${i + 1}/${maxRetries} after ${delay}ms: ${error.message}`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError;
}

// 使用
const receipt = await withRetry(() =>
    provider.getTransactionReceipt(txHash)
);

// Nonce 管理
class NonceManager {
    constructor(provider, address) {
        this.provider = provider;
        this.address = address;
        this.localNonce = null;
        this.lock = Promise.resolve();
    }

    async getNonce() {
        // 使用锁防止并发问题
        return this.lock.then(async () => {
            if (this.localNonce === null) {
                this.localNonce = await this.provider.getTransactionCount(this.address, "pending");
            }
            const nonce = this.localNonce;
            this.localNonce++;
            return nonce;
        });
    }

    async reset() {
        this.localNonce = await this.provider.getTransactionCount(this.address, "pending");
    }
}
```

### 6.2 安全清单

| 类别 | 最佳实践 |
|------|----------|
| **私钥管理** | 使用环境变量 / KMS / HSM，不硬编码 |
| **Nonce 管理** | 使用 NonceManager 防止交易卡住 |
| **Gas 估算** | 始终估算 gas limit 并加 20% buffer |
| **错误处理** | 区分可重试和不可重试错误 |
| **WebSocket 重连** | 实现自动重连和心跳检测 |
| **RPC 负载均衡** | 多个 RPC 提供商轮询 / failover |
| **速率限制** | 对公共 API 实施速率限制 |
| **输入验证** | 校验地址格式、金额范围 |
| **日志审计** | 记录所有链上交易 |
| **监控告警** | 交易失败、大额转账告警 |

---

## 相关页面

- [[智能合约开发]] - Solidity 合约编写
- [[DeFi协议指南]] - DeFi 后端集成
- [[NFT开发指南]] - NFT 索引与 API
- [[Layer2与扩容方案]] - L2 后端适配
