---
title: Layer2与扩容方案
aliases:
  - Layer 2 Scaling
  - L2
  - 扩容方案
  - Rollup
tags:
  - blockchain
  - layer2
  - rollup
  - scaling
  - plasma
  - sidechain
  - state-channel
  - optimism
  - arbitrum
  - zk
  - web3
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: 原创
difficulty: advanced
project: AI-Agent
---

# Layer2 与扩容方案

## 概述

以太坊主网（Layer 1）面临吞吐量瓶颈（约 15 TPS）和高 Gas 费用。Layer 2 扩容方案通过在链下处理交易，仅在主链上结算最终状态，实现高吞吐、低成本的交易体验。本指南涵盖 Rollup（Optimistic / ZK）、Plasma、侧链和状态通道。

### 扩容方案分类

```
┌─────────────────────────────────────────────────────────────────┐
│                    区块链扩容方案分类                              │
├──────────────────┬──────────────────────────────────────────────┤
│                  │  On-Chain (Layer 1)                          │
│   Layer 1 扩容   │  ├── 分片              │
│                  │  └── 状态膨胀控制 (State Expiry)             │
├──────────────────┼──────────────────────────────────────────────┤
│                  │  Off-Chain (Layer 2)                         │
│                  │  ├── Rollup                                  │
│                  │  │   ├── Optimistic Rollup (OP, Arbitrum)    │
│                  │  │   └── ZK Rollup (zkSync, StarkNet)        │
│   Layer 2 扩容   │  ├── Plasma                                  │
│                  │  ├── Sidechain (Polygon PoS, Gnosis Chain)   │
│                  │  └── State Channel (Lightning, Raiden)       │
├──────────────────┼──────────────────────────────────────────────┤
│                  │  Independent Chains                          │
│   其他方案       │  ├── Cosmos (IBC)                            │
│                  │  ├── Polkadot                                │
│                  │  └── Near (Sharding + DoomSlug)              │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## 一、Optimistic Rollup

### 1.1 工作原理

Optimistic Rollup 假设所有交易都是有效的（"乐观"），提交后有一个挑战期（通常 7 天）。在此期间任何人都可以提交欺诈证明 来挑战无效交易。

```
┌──────────────────────────────────────────────────────┐
│              Layer 1 (Ethereum)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Rollup Contract (Bridge / State Root)        │   │
│  │  ┌─────────────┐  ┌──────────────────────┐   │   │
│  │  │ Deposits    │  │ State Roots (Merkle) │   │   │
│  │  └─────────────┘  └──────────────────────┘   │   │
│  │  ┌─────────────┐  ┌──────────────────────┐   │   │
│  │  │ Withdrawals │  │ Fraud Proofs         │   │   │
│  │  └─────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└───────────────────────┬──────────────────────────────┘
                        │ 定期提交批次 (Batch)
┌───────────────────────▼──────────────────────────────┐
│              Layer 2 (Rollup Chain)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Sequencer│  │ Verifier │  │ Data     │           │
│  │ (排序器) │  │ (验证者) │  │ Avail.   │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│  Transactions: tx1 → tx2 → tx3 → ... → txN          │
└──────────────────────────────────────────────────────┘
```

### 1.2 Optimism 合约开发

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Optimism 上的合约与以太坊 L1 合约几乎完全兼容
// 主要差异：L2 特有的 predeploys 和 cross-domain 消息

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract OptimismToken is ERC20, Ownable {
    constructor(uint256 _initialSupply) ERC20("OptToken", "OPT") Ownable(msg.sender) {
        _mint(msg.sender, _initialSupply);
    }

    function mint(address _to, uint256 _amount) external onlyOwner {
        _mint(_to, _amount);
    }
}
```

### 1.3 L1 ↔ L2 跨域消息（Optimism）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// === L1 合约（部署在以太坊主网）===

interface ICrossDomainMessenger {
    function sendMessage(
        address _target,
        bytes calldata _message,
        uint32 _minGasLimit
    ) external payable;
}

