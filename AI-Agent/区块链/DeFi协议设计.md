---
title: DeFi协议设计
aliases:
  - DeFi Protocol Design
  - 去中心化金融
  - DeFi开发
tags:
  - defi
  - amm
  - lending
  - flash-loan
  - oracle
  - liquidity
  - ethereum
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: original
difficulty: advanced
project: AI-Agent-Wiki
---

# DeFi协议设计

> 去中心化金融 (DeFi) 通过智能合约构建开放式金融系统。本文涵盖自动做市商 (AMM)、借贷协议、流动性池、闪电贷与预言机的核心设计原理及代码实现。

## 目录

- [1. 自动做市商 (AMM)](#1-自动做市商-amm)
- [2. 借贷协议](#2-借贷协议)
- [3. 流动性池设计](#3-流动性池设计)
- [4. 闪电贷](#4-闪电贷)
- [5. 预言机](#5-预言机)
- [6. 最佳实践](#6-最佳实践)
- [7. 相关页面](#7-相关页面)

---

## 1. 自动做市商 (AMM)

### 1.1 恒定乘积公式

Uniswap V2 使用 **x * y = k** 恒定乘积公式：

```
(x + Δx)(y - Δy) = k = x * y

其中：
  x = 代币A的储备量
  y = 代币B的储备量
  Δx = 买入的代币A数量
  Δy = 卖出的代币B数量
```

交易输出量计算：

```
Δy = y * Δx_in * (1 - fee) / (x + Δx_in * (1 - fee))

Uniswap V2 fee = 0.3% (30 bps)
```

### 1.2 Solidity 实现：简化版 AMM

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title 简化版恒定乘积 AMM (类似 Uniswap V2)
contract SimpleAMM is ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public tokenA;
    address public tokenB;
    uint256 public reserveA;
    uint256 public reserveB;

    uint256 public constant FEE_BPS = 30; // 0.3%
    uint256 public constant BPS_DENOMINATOR = 10000;

    uint256 public totalLiquidity;
    mapping(address => uint256) public liquidityOf;

    event LiquidityAdded(address provider, uint256 amountA, uint256 amountB, uint256 lpTokens);
    event LiquidityRemoved(address provider, uint256 amountA, uint256 amountB, uint256 lpTokens);
    event Swap(address user, address tokenIn, uint256 amountIn, address tokenOut, uint256 amountOut);

    constructor(address _tokenA, address _tokenB) {
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    // ===== 添加流动性 =====
    function addLiquidity(uint256 amountA, uint256 amountB) external nonReentrant returns (uint256 lpMinted) {
        require(amountA > 0 && amountB > 0, "Zero amounts");

        IERC20(tokenA).safeTransferFrom(msg.sender, address(this), amountA);
        IERC20(tokenB).safeTransferFrom(msg.sender, address(this), amountB);

        if (totalLiquidity == 0) {
            // 首次添加: LP = sqrt(amountA * amountB)
            lpMinted = sqrt(amountA * amountB);
        } else {
            // 后续添加: 按比例铸造 LP
            uint256 lpA = (amountA * totalLiquidity) / reserveA;
            uint256 lpB = (amountB * totalLiquidity) / reserveB;
            require(lpA == lpB, "Imbalanced ratio");
            lpMinted = lpA;
        }

        liquidityOf[msg.sender] += lpMinted;
        totalLiquidity += lpMinted;
        reserveA += amountA;
        reserveB += amountB;

        emit LiquidityAdded(msg.sender, amountA, amountB, lpMinted);
    }

    // ===== 移除流动性 =====
    function removeLiquidity(uint256 lpAmount) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(liquidityOf[msg.sender] >= lpAmount, "Insufficient LP");

        amountA = (lpAmount * reserveA) / totalLiquidity;
        amountB = (lpAmount * reserveB) / totalLiquidity;

        liquidityOf[msg.sender] -= lpAmount;
        totalLiquidity -= lpAmount;
        reserveA -= amountA;
        reserveB -= amountB;

        IERC20(tokenA).safeTransfer(msg.sender, amountA);
        IERC20(tokenB).safeTransfer(msg.sender, amountB);

        emit LiquidityRemoved(msg.sender, amountA, amountB, lpAmount);
    }

    // ===== 交换代币 =====
    function swap(address tokenIn, uint256 amountIn)
        external
        nonReentrant
        returns (uint256 amountOut)
    {
        require(amountIn > 0, "Zero input");
        require(tokenIn == tokenA || tokenIn == tokenB, "Invalid token");

        address tokenOut = tokenIn == tokenA ? tokenB : tokenA;
        uint256 reserveIn = tokenIn == tokenA ? reserveA : reserveB;
        uint256 reserveOut = tokenIn == tokenA ? reserveB : reserveA;

        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

        // 计算输出 (扣除手续费)
        uint256 amountInWithFee = (amountIn * (BPS_DENOMINATOR - FEE_BPS)) / BPS_DENOMINATOR;
        amountOut = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee);
        require(amountOut > 0, "Zero output");

        // 更新储备量
        if (tokenIn == tokenA) {
            reserveA += amountIn;
            reserveB -= amountOut;
        } else {
            reserveB += amountIn;
            reserveA -= amountOut;
        }

        IERC20(tokenOut).safeTransfer(msg.sender, amountOut);

        emit Swap(msg.sender, tokenIn, amountIn, tokenOut, amountOut);
    }

    // ===== 获取报价 (不执行交易) =====
    function getAmountOut(address tokenIn, uint256 amountIn) external view returns (uint256) {
        uint256 reserveIn = tokenIn == tokenA ? reserveA : reserveB;
        uint256 reserveOut = tokenIn == tokenA ? reserveB : reserveA;
        uint256 amountInWithFee = (amountIn * (BPS_DENOMINATOR - FEE_BPS)) / BPS_DENOMINATOR;
        return (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee);
    }

    function sqrt(uint256 x) internal pure returns (uint256 y) {
        uint256 z = (x + 1) / 2;
        y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
    }
}
```

### 1.3 Python AMM 模拟

```python
class AMMSimulator:
    """恒定乘积 AMM (x * y = k) 模拟器"""
    def __init__(self, reserve_a: float, reserve_b: float, fee_bps: int = 30):
        self.reserve_a = reserve_a
        self.reserve_b = reserve_b
        self.fee_rate = fee_bps / 10000  # 0.003 = 0.3%
        self.k = reserve_a * reserve_b
        self.total_lp = (reserve_a * reserve_b) ** 0.5
        print(f"Pool initialized: A={reserve_a}, B={reserve_b}, k={self.k:.2f}, LP={self.total_lp:.2f}")

    def get_amount_out(self, token_in: str, amount_in: float) -> float:
        """计算给定输入量能得到多少输出"""
        if token_in == "A":
            reserve_in, reserve_out = self.reserve_a, self.reserve_b
        else:
            reserve_in, reserve_out = self.reserve_b, self.reserve_a

        amount_in_after_fee = amount_in * (1 - self.fee_rate)
        amount_out = (reserve_out * amount_in_after_fee) / (reserve_in + amount_in_after_fee)
        return amount_out

    def swap(self, token_in: str, amount_in: float) -> float:
        """执行交换"""
        amount_out = self.get_amount_out(token_in, amount_in)

        if token_in == "A":
            self.reserve_a += amount_in
            self.reserve_b -= amount_out
        else:
            self.reserve_b += amount_in
            self.reserve_a -= amount_out

        new_k = self.reserve_a * self.reserve_b
        print(f"  Swap {amount_in} {token_in} → {amount_out:.6f} {'B' if token_in == 'A' else 'A'}"
              f" | Reserves: A={self.reserve_a:.4f}, B={self.reserve_b:.4f}, k={new_k:.2f}")
        return amount_out

    def get_price(self) -> float:
        """A 相对于 B 的价格"""
        return self.reserve_b / self.reserve_a


# === 模拟交易 ===
pool = AMMSimulator(reserve_a=100000, reserve_b=100000)  # 1 A = 1 B
print(f"\nInitial price: 1 A = {pool.get_price()} B")

# 大额交易会产生滑点
print("\n--- Small swap ---")
pool.swap("A", 100)   # 小额: 低滑点

print("\n--- Large swap ---")
pool.swap("A", 10000)  # 大额: 高滑点

print(f"\nFinal price: 1 A = {pool.get_price():.6f} B")
```

---

## 2. 借贷协议

### 2.1 核心概念

```
                    借贷协议架构
    ┌──────────────────────────────────┐
    │            利率模型               │
    │    (利用率 → 借贷利率)             │
    ├──────────────────────────────────┤
    │  存款人         借款人             │
    │  提供资金    →   借出资金           │
    │  赚取利息        支付利息           │
    │  获得cToken      提供抵押品         │
    ├──────────────────────────────────┤
    │         清算机制                   │
    │  (抵押率 < 清算阈值 → 清算)         │
    └──────────────────────────────────┘
```

### 2.2 利率模型

```
Utilization Rate (U) = Total Borrows / Total Liquidity

Borrow APY = Base Rate + (U * Multiplier)        (当 U < Kink)
Borrow APY = Base Rate + (Kink * Multiplier)
             + (U - Kink) * JumpMultiplier       (当 U >= Kink)

Supply APY = Borrow APY * U * (1 - Reserve Factor)
```

```python
class InterestRateModel:
    """Compound 风格跳跃式利率模型"""
    def __init__(self, base_rate=0.02, multiplier=0.1, jump_multiplier=2.0, kink=0.8, reserve_factor=0.1):
        self.base_rate = base_rate           # 基础年利率 2%
        self.multiplier = multiplier         # 斜率 (kink 前)
        self.jump_multiplier = jump_multiplier  # 斜率 (kink 后)
        self.kink = kink                     # 利用率拐点 80%
        self.reserve_factor = reserve_factor # 协议保留比例 10%

    def get_borrow_rate(self, utilization: float) -> float:
        """根据利用率计算借款年化利率"""
        if utilization <= self.kink:
            return self.base_rate + utilization * self.multiplier
        else:
            rate_at_kink = self.base_rate + self.kink * self.multiplier
            excess = utilization - self.kink
            return rate_at_kink + excess * self.jump_multiplier

    def get_supply_rate(self, utilization: float) -> float:
        """存款年化利率"""
        borrow_rate = self.get_borrow_rate(utilization)
        return borrow_rate * utilization * (1 - self.reserve_factor)

    def show_curve(self):
        """打印利率曲线"""
        print(f"{'利用率':>8} | {'借款APY':>10} | {'存款APY':>10}")
        print("-" * 36)
        for pct in range(0, 101, 10):
            u = pct / 100
            borrow_apy = self.get_borrow_rate(u)
            supply_apy = self.get_supply_rate(u)
            print(f"{pct:>7}% | {borrow_apy:>9.2%} | {supply_apy:>9.2%}")


# === 查看利率曲线 ===
model = InterestRateModel()
model.show_curve()

# 输出:
#      利用率 |     借款APY |     存款APY
# ------------------------------------
#        0% |     2.00% |     0.00%
#       10% |     3.00% |     0.27%
#       20% |     4.00% |     0.72%
#       ...
#       80% |    10.00% |     7.20%  ← Kink
#       90% |    30.00% |    24.30%  ← 跳跃
#      100% |    50.00% |    45.00%
```

### 2.3 Solidity 借贷合约（简化版）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title 简化版借贷协议
contract SimpleLending is ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct Market {
        address token;
        bool isListed;
        uint256 collateralFactor;  // 抵押率 (e.g., 75% = 7500)
        uint256 totalDeposits;
        uint256 totalBorrows;
        uint256 borrowRate;        // 年化利率 (basis points)
    }

    mapping(address => Market) public markets;
    mapping(address => mapping(address => uint256)) public deposits;   // user => token => amount
    mapping(address => mapping(address => uint256)) public borrows;    // user => token => amount
    address public oracle; // Price Oracle address

    uint256 public constant COLLATERAL_FACTOR_MAX = 10000; // 100%
    uint256 public constant LIQUIDATION_THRESHOLD = 8000;  // 80%

    event Deposited(address user, address token, uint256 amount);
    event Borrowed(address user, address token, uint256 amount);
    event Repaid(address user, address token, uint256 amount);
    event Liquidated(address liquidator, address user, uint256 debtCovered);

    constructor(address _oracle) {
        oracle = _oracle;
    }

    function listMarket(address token, uint256 collateralFactor) external {
        require(collateralFactor <= COLLATERAL_FACTOR_MAX, "Factor too high");
        markets[token] = Market(token, true, collateralFactor, 0, 0, 500); // 5% APR
    }

    // ===== 存款 (作为抵押品) =====
    function deposit(address token, uint256 amount) external nonReentrant {
        require(markets[token].isListed, "Market not listed");
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        deposits[msg.sender][token] += amount;
        markets[token].totalDeposits += amount;
        emit Deposited(msg.sender, token, amount);
    }

    // ===== 借款 =====
    function borrow(address token, uint256 amount) external nonReentrant {
        require(markets[token].isListed, "Market not listed");

        // 检查抵押品是否足够
        uint256 collateralValue = _getAccountLiquidity(msg.sender);
        uint256 borrowValue = _getTokenValue(token, amount);
        require(collateralValue >= borrowValue, "Insufficient collateral");

        require(IERC20(token).balanceOf(address(this)) >= amount, "Not enough liquidity");

        borrows[msg.sender][token] += amount;
        markets[token].totalBorrows += amount;

        IERC20(token).safeTransfer(msg.sender, amount);
        emit Borrowed(msg.sender, token, amount);
    }

    // ===== 还款 =====
    function repay(address token, uint256 amount) external nonReentrant {
        require(borrows[msg.sender][token] >= amount, "Amount exceeds debt");
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        borrows[msg.sender][token] -= amount;
        markets[token].totalBorrows -= amount;
        emit Repaid(msg.sender, token, amount);
    }

    // ===== 清算 =====
    function liquidate(address user, address debtToken, uint256 coverAmount) external nonReentrant {
        // 检查借款人是否资不抵债
        uint256 accountLiquidity = _getAccountLiquidity(user);
        require(accountLiquidity < 0 || _isUnderwater(user), "Account not liquidatable");

        uint256 debt = borrows[user][debtToken];
        uint256 closeAmount = coverAmount > debt ? debt : coverAmount;

        // 清算人替借款人还款
        IERC20(debtToken).safeTransferFrom(msg.sender, address(this), closeAmount);
        borrows[user][debtToken] -= closeAmount;

        // 清算人获得折扣抵押品 (清算激励 5%)
        // ... 简化: 假设用抵押品 token 偿还
        emit Liquidated(msg.sender, user, closeAmount);
    }

    // ===== 内部: 计算账户流动性 =====
    function _getAccountLiquidity(address user) internal view returns (uint256) {
        uint256 totalCollateralValue = 0;
        uint256 totalBorrowValue = 0;

        // 遍历所有市场计算 (简化)
        // 实际实现中通过映射跟踪用户活跃市场
        // totalCollateralValue = deposits * collateralFactor * price
        // totalBorrowValue = borrows * price

        return totalCollateralValue > totalBorrowValue
            ? totalCollateralValue - totalBorrowValue
            : 0;
    }

    function _getTokenValue(address token, uint256 amount) internal view returns (uint256) {
        // 调用预言机获取价格
        // return IPriceOracle(oracle).getPrice(token) * amount;
        return amount; // 简化
    }

    function _isUnderwater(address user) internal view returns (bool) {
        return false; // 简化
    }
}
```

---

## 3. 流动性池设计

### 3.1 流动性池类型对比

| 类型 | 公式 | 代表协议 | 特点 |
|------|------|---------|------|
| 恒定乘积 | x * y = k | Uniswap V2 | 简单通用，高滑点 |
| 恒定和 | x + y = C | StableSwap | 低滑点，适合稳定币 |
| 集中流动性 | 自定义区间 | Uniswap V3 | 资本效率高 |
| 权重池 | ∏(R_i^W_i) | Balancer | 多资产灵活配比 |

### 3.2 Uniswap V3 集中流动性概念

```python
class ConcentratedLiquidityPool:
    """
    简化版集中流动性模型 (Uniswap V3 风格)
    LP 可以选择在特定价格区间提供流动性
    """
    def __init__(self, price_current: float):
        self.price = price_current  # 当前价格
        self.liquidity = 0          # 流动性 (L)
        self.positions = []         # 所有 LP 仓位

    def add_position(self, lower_price: float, upper_price: float, amount: float):
        """在 [lower, upper] 价格区间添加流动性"""
        if lower_price <= self.price <= upper_price:
            self.positions.append({
                'lower': lower_price,
                'upper': upper_price,
                'amount': amount,
            })
            # 计算有效流动性
            self.liquidity += amount / ((1/abs(self.price - lower_price)**0.5 + 1/abs(upper_price - self.price)**0.5))
            print(f"  +Added {amount} in [{lower_price}, {upper_price}], active liquidity: {self.liquidity:.2f}")
        else:
            print(f"  Position [{lower_price}, {upper_price}] out of range, not active")

    def total_active_liquidity(self) -> float:
        """当前价格区间的有效流动性"""
        active = sum(p['amount'] for p in self.positions
                     if p['lower'] <= self.price <= p['upper'])
        return active


# === 模拟 ===
pool = ConcentratedLiquidityPool(price_current=2000)  # ETH = $2000
pool.add_position(1800, 2200, 100000)  # 紧密区间
pool.add_position(1500, 2500, 50000)   # 宽松区间
pool.add_position(1000, 1500, 30000)   # 不在区间内
print(f"\nTotal active liquidity: ${pool.total_active_liquidity():,.0f}")
```

---

## 4. 闪电贷

### 4.1 核心原理

```
闪电贷 (Flash Loan):
    在同一笔交易中借入并归还资金，无需抵押品。
    如果未归还，整个交易回滚 (revert)。

    典型用途:
    1. 套利 (不同 DEX 之间的价格差)
    2. 自我清算 (清算自己的抵押仓位)
    3. 债务置换 (将 A 协议的贷款转移到 B 协议)

    安全模型:
    借入 → 执行操作 → 归还 (本金 + 手续费 0.09%)
    ────────────────  同一区块  ────────────────
```

### 4.2 闪电贷池合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface IFlashLoanReceiver {
    /// @notice 闪电贷回调函数
    /// @dev 借款人必须在此函数内归还贷款
    function executeOperation(
        address token,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

/// @title 闪电贷池
contract FlashLoanPool is ReentrancyGuard {
    using SafeERC20 for IERC20;

    uint256 public constant PREMIUM_BPS = 9; // 0.09% 手续费
    uint256 public constant BPS_DENOMINATOR = 10000;
    mapping(address => bool) public supportedTokens;

    event FlashLoan(address initiator, address token, uint256 amount, uint256 premium);

    function flashLoan(
        address token,
        uint256 amount,
        bytes calldata params
    ) external nonReentrant {
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        require(balanceBefore >= amount, "Not enough liquidity");

        uint256 premium = (amount * PREMIUM_BPS) / BPS_DENOMINATOR;

        // 转账给借款人
        IERC20(token).safeTransfer(msg.sender, amount);

        // 调用借款人的回调
        bool success = IFlashLoanReceiver(msg.sender).executeOperation(
            token,
            amount,
            premium,
            msg.sender,
            params
        );
        require(success, "Callback failed");

        // 验证归还
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        require(balanceAfter >= balanceBefore + premium, "Flash loan not repaid");

        emit FlashLoan(msg.sender, token, amount, premium);
    }
}
```

### 4.3 闪电贷套利合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

interface IFlashLoanPool {
    function flashLoan(address token, uint256 amount, bytes calldata params) external;
}

interface IAMM {
    function swap(address tokenIn, uint256 amountIn) external returns (uint256);
    function getAmountOut(address tokenIn, uint256 amountIn) external view returns (uint256);
}

/// @title 闪电贷套利机器人
contract FlashArbitrage is IFlashLoanReceiver {
    using SafeERC20 for IERC20;

    address public owner;
    address public flashPool;
    address public amm1;  // DEX 1
    address public amm2;  // DEX 2

    constructor(address _flashPool, address _amm1, address _amm2) {
        owner = msg.sender;
        flashPool = _flashPool;
        amm1 = _amm1;
        amm2 = _amm2;
    }

    /// @notice 发起套利
    function startArbitrage(address token, uint256 amount) external {
        bytes memory params = abi.encode(token);
        IFlashLoanPool(flashPool).flashLoan(token, amount, params);
    }

    /// @notice 闪电贷回调
    function executeOperation(
        address token,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == flashPool, "Unauthorized");
        require(initiator == address(this), "Invalid initiator");

        // Step 1: 在 AMM1 买入 tokenB
        uint256 tokenBReceived = IAMM(amm1).swap(token, amount);

        // Step 2: 在 AMM2 卖出 tokenB 换回 tokenA
        // ...确定 tokenB 地址并执行交换...

        // Step 3: 计算利润
        uint256 totalOwed = amount + premium;
        uint256 balance = IERC20(token).balanceOf(address(this));

        require(balance >= totalOwed, "No profit");

        // Step 4: 归还闪电贷
        IERC20(token).safeApprove(flashPool, totalOwed);

        // Step 5: 提取利润
        uint256 profit = balance - totalOwed;
        if (profit > 0) {
            IERC20(token).safeTransfer(owner, profit);
        }

        return true;
    }
}
```

---

## 5. 预言机

### 5.1 预言机类型

| 类型 | 说明 | 代表 |
|------|------|------|
| **链下预言机** | 从外部API获取数据 | Chainlink, API3, Pyth |
| **链上预言机** | 从 DEX 获取价格 | Uniswap TWAP |
| **推式预言机** | 定期推送价格 | Chainlink (push model) |
| **拉式预言机** | 按需拉取价格 | Pyth Network (pull model) |

### 5.2 Chainlink 价格预言机集成

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/// @title Chainlink 价格消费者
contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    /// @notice 获取最新价格
    /// @return price 最新价格 (8位小数)
    function getLatestPrice() public view returns (int256) {
        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        require(updatedAt != 0, "Round not complete");
        require(block.timestamp - updatedAt < 3600, "Stale price"); // 1小时过期
        require(price > 0, "Invalid price");

        return price;
    }

    /// @notice 带安全检查的价格获取
    function getSafePrice() external view returns (uint256) {
        int256 rawPrice = getLatestPrice();
        // Chainlink ETH/USD 使用 8 位小数
        // 转换为 18 位小数
        return uint256(rawPrice) * 1e10;
    }
}

// === 常用 Chainlink Price Feed 地址 (ETH Mainnet) ===
// ETH/USD:  0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
// BTC/USD:  0xF4030086522a5bEEa4988F38c5DfE0e92D2cAC8
// LINK/USD: 0x2c1d072e956AFFC0D435Cb85AC109eC5a6e7e0F
// USDC/USD: 0x8fFfFfd4AfB6115b954Bd326cbe7B41564607932
```

### 5.3 TWAP (时间加权平均价格) 预言机

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title 简化版 TWAP 预言机
contract TWAPOracle {
    struct Observation {
        uint256 timestamp;
        uint256 priceCumulative;
    }

    Observation[] public observations;
    uint256 public period = 1800; // 30 分钟窗口

    function update(uint256 currentPrice) external {
        if (observations.length == 0) {
            observations.push(Observation(block.timestamp, currentPrice));
        } else {
            Observation storage last = observations[observations.length - 1];
            uint256 timeElapsed = block.timestamp - last.timestamp;
            uint256 newCumulative = last.priceCumulative + (currentPrice * timeElapsed);
            observations.push(Observation(block.timestamp, newCumulative));
        }
    }

    function getTWAP() external view returns (uint256) {
        require(observations.length >= 2, "Not enough data");

        Observation storage current = observations[observations.length - 1];

        // 找到 period 之前的观察点
        uint256 targetTime = current.timestamp - period;
        uint256 i = observations.length - 1;
        while (i > 0 && observations[i].timestamp > targetTime) {
            i--;
        }

        Observation storage historical = observations[i];
        uint256 timeElapsed = current.timestamp - historical.timestamp;
        uint256 priceDelta = current.priceCumulative - historical.priceCumulative;

        return priceDelta / timeElapsed;
    }
}
```

### 5.4 Python 价格聚合器

```python
import time
from typing import Optional

class PriceAggregator:
    """多源价格聚合器 (防止预言机操纵)"""
    def __init__(self):
        self.sources = {}  # source_name -> [(timestamp, price), ...]

    def add_price(self, source: str, price: float):
        if source not in self.sources:
            self.sources[source] = []
        self.sources[source].append((time.time(), price))
        # 只保留最近 1 小时数据
        cutoff = time.time() - 3600
        self.sources[source] = [(t, p) for t, p in self.sources[source] if t > cutoff]

    def get_median_price(self, max_staleness: int = 300) -> Optional[float]:
        """获取中位数价格 (抗操纵)"""
        latest_prices = []
        now = time.time()

        for source, history in self.sources.items():
            if history and (now - history[-1][0]) < max_staleness:
                latest_prices.append(history[-1][1])

        if len(latest_prices) < 2:
            return None

        latest_prices.sort()
        mid = len(latest_prices) // 2
        if len(latest_prices) % 2 == 0:
            return (latest_prices[mid - 1] + latest_prices[mid]) / 2
        else:
            return latest_prices[mid]

    def detect_outlier(self, price: float, threshold: float = 0.05) -> bool:
        """检测异常价格 (偏离中位数 > threshold)"""
        median = self.get_median_price()
        if median is None:
            return False
        deviation = abs(price - median) / median
        return deviation > threshold


# === 使用示例 ===
aggregator = PriceAggregator()
aggregator.add_price("Chainlink", 2000.0)
aggregator.add_price("Uniswap", 2005.0)
aggregator.add_price("Coinbase", 2002.0)
aggregator.add_price("Binance", 2001.0)

median = aggregator.get_median_price()
print(f"Median ETH price: ${median:.2f}")

# 异常检测
print(f"Price 2003 is outlier? {aggregator.detect_outlier(2003.0)}")
print(f"Price 2500 is outlier? {aggregator.detect_outlier(2500.0)}")
```

---

## 6. 最佳实践

### 安全设计原则

| 原则 | 说明 |
|------|------|
| **重入保护** | 所有涉及资金转移的函数使用 `ReentrancyGuard` |
| **超额抵押** | 借贷协议使用 120%-150% 抵押率 |
| **清算机制** | 自动化清算，设置合理的清算激励 (5%-10%) |
| **预言机安全** | 多源聚合，TWAP 平滑，异常检测 |
| **审计** | 主网部署前必须通过专业审计 |
| **渐进式部署** | 先在测试网充分测试，主网以小金额开始 |
| **紧急开关** | 设置 Pause / Kill Switch 机制 |
| **保险基金** | 预留资金应对坏账 |

### 常用审计工具与公司

- **静态分析**: [Slither](https://github.com/crytic/slither), [Mythril](https://github.com/Consensys/mythril)
- **模糊测试**: [Echidna](https://github.com/crytic/echidna), [Foundry Fuzz](https://book.getfoundry.sh/forge/fuzz-tests)
- **形式化验证**: [Certora Prover](https://www.certora.com/)
- **审计公司**: OpenZeppelin, ConsenSys Diligence, Trail of Bits, CertiK, Spearbit

### DeFi 风险类型

```
┌─────────────────────────────────────────────┐
│               DeFi 风险分层                   │
├──────────────┬──────────────────────────────┤
│ 智能合约风险   │ 代码漏洞、重入攻击、逻辑错误    │
├──────────────┼──────────────────────────────┤
│ 协议治理风险   │ 恶意提案、多签被控制           │
├──────────────┼──────────────────────────────┤
│ 预言机风险     │ 价格操纵、延迟、停机           │
├──────────────┼──────────────────────────────┤
│ 系统性风险     │ 级联清算、流动性枯竭           │
├──────────────┼──────────────────────────────┤
│ 前端风险      │ 钓鱼、DNS 劫持、API 宕机       │
└──────────────┴──────────────────────────────┘
```

---

## 7. 相关页面

- [[区块链基础原理]] - 区块结构、共识机制、智能合约基础
- [[以太坊开发指南]] - Solidity、Hardhat、合约部署
- [[NFT与数字资产]] - ERC-721 / ERC-1155 标准
- [[Layer2扩容方案]] - 扩容方案，降低 DeFi Gas 成本

---

## 参考资源

- [Uniswap V2 Whitepaper](https://uniswap.org/whitepaper.pdf)
- [Uniswap V3 Whitepaper](https://uniswap.org/whitepaper-v3.pdf)
- [Compound Whitepaper](https://compound.finance/documents/Compound.whitepaper.pdf)
- [Aave Documentation](https://docs.aave.com/)
- [Chainlink Documentation](https://docs.chain.link/)
- [DeFi Pulse](https://defipulse.com/) - DeFi 数据追踪
- [DeFi Llama](https://defillama.com/) - TVL 排行
