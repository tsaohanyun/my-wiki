---
title: DeFi协议指南
aliases:
  - DeFi Guide
  - 去中心化金融
  - DeFi Protocol
tags:
  - blockchain
  - defi
  - amm
  - lending
  - oracle
  - cross-chain
  - web3
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: 原创
difficulty: advanced
project: AI-Agent
---

# DeFi 协议指南

## 概述

DeFi（Decentralized Finance，去中心化金融）通过智能合约在区块链上重建传统金融服务，无需银行或券商等中介。本指南涵盖 AMM（自动做市商）、借贷协议、质押挖矿、预言机集成和跨链桥接。

---

## 一、AMM（自动做市商）

### 1.1 恒定乘积公式（x * y = k）

Uniswap V2 的核心公式 `x * y = k` 维持两个代币储备的乘积恒定。

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract SimpleAMM {
    using SafeERC20 for IERC20;

    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;

    uint256 public reserveA;
    uint256 public reserveB;

    uint256 public constant FEE_NUMERATOR = 997;   // 0.3% 手续费
    uint256 public constant FEE_DENOMINATOR = 1000;

    event Swap(address indexed sender, uint256 amountIn, uint256 amountOut, bool isAToB);
    event LiquidityAdded(address indexed provider, uint256 amountA, uint256 amountB);
    event LiquidityRemoved(address indexed provider, uint256 amountA, uint256 amountB);

    constructor(address _tokenA, address _tokenB) {
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    // 添加流动性
    function addLiquidity(uint256 _amountA, uint256 _amountB) external {
        tokenA.safeTransferFrom(msg.sender, address(this), _amountA);
        tokenB.safeTransferFrom(msg.sender, address(this), _amountB);

        if (reserveA == 0 && reserveB == 0) {
            // 首次添加流动性
            (reserveA, reserveB) = (_amountA, _amountB);
        } else {
            // 后续添加需要按比例
            uint256 amountAOptimal = (reserveA * _amountB) / reserveB;
            require(_amountA >= amountAOptimal, "Insufficient tokenA amount");

            reserveA += _amountA;
            reserveB += _amountB;
        }

        emit LiquidityAdded(msg.sender, _amountA, _amountB);
    }

    // 计算输出金额
    function getAmountOut(
        uint256 _amountIn,
        uint256 _reserveIn,
        uint256 _reserveOut
    ) public pure returns (uint256 amountOut) {
        require(_amountIn > 0, "Insufficient input amount");
        require(_reserveIn > 0 && _reserveOut > 0, "Insufficient liquidity");

        uint256 amountInWithFee = _amountIn * FEE_NUMERATOR;
        uint256 numerator = amountInWithFee * _reserveOut;
        uint256 denominator = (_reserveIn * FEE_DENOMINATOR) + amountInWithFee;
        amountOut = numerator / denominator;
    }

    // 交换 A -> B
    function swapAforB(uint256 _amountIn) external returns (uint256 amountOut) {
        amountOut = getAmountOut(_amountIn, reserveA, reserveB);

        tokenA.safeTransferFrom(msg.sender, address(this), _amountIn);
        tokenB.safeTransfer(msg.sender, amountOut);

        reserveA += _amountIn;
        reserveB -= amountOut;

        emit Swap(msg.sender, _amountIn, amountOut, true);
    }

    // 交换 B -> A
    function swapBforA(uint256 _amountIn) external returns (uint256 amountOut) {
        amountOut = getAmountOut(_amountIn, reserveB, reserveA);

        tokenB.safeTransferFrom(msg.sender, address(this), _amountIn);
        tokenA.safeTransfer(msg.sender, amountOut);

        reserveB += _amountIn;
        reserveA -= amountOut;

        emit Swap(msg.sender, _amountIn, amountOut, false);
    }

    // 获取当前价格
    function getPriceAinB() external view returns (uint256) {
        return (reserveB * 1e18) / reserveA;
    }
}
```

### 1.2 Uniswap V3 集中流动性概念

```solidity
// Uniswap V3 引入了集中流动性（Concentrated Liquidity）
// LP 可以选择价格区间提供流动性，提高资本效率

pragma solidity ^0.8.20;

library TickMath {
    int24 public constant MIN_TICK = -887272;
    int24 public constant MAX_TICK = 887272;

    // 简化版：计算 tick 对应的价格
    function tickToPrice(int24 tick) internal pure returns (uint256 price) {
        if (tick < 0) {
            uint256 absTick = uint256(-int256(tick));
            // price = 1.0001^(-tick)
            // 实际实现更复杂，使用二进制分解
            price = (1e18 * 1e18) / (1e18 + absTick * 1e14);
        } else {
            price = 1e18 + uint256(int256(tick)) * 1e14;
        }
    }

    // 价格转 tick
    function priceToTick(uint256 price) internal pure returns (int24 tick) {
        if (price >= 1e18) {
            tick = int24(int256((price - 1e18) / 1e14));
        } else {
            tick = -int24(int256((1e18 - price) / 1e14));
        }
        require(tick >= MIN_TICK && tick <= MAX_TICK, "Tick out of range");
    }
}
```

### 1.3 通过 SDK 交互

```javascript
// 使用 ethers.js 与 Uniswap V2 交互
const { ethers } = require("ethers");

const provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_KEY");

// Uniswap V2 Router ABI（简化）
const routerAbi = [
    "function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] path, address to, uint deadline) external returns (uint[] amounts)",
    "function getAmountsOut(uint amountIn, address[] path) public view returns (uint[] amounts)"
];

const routerAddress = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D";
const router = new ethers.Contract(routerAddress, routerAbi, provider);

async function swapTokens() {
    const amountIn = ethers.parseEther("1");
    const path = ["0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", // WETH
                  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"]; // USDC

    // 获取预期输出
    const amounts = await router.getAmountsOut(amountIn, path);
    console.log("Expected output:", amounts[1]);

    // 设置最小输出（滑点保护）
    const minOutput = amounts[1] * 95n / 100n; // 5% 滑点
    const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20 分钟

    // 执行交易（需要 signer）
    const tx = await router.swapExactTokensForTokens(
        amountIn,
        minOutput,
        path,
        wallet.address,
        deadline
    );
    console.log("TX:", tx.hash);
}
```

---

## 二、借贷协议

### 2.1 基本借贷合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract LendingProtocol is ReentrancyGuard {
    using SafeERC20 for IERC20;

    // 资产配置
    struct AssetConfig {
        bool isActive;
        uint256 collateralFactor;  // 抵押率，如 75% = 7500
        uint256 liquidationThreshold; // 清算阈值，如 80% = 8000
        uint256 liquidationBonus;  // 清算奖励，如 5% = 500
        uint256 baseBorrowRate;    // 基础借款利率 (年化)
        uint256 reserveFactor;     // 储备金比例
    }

    // 用户仓位
    struct Position {
        uint256 collateralAmount;
        uint256 borrowedAmount;
        uint256 lastAccruedBlock;
    }

    IERC20 public immutable collateralToken;
    IERC20 public immutable borrowToken;

    mapping(address => Position) public positions;
    AssetConfig public assetConfig;

    // 利率累加指数
    uint256 public borrowIndex = 1e18;
    uint256 public totalBorrows;
    uint256 public totalCollateral;
    uint256 public constant SECONDS_PER_YEAR = 365 days;

    event Deposited(address indexed user, uint256 amount);
    event Borrowed(address indexed user, uint256 amount);
    event Repaid(address indexed user, uint256 amount);
    event Liquidated(address indexed liquidator, address indexed borrower, uint256 debtAmount);

    constructor(address _collateralToken, address _borrowToken) {
        collateralToken = IERC20(_collateralToken);
        borrowToken = IERC20(_borrowToken);

        assetConfig = AssetConfig({
            isActive: true,
            collateralFactor: 7500,      // 75%
            liquidationThreshold: 8000,  // 80%
            liquidationBonus: 500,       // 5%
            baseBorrowRate: 5e16,        // 5% APR
            reserveFactor: 1000          // 10%
        });
    }

    // 存入抵押品
    function deposit(uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be > 0");
        require(assetConfig.isActive, "Asset not active");

        collateralToken.safeTransferFrom(msg.sender, address(this), _amount);

        Position storage pos = positions[msg.sender];
        pos.collateralAmount += _amount;
        totalCollateral += _amount;

        emit Deposited(msg.sender, _amount);
    }

    // 借款
    function borrow(uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be > 0");

        _accrueInterest();

        Position storage pos = positions[msg.sender];
        pos.borrowedAmount += _amount;

        // 检查抵押率
        require(_isHealthy(msg.sender), "Insufficient collateral");

        borrowToken.safeTransfer(msg.sender, _amount);
        totalBorrows += _amount;

        emit Borrowed(msg.sender, _amount);
    }

    // 还款
    function repay(uint256 _amount) external nonReentrant {
        Position storage pos = positions[msg.sender];
        require(pos.borrowedAmount > 0, "No debt");

        uint256 repayAmount = _amount > pos.borrowedAmount ? pos.borrowedAmount : _amount;

        borrowToken.safeTransferFrom(msg.sender, address(this), repayAmount);

        pos.borrowedAmount -= repayAmount;
        totalBorrows -= repayAmount;

        emit Repaid(msg.sender, repayAmount);
    }

    // 清算
    function liquidate(address _borrower) external nonReentrant {
        Position storage pos = positions[_borrower];
        require(!_isHealthy(_borrower), "Position is healthy");

        uint256 debtAmount = pos.borrowedAmount;
        // 清算者获得抵押品 + 奖励
        uint256 collateralSeized = (debtAmount * (10000 + assetConfig.liquidationBonus)) / 10000;

        require(pos.collateralAmount >= collateralSeized, "Insufficient collateral to seize");

        // 转移借款代币（清算者偿还债务）
        borrowToken.safeTransferFrom(msg.sender, address(this), debtAmount);

        // 转移抵押品给清算者
        collateralToken.safeTransfer(msg.sender, collateralSeized);

        pos.collateralAmount -= collateralSeized;
        pos.borrowedAmount = 0;
        totalBorrows -= debtAmount;
        totalCollateral -= collateralSeized;

        emit Liquidated(msg.sender, _borrower, debtAmount);
    }

    // 检查仓位是否健康
    function _isHealthy(address _user) internal view returns (bool) {
        Position storage pos = positions[_user];
        if (pos.borrowedAmount == 0) return true;

        uint256 maxBorrow = (pos.collateralAmount * assetConfig.collateralFactor) / 10000;
        return pos.borrowedAmount <= maxBorrow;
    }

    // 计算利息（简化版：线性利率）
    function _accrueInterest() internal {
        if (totalBorrows == 0) return;

        uint256 timeElapsed = block.timestamp - lastAccrueTime;
        if (timeElapsed == 0) return;

        // 利息 = 总借款 * 年化利率 * 经过时间 / 一年秒数
        uint256 interest = (totalBorrows * assetConfig.baseBorrowRate * timeElapsed) / (SECONDS_PER_YEAR * 1e18);

        borrowIndex += interest;
        lastAccrueTime = block.timestamp;
    }

    uint256 lastAccrueTime = block.timestamp;

    // 查询用户健康度
    function getHealthFactor(address _user) external view returns (uint256) {
        Position storage pos = positions[_user];
        if (pos.borrowedAmount == 0) return type(uint256).max;

        uint256 collateralValue = (pos.collateralAmount * assetConfig.liquidationThreshold) / 10000;
        return (collateralValue * 1e18) / pos.borrowedAmount;
    }
}
```

### 2.2 闪电贷

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IFlashLoanReceiver {
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

contract FlashLoanProvider {
    mapping(address => bool) public allowedTokens;
    uint256 public premiumRate = 9; // 0.09% 手续费

    event FlashLoanExecuted(address indexed receiver, address indexed asset, uint256 amount, uint256 premium);

    function flashLoan(
        address _asset,
        uint256 _amount,
        bytes calldata _params
    ) external {
        require(allowedTokens[_asset], "Token not supported");

        uint256 balanceBefore = IERC20(_asset).balanceOf(address(this));
        require(balanceBefore >= _amount, "Insufficient liquidity");

        uint256 premium = (_amount * premiumRate) / 10000;

        // 转移资金给接收者
        IERC20(_asset).transfer(msg.sender, _amount);

        // 调用接收者的回调
        bool success = IFlashLoanReceiver(msg.sender).executeOperation(
            _asset,
            _amount,
            premium,
            msg.sender,
            _params
        );
        require(success, "Callback failed");

        // 确认还款
        uint256 balanceAfter = IERC20(_asset).balanceOf(address(this));
        require(balanceAfter >= balanceBefore + premium, "Flash loan not repaid");

        emit FlashLoanExecuted(msg.sender, _asset, _amount, premium);
    }
}

interface IERC20 {
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}
```

### 2.3 Aave V3 闪电贷示例

```javascript
// 使用 Aave V3 闪电贷进行套利
const { ethers } = require("ethers");

// Aave V3 Pool 地址（Polygon）
const poolAddress = "0x794a61358D6845594F94dc1DB02A252b5b4814aD";

// 闪电贷接收合约
const flashLoanReceiverCode = `
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";

contract ArbitrageFlashLoan is FlashLoanSimpleReceiverBase {
    constructor(address provider)
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(provider))
    {}

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        // 1. 在 DEX A 上用借来的资金买入代币
        // 2. 在 DEX B 上卖出代币获得利润
        // 3. 偿还闪电贷（本金 + 手续费）

        uint256 amountToReturn = amount + premium;
        IERC20(asset).approve(address(POOL), amountToReturn);

        return true;
    }

    function requestFlashLoan(address _asset, uint256 _amount) external {
        address receiverAddress = address(this);
        bytes memory params = "";
        uint16 referralCode = 0;

        POOL.flashLoanSimple(
            receiverAddress,
            _asset,
            _amount,
            params,
            referralCode
        );
    }
}
`;
```

---

## 三、质押与流动性挖矿

### 3.1 质押合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract StakingRewards is ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable stakingToken;
    IERC20 public immutable rewardsToken;

    uint256 public rewardRate;          // 每秒奖励代币数量
    uint256 public rewardsDuration;     // 奖励周期
    uint256 public lastUpdateTime;      // 上次更新时间
    uint256 public rewardPerTokenStored; // 每代币累计奖励

    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;

    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;

    address public owner;

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);
    event RewardAdded(uint256 reward);

    constructor(address _stakingToken, address _rewardsToken) {
        stakingToken = IERC20(_stakingToken);
        rewardsToken = IERC20(_rewardsToken);
        owner = msg.sender;
    }

    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }
        _;
    }

    // === 视图函数 ===

    function totalSupply() external view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address _account) external view returns (uint256) {
        return _balances[_account];
    }

    function lastTimeRewardApplicable() public view returns (uint256) {
        return block.timestamp < periodFinish ? block.timestamp : periodFinish;
    }

    function rewardPerToken() public view returns (uint256) {
        if (_totalSupply == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (
            (lastTimeRewardApplicable() - lastUpdateTime) * rewardRate * 1e18
        ) / _totalSupply;
    }

    function earned(address _account) public view returns (uint256) {
        return (_balances[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account])) / 1e18
            + rewards[_account];
    }

    function getRewardForDuration() external view returns (uint256) {
        return rewardRate * rewardsDuration;
    }

    // === 核心功能 ===

    uint256 public periodFinish;

    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        require(_amount > 0, "Cannot stake 0");

        _totalSupply += _amount;
        _balances[msg.sender] += _amount;

        stakingToken.safeTransferFrom(msg.sender, address(this), _amount);
        emit Staked(msg.sender, _amount);
    }

    function withdraw(uint256 _amount) public nonReentrant updateReward(msg.sender) {
        require(_amount > 0, "Cannot withdraw 0");

        _totalSupply -= _amount;
        _balances[msg.sender] -= _amount;

        stakingToken.safeTransfer(msg.sender, _amount);
        emit Withdrawn(msg.sender, _amount);
    }

    function getReward() public nonReentrant updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }
    }

    function exit() external {
        withdraw(_balances[msg.sender]);
        getReward();
    }

    // === 管理 ===

    function notifyRewardAmount(uint256 _reward) external updateReward(address(0)) {
        require(msg.sender == owner, "Only owner");

        if (block.timestamp >= periodFinish) {
            rewardRate = _reward / rewardsDuration;
        } else {
            uint256 remaining = periodFinish - block.timestamp;
            uint256 leftover = remaining * rewardRate;
            rewardRate = (_reward + leftover) / rewardsDuration;
        }

        lastUpdateTime = block.timestamp;
        periodFinish = block.timestamp + rewardsDuration;
        emit RewardAdded(_reward);
    }

    function setRewardsDuration(uint256 _rewardsDuration) external {
        require(msg.sender == owner, "Only owner");
        require(block.timestamp > periodFinish, "Previous period not finished");
        rewardsDuration = _rewardsDuration;
    }
}
```

---

## 四、预言机（Oracle）

### 4.1 Chainlink Price Feed

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    // Chainlink Price Feed 地址（以太坊主网）
    // ETH/USD: 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
    // BTC/USD: 0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c
    // LINK/USD: 0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c

    mapping(string => AggregatorV3Interface) public priceFeeds;

    constructor() {
        // 初始化价格源
        priceFeeds["ETH/USD"] = AggregatorV3Interface(0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419);
        priceFeeds["BTC/USD"] = AggregatorV3Interface(0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c);
    }

    function getLatestPrice(string memory _pair) external view returns (int256, uint256) {
        AggregatorV3Interface feed = priceFeeds[_pair];
        require(address(feed) != address(0), "Feed not found");

        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = feed.latestRoundData();

        require(price > 0, "Invalid price");
        require(updatedAt > 0, "Round not complete");
        require(block.timestamp - updatedAt < 1 hours, "Stale price");

        uint8 decimals = feed.decimals();
        return (price, decimals);
    }

    // TWAP（时间加权平均价格）— 抵御闪贷攻击
    function getTwapPrice(string memory _pair, uint256 _lookback) external view returns (int256) {
        AggregatorV3Interface feed = priceFeeds[_pair];
        uint256 totalTime = 0;
        int256 totalPrice = 0;
        uint16 rounds = 0;

        // 简化版：取最近几轮的平均值
        (uint80 latestRound, , , , ) = feed.latestRoundData();

        for (uint80 i = 0; i < 3; i++) {
            if (latestRound <= i) break;
            (, int256 price, , uint256 updatedAt, ) = feed.getRoundData(latestRound - i);
            totalPrice += price;
            rounds++;
        }

        return totalPrice / int256(uint256(rounds));
    }
}
```

### 4.2 Chainlink VRF（可验证随机数）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/vrf/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";

contract RandomNumberGenerator is VRFConsumerBaseV2 {
    LinkTokenInterface public immutable linkToken;

    // VRF Coordinator 地址 & Key Hash
    address vrfCoordinator = 0x6168499c0cFfCaCD319c818142124B7A15E857fF; // Goerli
    bytes32 keyHash = 0x79d3d8832d904592c0bf9818b621522c988bb8b0c05cdc3b15dbe1f6852d0c0b;
    uint64 subscriptionId;

    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;

    mapping(uint256 => address) public requestToSender;
    mapping(address => uint256) public randomResults;

    event RandomnessRequested(address indexed requester, uint256 requestId);
    event RandomnessFulfilled(uint256 requestId, uint256 randomWord);

    constructor(uint64 _subscriptionId) VRFConsumerBaseV2(vrfCoordinator) {
        subscriptionId = _subscriptionId;
        linkToken = LinkTokenInterface(0x326C977E6efc84E512bB9C30f76E30c160eD06FB);
    }

    function requestRandomWords() external returns (uint256 requestId) {
        requestId = VRFCoordinatorV2Interface(vrfCoordinator).requestRandomWords(
            keyHash,
            subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );

        requestToSender[requestId] = msg.sender;
        emit RandomnessRequested(msg.sender, requestId);
    }

    function fulfillRandomWords(uint256 _requestId, uint256[] memory _randomWords) internal override {
        address sender = requestToSender[_requestId];
        randomResults[sender] = _randomWords[0];
        emit RandomnessFulfilled(_requestId, _randomWords[0]);
    }
}
```

---

## 五、跨链桥接

### 5.1 跨链消息传递

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ICrossChainBridge {
    function sendMessage(uint32 _destinationChainId, bytes calldata _payload) external payable;
    function receiveMessage(uint32 _sourceChainId, bytes calldata _payload) external;
}

contract CrossChainTokenBridge {
    // === LayerZero 风格跨链桥 ===

    mapping(uint16 => bytes) public trustedRemoteLookup; // chainId => remote address
    mapping(bytes32 => bool) public processedMessages;

    event MessageSent(uint16 indexed destChainId, bytes payload);
    event MessageReceived(uint16 indexed srcChainId, bytes payload);

    function setTrustedRemote(uint16 _remoteChainId, bytes calldata _remoteAddress) external {
        trustedRemoteLookup[_remoteChainId] = _remoteAddress;
    }

    function bridgeTokens(
        uint16 _dstChainId,
        address _to,
        uint256 _amount
    ) external payable {
        require(_amount > 0, "Zero amount");

        // 锁定代币（或销毁）
        // token.burn(msg.sender, _amount);
        // 或锁定
        // token.transferFrom(msg.sender, address(this), _amount);

        // 构造跨链消息
        bytes memory payload = abi.encode(
            msg.sender,    // from
            _to,           // to
            _amount,       // amount
            keccak256(abi.encode(block.timestamp, msg.sender)) // nonce
        );

        emit MessageSent(_dstChainId, payload);

        // 实际项目中调用 LayerZero / Wormhole / Axelar 的发送函数
        // ILayerZeroEndpoint(lzEndpoint).send{value: msg.value}(
        //     _dstChainId,
        //     trustedRemoteLookup[_dstChainId],
        //     payload,
        //     payable(msg.sender),
        //     address(0),
        //     bytes("")
        // );
    }

    // 接收跨链消息
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) external {
        // 验证来源
        require(
            keccak256(_srcAddress) == keccak256(trustedRemoteLookup[_srcChainId]),
            "Untrusted source"
        );

        // 防止重放
        bytes32 messageId = keccak256(abi.encodePacked(_srcChainId, _nonce, _payload));
        require(!processedMessages[messageId], "Message already processed");
        processedMessages[messageId] = true;

        // 解析消息
        (address from, address to, uint256 amount, bytes32 nonce) = abi.decode(_payload, (address, address, uint256, bytes32));

        // 铸造或释放代币
        // token.mint(to, amount);
        // 或解锁
        // token.transfer(to, amount);

        emit MessageReceived(_srcChainId, _payload);
    }
}
```

### 5.2 使用 Wormhole 进行跨链

```javascript
// 使用 Wormhole SDK 进行跨链代币转移
const { ethers } = require("ethers");
const { Wormhole } = require("@wormhole-foundation/connectors-evm");

// 源链和目标链配置
const sourceChain = "ethereum";
const destChain = "polygon";
const tokenAddress = "0x...";

// 配置 Wormhole
const wh = new Wormhole({
    networks: {
        ethereum: { rpc: "https://mainnet.infura.io/v3/YOUR_KEY" },
        polygon: { rpc: "https://polygon-rpc.com" },
    },
});

async function bridgeTokens() {
    // 1. 批准代币
    const token = new ethers.Contract(tokenAddress, erc20Abi, wallet);
    await token.approve(wormholeTokenBridgeAddress, amount);

    // 2. 发起跨链转移
    const receipt = await wh.transfer(
        sourceChain,
        tokenAddress,
        amount,
        destChain,
        recipientAddress
    );

    // 3. 等待 Wormhole 守护者网络签名 VAA
    const vaa = await wh.getVaa(receipt.txHash, "TokenBridge");

    // 4. 在目标链上领取
    await wh.redeem(destChain, vaa);
}
```

---

## 六、最佳实践

### 6.1 安全设计原则

| 原则 | 说明 |
|------|------|
| **使用 CEI 模式** | Checks → Effects → Interactions，防止重入 |
| **预言机操纵防护** | 使用 TWAP 或 Chainlink，不使用单一 DEX 现价 |
| **闪电贷防护** | 检查 `block.number == tx.origin` 或使用时间锁 |
| **合理抵押率** | 抵押率 ≤ 80%，清算阈值留有缓冲 |
| **紧急暂停** | 所有核心合约内置 Pausable |
| **多签管理** | 关键操作（参数调整、资金提取）使用多签 |
| **审计** | 主网部署前必须经过专业审计 |
| **形式化验证** | 高价值协议使用 Certora 等 |

### 6.2 利率模型

```solidity
// 基于利用率的利率模型（类似 Compound）
pragma solidity ^0.8.20;

contract InterestRateModel {
    uint256 public constant BASE_RATE = 2e16;          // 2% 基础利率
    uint256 public constant MULTIPLIER = 1e17;          // 乘数
    uint256 public constant JUMP_MULTIPLIER = 9e17;      // 跳跃乘数
    uint256 public constant KINK = 8e17;                 // 拐点 80%

    function getBorrowRate(
        uint256 cash,
        uint256 borrows,
        uint256 reserves
    ) public view returns (uint256) {
        uint256 totalSupply = cash + borrows - reserves;
        if (totalSupply == 0) return BASE_RATE;

        uint256 utilizationRate = (borrows * 1e18) / totalSupply;

        if (utilizationRate <= KINK) {
            // 正常区间
            return BASE_RATE + (utilizationRate * MULTIPLIER) / 1e18;
        } else {
            // 超过拐点，利率陡峭上升
            uint256 excessUtilization = utilizationRate - KINK;
            return BASE_RATE
                + (KINK * MULTIPLIER) / 1e18
                + (excessUtilization * JUMP_MULTIPLIER) / 1e18;
        }
    }
}
```

---

## 相关页面

- [[智能合约开发]] - Solidity 基础与开发框架
- [[NFT开发指南]] - NFT 市场与协议
- [[Web3后端开发]] - 后端服务与索引
- [[Layer2与扩容方案]] - L2 上的 DeFi 应用