contract L1Bridge {
    ICrossDomainMessenger public constant ovmL1CrossDomainMessenger =
        ICrossDomainMessenger(0x25ace71c97B33Cc4729CF772ae268934F7ab5fA1); // Optimism L1 Gateway

    address public l2TokenAddress;

    event DepositInitiated(address indexed from, address indexed to, uint256 amount);

    function setL2Token(address _l2Token) external {
        l2TokenAddress = _l2Token;
    }

    // 从 L1 存款到 L2
    function depositTo(address _to, uint256 _amount) external {
        // 锁定代币在 L1
        // token.transferFrom(msg.sender, address(this), _amount);

        // 发送跨域消息到 L2
        bytes memory message = abi.encodeWithSignature(
            "mint(address,uint256)",
            _to,
            _amount
        );

        ovmL1CrossDomainMessenger.sendMessage(
            l2TokenAddress,
            message,
            200000 // gas limit for L2 execution
        );

        emit DepositInitiated(msg.sender, _to, _amount);
    }

    // 从 L2 提款到 L1（由 L2 通过 CrossDomainMessenger 调用）
    function withdrawFrom(
        address _from,
        address _to,
        uint256 _amount
    ) external {
        // 验证消息来自 L2（通过 CrossDomainMessenger）
        require(
            msg.sender == address(ovmL1CrossDomainMessenger),
            "Only CrossDomainMessenger"
        );

        // 解锁代币
        // token.transfer(_to, _amount);

        emit WithdrawalFinalized(_from, _to, _amount);
    }

    event WithdrawalFinalized(address indexed from, address indexed to, uint256 amount);
}
```

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// === L2 合约（部署在 Optimism）===

interface IL2CrossDomainMessenger {
    function sendMessage(
        address _target,
        bytes calldata _message,
        uint32 _minGasLimit
    ) external payable;
}

contract L2Token {
    IL2CrossDomainMessenger public constant l2CrossDomainMessenger =
        IL2CrossDomainMessenger(0x4200000000000000000000000000000000000007); // Optimism L2 Messenger

    address public l1TokenAddress;
    address public l1BridgeAddress;

    // 被 L1 Bridge 通过 CrossDomainMessenger 调用
    function mint(address _to, uint256 _amount) external {
        require(
            msg.sender == address(l2CrossDomainMessenger),
            "Only from L1"
        );

        // 验证来源是 L1 Bridge
        require(
            l2CrossDomainMessenger == l1BridgeAddress,
            "Only from L1 bridge"
        );

        // 铸造代币
        _mintInternal(_to, _amount);
    }

    // 从 L2 提款到 L1
    function withdrawTo(address _to, uint256 _amount) external {
        // 销毁 L2 代币
        _burnInternal(msg.sender, _amount);

        // 发送消息到 L1 Bridge
        bytes memory message = abi.encodeWithSignature(
            "withdrawFrom(address,address,uint256)",
            msg.sender,
            _to,
            _amount
        );

        l2CrossDomainMessenger.sendMessage(
            l1BridgeAddress,
            message,
            200000
        );
    }

    function _mintInternal(address, uint256) internal { /* ... */ }
    function _burnInternal(address, uint256) internal { /* ... */ }
}
```

### 1.4 使用 ethers.js 与 Optimism 交互

```javascript
const { ethers } = require("ethers");

// Optimism 网络
const optimismProvider = new ethers.JsonRpcProvider("https://mainnet.optimism.io");
const optimismWsProvider = new ethers.WebSocketProvider("wss://ws-mainnet.optimism.io");

// L1 Provider
const l1Provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_KEY");

// L1 ↔ L2 桥接
const l1StandardBridgeAbi = [
    "function depositETH(uint32 l2Gas, bytes calldata data) external payable",
    "function depositERC20(address l1Token, address l2Token, uint256 amount, uint32 l2Gas, bytes calldata data) external",
    "event ERC20DepositInitiated(address indexed l1Token, address indexed l2Token, address indexed from, address to, uint256 amount, bytes data)",
];

const L1_STANDARD_BRIDGE = "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1";

async function bridgeETH() {
    const l1Wallet = new ethers.Wallet(process.env.PRIVATE_KEY, l1Provider);
    const bridge = new ethers.Contract(L1_STANDARD_BRIDGE, l1StandardBridgeAbi, l1Wallet);

    // 从 L1 存入 ETH 到 L2
    const amount = ethers.parseEther("1");
    const tx = await bridge.depositETH(200000, "0x", { value: amount });
    console.log("L1 Deposit TX:", tx.hash);

    const receipt = await tx.wait();
    console.log("Deposit confirmed on L1, block:", receipt.blockNumber);

    // 等待 L2 上确认（通常几分钟）
    // 可以使用 Optimism SDK 监听 L2 上的 deposit 状态
    const l2TxHash = await waitForL2Deposit(receipt);
    console.log("L2 Mint TX:", l2TxHash);
}

// 使用 @eth-optimism/sdk
const { CrossChainMessenger } = require("@eth-optimism/sdk");

async function bridgeWithSDK() {
    const l1Wallet = new ethers.Wallet(process.env.PRIVATE_KEY, l1Provider);
    const l2Wallet = new ethers.Wallet(process.env.PRIVATE_KEY, optimismProvider);

    const messenger = new CrossChainMessenger({
        l1SignerOrProvider: l1Wallet,
        l2SignerOrProvider: l2Wallet,
        l1ChainId: 1,
        l2ChainId: 10, // Optimism
    });

    // 存入 ETH
    const depositTx = await messenger.depositETH(ethers.parseEther("1"));
    await depositTx.wait();
    console.log("Deposit TX:", depositTx.hash);

    // 等待 L2 确认
    await messenger.waitForMessageStatus(depositTx.hash, OptimismSDK.MessageStatus.RELAYED);
    console.log("Deposit relayed to L2");

    // 提取 ETH
    const withdrawTx = await messenger.withdrawETH(ethers.parseEther("0.5"));
    await withdrawTx.wait();
    console.log("Withdrawal initiated:", withdrawTx.hash);

    // 等待 7 天挑战期
    const status = await messenger.getMessageStatus(withdrawTx.hash);
    if (status === OptimismSDK.MessageStatus.READY_TO_PROVE) {
        await messenger.proveMessage(withdrawTx.hash);
        console.log("Proved on L1");
    }

    // 等待最终确认后领取
    // await messenger.finalizeMessage(withdrawTx.hash);
}
```

---

## 二、ZK Rollup

### 2.1 工作原理

ZK Rollup 使用零知识证明 来验证交易有效性。每个批次提交时附带一个有效性证明，L1 合约只需验证证明即可确认所有交易合法。

```
┌──────────────────────────────────────────────────────┐
│              Layer 1 (Ethereum)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  ZK Verifier Contract                         │   │
│  │  ├── 验证 ZK Proof (groth16 / PLONK / STARK) │   │
│  │  └── 更新 State Root                          │   │
│  └──────────────────────────────────────────────┘   │
└───────────────────────┬──────────────────────────────┘
                        │ 提交 Batch + ZK Proof
┌───────────────────────▼──────────────────────────────┐
│              Layer 2 (ZK Chain)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Sequencer│  │ Prover   │  │ State    │           │
│  │ (排序+执行)│  │ (生成证明)│  │ Manager  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│  Validity Proof: π = Prove(state_transition_valid)  │
└──────────────────────────────────────────────────────┘

对比:
┌─────────────────┬─────────────────────┬─────────────────────┐
│                 │  Optimistic Rollup  │  ZK Rollup          │
├─────────────────┼─────────────────────┼─────────────────────┤
│ 假设            │  交易有效（乐观）   │  需证明有效           │
│ 挑战期          │  ~7 天              │  ~几分钟（即时确认）  │
│ 提款时间        │  ~7 天              │  ~1 小时             │
│ 计算开销        │  低（仅争议时验证） │  高（每次都生成证明） │
│ EVM 兼容性      │  完全兼容           │  部分兼容/发展中      │
│ 代表项目        │  OP, Arbitrum       │  zkSync, StarkNet    │
└─────────────────┴─────────────────────┴─────────────────────┘
```

### 2.2 zkSync 开发

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// zkSync Era 兼容大部分 EVM 操作码
// 主要差异:
// 1. 不支持 prevrandao（使用 block.timestamp 替代随机性场景）
// 2. paymaster 支持（用户可用 ERC-20 支付 Gas）
// 3. 账户抽象原生支持

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ZkSyncToken is ERC20 {
    constructor() ERC20("ZkToken", "ZKT") {
        _mint(msg.sender, 1_000_000 * 10**18);
    }
}
```

```javascript
// 使用 zksync-web3 SDK 与 zkSync 交互
const { Wallet, Provider, utils } = require("zksync-web3");
const { ethers } = require("ethers");

async function zkSyncExample() {
    // 连接到 zkSync Era
    const zkSyncProvider = new Provider("https://mainnet.era.zksync.io");
    const ethereumProvider = ethers.getDefaultProvider("mainnet");

    // 创建 zkSync Wallet
    const wallet = new Wallet(process.env.PRIVATE_KEY, zkSyncProvider, ethereumProvider);

    // 查询余额
    const ethBalance = await wallet.getBalance();
    console.log("ETH balance:", ethers.formatEther(ethBalance));

    // L1 → L2 存款
    const deposit = await wallet.deposit({
        token: utils.ETH_ADDRESS,
        amount: ethers.parseEther("0.1"),
    });
    console.log("Deposit TX:", deposit.hash);
    await deposit.wait();
    console.log("Deposit confirmed on L2");

    // L2 上转账
    const transfer = await wallet.transfer({
        to: "0xRecipient...",
        amount: ethers.parseEther("0.05"),
    });
    console.log("Transfer TX:", transfer.hash);

    // L2 → L1 提款
    const withdraw = await wallet.withdraw({
        token: utils.ETH_ADDRESS,
        amount: ethers.parseEther("0.05"),
    });
    await withdraw.wait();
    console.log("Withdrawal initiated");

    // 提款在 L1 上确认（通常需要几小时）
    const finalize = await withdraw.waitFinalize();
    console.log("Withdrawal ready to finalize");

    // 最终在 L1 领取
    await wallet.finalizeWithdraw(withdraw.hash);
    console.log("Withdrawal completed on L1");
}
```

### 2.3 账户抽象（EIP-4337）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// EIP-4337: 账户抽象允许智能合约钱包作为普通账户使用
// 核心组件: EntryPoint, Smart Account, Paymaster, Bundler

interface IUserOperation {
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external returns (uint256 validationData);
}

struct UserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    uint256 callGasLimit;
    uint256 verificationGasLimit;
    uint256 preVerificationGas;
    uint256 maxFeePerGas;
    uint256 maxPriorityFeePerGas;
    bytes paymasterAndData;
    bytes signature;
}

// 简化的智能合约钱包
contract SimpleAccount is IUserOperation {
    address public owner;
    uint256 public nonce;

    constructor(address _owner) {
        owner = _owner;
    }

    function execute(address dest, uint256 value, bytes calldata func) external {
        require(msg.sender == owner, "Not owner");
        (bool success, bytes memory result) = dest.call{value: value}(func);
        if (!success) {
            revert(string(result));
        }
    }

    function executeBatch(
        address[] calldata dest,
        uint256[] calldata values,
        bytes[] calldata funcs
    ) external {
        require(msg.sender == owner, "Not owner");
        require(dest.length == values.length && dest.length == funcs.length, "Length mismatch");

        for (uint256 i = 0; i < dest.length; i++) {
            (bool success, ) = dest[i].call{value: values[i]}(funcs[i]);
            require(success, "Batch execution failed");
        }
    }

    // EIP-4337 验证函数
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        // 验证签名
        require(
            owner == ECDSA.recover(userOpHash, userOp.signature),
            "Invalid signature"
        );

        // 验证 nonce
        require(userOp.nonce == nonce++, "Invalid nonce");

        // 支付 Gas（如果需要）
        if (missingAccountFunds > 0) {
            (bool success, ) = msg.sender.call{value: missingAccountFunds}("");
            require(success, "Payment failed");
        }

        return 0; // validationData = 0 表示验证通过
    }

    receive() external payable {}
}

library ECDSA {
    function recover(bytes32 hash, bytes memory signature) internal pure returns (address) {
        if (signature.length != 65) return address(0);
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(signature, 0x20))
            s := mload(add(signature, 0x40))
            v := byte(0, mload(add(signature, 0x60)))
        }
        return ecrecover(hash, v, r, s);
    }
}
```

---

## 三、Plasma

### 3.1 Plasma 工作原理

Plasma 是一系列链下区块链，定期将 Merkle Root 提交到 L1。使用欺诈证明来确保安全。

```
┌──────────────────────────────────────────────────────┐
│              L1 Root Chain Contract                  │
│  ├── Plasma Block Headers (Merkle Root)              │
│  ├── Deposit / Withdrawal Management                 │
│  └── Challenge Mechanism                             │
└───────────────────────┬──────────────────────────────┘
                        │ 提交区块 Merkle Root
┌───────────────────────▼──────────────────────────────┐
│              Plasma Child Chain                      │
│  ├── Block Producer (中心化/去中心化)                 │
│  ├── UTXO Model 或 Account Model                     │
│  └── Exit Game (退出机制)                            │
│  Block 1: [tx1, tx2, tx3] → Merkle Root → L1         │
│  Block 2: [tx4, tx5, tx6] → Merkle Root → L1         │
│  Block 3: [tx7, tx8, tx9] → Merkle Root → L1         │
└──────────────────────────────────────────────────────┘
```

### 3.2 简化版 Plasma 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SimplePlasma is ReentrancyGuard {
    struct PlasmaBlock {
        bytes32 merkleRoot;
        uint256 timestamp;
        address submitter;
    }

    mapping(uint256 => PlasmaBlock) public blocks;
    uint256 public currentBlock;

    // 存款
    mapping(address => uint256) public deposits;

    // 退出
    struct Exit {
        address exitor;
        uint256 amount;
        uint256 priority;
        uint256 createdAt;
    }

    mapping(bytes32 => Exit) public exits;
    uint256 public constant CHALLENGE_PERIOD = 7 days;

    address public operator;

    event BlockSubmitted(uint256 indexed blockNumber, bytes32 merkleRoot);
    event Deposited(address indexed depositor, uint256 amount);
    event ExitStarted(bytes32 indexed exitId, address indexed exitor, uint256 amount);

    constructor() {
        operator = msg.sender;
    }

    // 存款（从 L1 进入 Plasma）
    function deposit() external payable {
        require(msg.value > 0, "Must deposit ETH");
        deposits[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    // 提交 Plasma 区块
    function submitBlock(bytes32 _merkleRoot) external {
        require(msg.sender == operator, "Only operator");
        currentBlock++;
        blocks[currentBlock] = PlasmaBlock({
            merkleRoot: _merkleRoot,
            timestamp: block.timestamp,
            submitter: msg.sender
        });
        emit BlockSubmitted(currentBlock, _merkleRoot);
    }

    // 开始退出（Merkle 证明 + 挑战期）
    function startExit(
        uint256 _blockNumber,
        uint256 _txIndex,
        bytes calldata _txData,
        bytes calldata _proof,
        bytes calldata _confirmSig
    ) external {
        PlasmaBlock memory plasmaBlock = blocks[_blockNumber];
        require(plasmaBlock.merkleRoot != bytes32(0), "Block not found");

        // 验证 Merkle Proof
        bytes32 leaf = keccak256(_txData);
        require(
            _verifyMerkleProof(leaf, _proof, _txIndex, plasmaBlock.merkleRoot),
            "Invalid Merkle proof"
        );

        // 解析交易（简化）
        (address from, address to, uint256 amount) = abi.decode(_txData, (address, address, uint256));
        require(msg.sender == to, "Not the owner");

        bytes32 exitId = keccak256(abi.encodePacked(_blockNumber, _txIndex, msg.sender));

        exits[exitId] = Exit({
            exitor: msg.sender,
            amount: amount,
            priority: block.timestamp, // MoreVIG 风格优先级
            createdAt: block.timestamp
        });

        emit ExitStarted(exitId, msg.sender, amount);
    }

    // 挑战退出
    function challengeExit(
        bytes32 _exitId,
        uint256 _challengeBlockNumber,
        uint256 _challengeTxIndex,
        bytes calldata _challengeTxData,
        bytes calldata _proof
    ) external {
        Exit storage exit = exits[_exitId];
        require(exit.exitor != address(0), "Exit not found");

        // 证明资金已被花出（包含一个后续交易引用了该 UTXO）
        PlasmaBlock memory plasmaBlock = blocks[_challengeBlockNumber];
        require(plasmaBlock.merkleRoot != bytes32(0), "Challenge block not found");

        bytes32 leaf = keccak256(_challengeTxData);
        require(
            _verifyMerkleProof(leaf, _proof, _challengeTxIndex, plasmaBlock.merkleRoot),
            "Invalid challenge proof"
        );

        // 验证挑战交易的花费
        (address from, , ) = abi.decode(_challengeTxData, (address, address, uint256));
        require(from == exit.exitor, "Challenge not related to exit");

        // 取消退出
        delete exits[_exitId];
    }

    // 完成退出（挑战期过后）
    function finalizeExit(bytes32 _exitId) external nonReentrant {
        Exit storage exit = exits[_exitId];
        require(exit.exitor != address(0), "Exit not found");
        require(
            block.timestamp >= exit.createdAt + CHALLENGE_PERIOD,
            "Challenge period not over"
        );

        uint256 amount = exit.amount;
        delete exits[_exitId];

        (bool success, ) = payable(exit.exitor).call{value: amount}("");
        require(success, "Transfer failed");
    }

    function _verifyMerkleProof(
        bytes32 _leaf,
        bytes calldata _proof,
        uint256 _index,
        bytes32 _root
    ) internal pure returns (bool) {
        bytes32 computedHash = _leaf;
        bytes32 proofElement;

        for (uint256 i = 0; i < 32; i++) {
            if (i * 32 >= _proof.length) break;
            proofElement = bytes32(_proof[i * 32:(i + 1) * 32]);

            if (_index % 2 == 0) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
            _index = _index / 2;
        }

        return computedHash == _root;
    }
}
```

> **注**: Plasma MVP 使用 UTXO 模型，Plasma Cash 使用 NFT 模型。目前 Plasma 在很大程度上已被 Rollup 取代。

---

## 四、侧链

### 4.1 侧链 vs Rollup 对比

| 特性 | 侧链 | Rollup |
|------|------|--------|
| **共识** | 独立共识 | 依赖 L1 共识 |
| **安全性** | 自身验证者集 | 继承 L1 安全性 |
| **提款时间** | 即时 / 分钟级 | OP: 7 天 / ZK: 小时级 |
| **数据可用性** | 侧链自己维护 | L1 维护 |
| **EVM 兼容** | 完全兼容 | 完全/部分兼容 |
| **代表** | Polygon PoS | Optimism, Arbitrum, zkSync |

### 4.2 Polygon PoS 集成

```javascript
const { ethers } = require("ethers");

// Polygon PoS 网络
const polygonProvider = new ethers.JsonRpcProvider("https://polygon-rpc.com");
const l1Provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_KEY");

// Polygon Bridge 地址
const POS_ROOT_CHAIN_MANAGER = "0xA0c68C638235ee32657e8f720a23ceC1bFc77C77";
const POS_ETH_PREDICATE = "0x8484Ef722627bf18ca5Ae6BcF031c23E6e922B30";

// 从 L1 桥接到 Polygon
async function bridgeETHtoPolygon() {
    const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, l1Provider);

    // 通过 RootChainManager 存款
    const rootChainManager = new ethers.Contract(
        POS_ROOT_CHAIN_MANAGER,
        [
            "function depositFor(address user, address rootToken, bytes calldata depositData) external payable",
        ],
        wallet
    );

    const amount = ethers.parseEther("1");
    const depositData = ethers.AbiCoder.defaultAbiCoder().encode(
        ["uint256"],
        [amount]
    );

    const tx = await rootChainManager.depositFor(
        wallet.address,
        POS_ETH_PREDICATE, // ETH Predicate 地址
        depositData,
        { value: amount }
    );

    console.log("L1 Bridge TX:", tx.hash);
    const receipt = await tx.wait();
    console.log("Confirmed on L1, block:", receipt.blockNumber);

    // 等待 Polygon 上的 state sync（通常 7-8 分钟）
    // 监听 Polygon 上的 StateSender 事件
}
```

---

## 五、状态通道

### 5.1 工作原理

状态通道允许参与者在链下进行任意多次状态更新，只在开启和关闭时与链交互。

```
┌──────────────────────────────────────────────────────┐
│              链上 (On-Chain)                          │
│                                                      │
│  1. 开启通道: 双方锁定保证金到 multisig 合约         │
│     ┌─────────────────────────────┐                 │
│     │  Channel Contract            │                 │
│     │  partyA: 5 ETH locked       │                 │
│     │  partyB: 5 ETH locked       │                 │
│     └─────────────────────────────┘                 │
│                                                      │
│  3. 关闭通道: 提交最终状态，按余额分配              │
│     ┌─────────────────────────────┐                 │
│     │  Channel Contract            │                 │
│     │  partyA: 3 ETH (lost 2)     │                 │
│     │  partyB: 7 ETH (gained 2)   │                 │
│     └─────────────────────────────┘                 │
└──────────────────────────────────────────────────────┘
         │ 开启                              │ 关闭
┌────────▼──────────────────────────────┬────┘─────────┐
│         链下 (Off-Channel)              │             │
│                                        │             │
│  State 0: A=5, B=5   ← 初始状态       │             │
│     ↓                                  │             │
│  State 1: A=4, B=6   ← A 支付 1 ETH   │             │
│     ↓                                  │             │
│  State 2: A=3, B=7   ← A 支付 1 ETH   │             │
│     ↓                                  │             │
│  State N: A=x, B=y   ← 任意多次交易   │             │
│                                        │             │
└────────────────────────────────────────┘             │
```

### 5.2 支付通道合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract PaymentChannel is ReentrancyGuard {
    using ECDSA for bytes32;

    struct Channel {
        address participantA;
        address participantB;
        uint256 depositA;
        uint256 depositB;
        uint256 challengePeriod; // 秒
        uint256 closeAt;         // 0 = 开启中
        bool closed;
    }

    mapping(bytes32 => Channel) public channels;

    uint256 public constant MIN_CHALLENGE_PERIOD = 1 days;
    uint256 public constant MAX_CHALLENGE_PERIOD = 30 days;

    event ChannelOpened(
        bytes32 indexed channelId,
        address indexed participantA,
        address indexed participantB,
        uint256 depositA,
        uint256 depositB
    );
    event ChannelChallenged(bytes32 indexed channelId, uint256 closeAt);
    event ChannelClosed(
        bytes32 indexed channelId,
        uint256 amountA,
        uint256 amountB
    );

    // 开启通道
    function openChannel(
        address _participantB,
        uint256 _challengePeriod
    ) external payable returns (bytes32 channelId) {
        require(
            _challengePeriod >= MIN_CHALLENGE_PERIOD &&
            _challengePeriod <= MAX_CHALLENGE_PERIOD,
            "Invalid challenge period"
        );

        channelId = keccak256(abi.encodePacked(
            msg.sender,
            _participantB,
            block.timestamp,
            block.number
        ));

        require(channels[channelId].participantA == address(0), "Channel exists");

        channels[channelId] = Channel({
            participantA: msg.sender,
            participantB: _participantB,
            depositA: msg.value,
            depositB: 0,
            challengePeriod: _challengePeriod,
            closeAt: 0,
            closed: false
        });

        emit ChannelOpened(channelId, msg.sender, _participantB, msg.value, 0);
    }

    // B 加入通道（存入保证金）
    function joinChannel(bytes32 _channelId) external payable {
        Channel storage channel = channels[_channelId];
        require(channel.participantA != address(0), "Channel not found");
        require(msg.sender == channel.participantB, "Not participant B");
        require(channel.depositB == 0, "Already joined");
        require(channel.closeAt == 0, "Channel closing");

        channel.depositB = msg.value;
    }

    // 合作关闭（双方签名最终状态）
    function cooperativeClose(
        bytes32 _channelId,
        uint256 _amountA,
        uint256 _amountB,
        bytes calldata _signatureA,
        bytes calldata _signatureB
    ) external nonReentrant {
        Channel storage channel = channels[_channelId];
        require(channel.participantA != address(0), "Channel not found");
        require(!channel.closed, "Already closed");
        require(channel.closeAt == 0 || block.timestamp >= channel.closeAt, "Challenge active");

        uint256 total = _amountA + _amountB;
        require(total == channel.depositA + channel.depositB, "Amount mismatch");

        // 验证双方签名
        bytes32 message = keccak256(abi.encodePacked(
            _channelId,
            _amountA,
            _amountB,
            address(this),
            block.chainid
        )).toEthSignedMessageHash();

        require(
            message.recover(_signatureA) == channel.participantA,
            "Invalid signature A"
        );
        require(
            message.recover(_signatureB) == channel.participantB,
            "Invalid signature B"
        );

        channel.closed = true;

        _payout(channel, _amountA, _amountB);

        emit ChannelClosed(_channelId, _amountA, _amountB);
    }

    // 单方关闭（发起挑战期）
    function challengeClose(bytes32 _channelId) external {
        Channel storage channel = channels[_channelId];
        require(channel.participantA != address(0), "Channel not found");
        require(!channel.closed, "Already closed");
        require(
            msg.sender == channel.participantA || msg.sender == channel.participantB,
            "Not a participant"
        );

        channel.closeAt = block.timestamp + channel.challengePeriod;
        emit ChannelChallenged(_channelId, channel.closeAt);
    }

    // 挑战期满后关闭
    function finalizeWithState(
        bytes32 _channelId,
        uint256 _amountA,
        uint256 _amountB,
        bytes calldata _counterSignature
    ) external nonReentrant {
        Channel storage channel = channels[_channelId];
        require(channel.participantA != address(0), "Channel not found");
        require(!channel.closed, "Already closed");
        require(channel.closeAt > 0, "Not challenged");
        require(block.timestamp >= channel.closeAt, "Challenge period not over");

        uint256 total = _amountA + _amountB;
        require(total == channel.depositA + channel.depositB, "Amount mismatch");

        // 验证对方签名（最新状态）
        bytes32 message = keccak256(abi.encodePacked(
            _channelId,
            _amountA,
            _amountB,
            address(this),
            block.chainid
        )).toEthSignedMessageHash();

        address signer = message.recover(_counterSignature);
        require(
            signer == channel.participantA || signer == channel.participantB,
            "Invalid counter-signature"
        );

        channel.closed = true;
        _payout(channel, _amountA, _amountB);
        emit ChannelClosed(_channelId, _amountA, _amountB);
    }

    function _payout(
        Channel storage channel,
        uint256 _amountA,
        uint256 _amountB
    ) internal {
        if (_amountA > 0) {
            (bool okA, ) = payable(channel.participantA).call{value: _amountA}("");
            require(okA, "Pay A failed");
        }
        if (_amountB > 0) {
            (bool okB, ) = payable(channel.participantB).call{value: _amountB}("");
            require(okB, "Pay B failed");
        }
    }
}
```

### 5.3 链下签名

```javascript
// 链下创建和签名支付状态
const { ethers } = require("ethers");

class PaymentChannelClient {
    constructor(channelId, wallet, contractAddress, chainId) {
        this.channelId = channelId;
        this.wallet = wallet;
        this.contractAddress = contractAddress;
        this.chainId = chainId;
        this.nonce = 0;
    }

    // 创建状态消息哈希
    createStateHash(amountA, amountB) {
        return ethers.solidityPackedKeccak256(
            ["bytes32", "uint256", "uint256", "address", "uint256"],
            [this.channelId, amountA, amountB, this.contractAddress, this.chainId]
        );
    }

    // 签名状态（转换为 EIP-191）
    async signState(amountA, amountB) {
        const hash = this.createStateHash(amountA, amountB);
        const signedHash = ethers.hashMessage(ethers.getBytes(hash));
        const signature = await this.wallet.signMessage(ethers.getBytes(hash));
        return { hash: signedHash, signature };
    }

    // 验证对方签名
    verifySignature(amountA, amountB, signature, expectedSigner) {
        const hash = this.createStateHash(amountA, amountB);
        const recovered = ethers.verifyMessage(ethers.getBytes(hash), signature);
        return recovered === expectedSigner;
    }

    // 链下更新状态（不需要链上交易）
    async createPayment(fromWallet, toWallet, amount) {
        // 更新余额
        // 签名新状态
        // 交换签名
        // 双方都保存最新已签名的状态
    }
}
```

---

## 六、L2 开发最佳实践

### 6.1 选择合适的 L2

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| **DeFi 协议** | Arbitrum / Optimism | EVM 完全兼容，流动性好 |
| **高吞吐应用** | zkSync Era | 更高 TPS，更低 Gas |
| **NFT 项目** | Polygon PoS | 低 Gas，用户量大 |
| **游戏** | Polygon / Immutable X | 极低 Gas，支持游戏特性 |
| **需要快速提款** | zkSync / Validium | ZK 提款时间短 |
| **最大去中心化** | Optimism | 开源工具链，去中心化路线图 |

### 6.2 L2 合约迁移清单

```solidity
// === 需要注意的差异 ===

pragma solidity ^0.8.20;

contract L2Compatibility {
    // ❌ 不可用: block.difficulty (Optimism, Arbitrum)
    // ✅ 替代: block.prevrandao (但某些 L2 也不支持)
    // 在 L2 上不应依赖 prevrandao 作为随机源

    // ❌ 不可用: 链上 Chainlink VRF（部分 L2）
    // ✅ 替代: 使用 L1 VRF 通过跨域消息传递

    // ⚠️ 注意: gasleft() 在 L2 上的行为可能不同
    // L2 的 gas 计算模型与 L1 不同

    // ⚠️ 注意: tx.gasprice 在 L2 上与用户支付的不同
    // L2 交易费用 = L2 执行费 + L1 数据可用性费

    // ✅ 兼容: 基本的 Solidity 语法和 OpenZeppelin 库
    // ✅ 兼容: 标准 ERC-20 / ERC-721 / ERC-1155
    // ✅ 兼容: 基本的 mapping / array / struct

    // ⚠️ 注意: selfdestruct 在某些 L2 上行为不同

    // ✅ 最佳实践: 使用 try/catch 处理跨域调用失败
    function safeCrossDomainCall() external {
        // 总是处理跨域消息失败的情况
    }
}
```

### 6.3 Gas 估算（L2 特殊处理）

```javascript
// L2 Gas 估算需要考虑 L1 数据费用
async function estimateL2Gas() {
    const provider = new ethers.JsonRpcProvider("https://mainnet.optimism.io");

    // 获取 L2 Gas 价格
    const l2GasPrice = await provider.getFeeData();
    console.log("L2 Gas price:", ethers.formatUnits(l2GasPrice.gasPrice, "gwei"), "gwei");

    // L1 数据费用估算（Optimism 特有）
    // 每笔 L2 交易需要将数据发布到 L1，产生额外费用
    const l1BaseFee = await provider.call({
        to: "0x420000000000000000000000000000000000000F", // GasPriceOracle
        data: "0x5b9cf315", // function l1BaseFee()
    });
    console.log("L1 Base fee:", ethers.formatUnits(BigInt(l1BaseFee), "gwei"), "gwei");

    // 计算总费用
    // 总费用 = L2 执行费 + L1 Calldata 费
    // L1 Calldata 费 ≈ (calldata bytes * 16) * L1 gas price

    // 使用 Optimism SDK 精确估算
    // const estimatedFee = await optimismProvider.estimateGas(tx);
}
```

---

## 七、L2 生态系统

### 7.1 主流 L2 对比

| L2 | 类型 | EVM 兼容 | TVL | 特色 |
|------|------|----------|-----|------|
| **Arbitrum One** | Optimistic | ✅ 完全 | 最高 | Nitro 技术栈，最活跃的生态 |
| **Optimism** | Optimistic | ✅ 完全 | 高 | OP Stack 开源，Superchain 愿景 |
| **Base** | Optimistic (OP Stack) | ✅ 完全 | 高 | Coinbase 支持 |
| **zkSync Era** | ZK | ✅ 大部分 | 高 | 原生账户抽象 |
| **Polygon zkEVM** | ZK | ✅ 大部分 | 中 | EVM 等效 |
| **StarkNet** | ZK | ❌ Cairo | 中 | Cairo VM，超高吞吐 |
| **Scroll** | ZK | ✅ 完全 | 中 | 完全 EVM 等效 ZK |
| **Linea** | ZK | ✅ 完全 | 中 | ConsenSys 开发 |

### 7.2 OP Stack 自定义链

```javascript
// 使用 OP Stack 部署自定义 L2 (Rollup-as-a-Service)
// 参考: https://stack.optimism.io/

// 关键配置参数
const opStackConfig = {
    // L1 配置
    l1ChainId: 1, // Ethereum Mainnet
    l1RpcUrl: "https://mainnet.infura.io/v3/YOUR_KEY",

    // L2 配置
    l2ChainId: 999999, // 自定义 Chain ID
    l2RpcUrl: "http://localhost:9545",

    // 批次提交者
    batchSenderAddress: "0x...",
    batchInboxAddress: "0x...",

    // 序列器
    sequencerAddress: "0x...",

    // 挑战期
    finalizationPeriodSeconds: 604800, // 7 天

    // Gas 配置
    l2GasPriceFloor: 1000000, // 0.001 gwei
    eip1559Denominator: 50,
    eip1559Elasticity: 10,
};
```

---

## 相关页面

- [[智能合约开发]] - Solidity 合约开发基础
- [[DeFi协议指南]] - L2 上的 DeFi 应用
- [[NFT开发指南]] - L2 NFT 生态
- [[Web3后端开发]] - L2 后端适配与多链支持
