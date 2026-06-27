---
title: NFT与数字资产
aliases:
  - NFT and Digital Assets
  - 非同质化代币
  - ERC-721
  - ERC-1155
tags:
  - nft
  - erc721
  - erc1155
  - ipfs
  - metadata
  - marketplace
  - web3
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: original
difficulty: intermediate
project: AI-Agent-Wiki
---

# NFT与数字资产

> 非同质化代币 (NFT) 是区块链上唯一不可替换的数字资产标识。本文涵盖 ERC-721/ERC-1155 标准、IPFS 去中心化存储、元数据规范及 NFT 市场合约设计。

## 目录

- [1. ERC-721 标准](#1-erc-721-标准)
- [2. ERC-1155 多代币标准](#2-erc-1155-多代币标准)
- [3. IPFS 去中心化存储](#3-ipfs-去中心化存储)
- [4. 元数据规范](#4-元数据规范)
- [5. NFT 市场合约](#5-nft-市场合约)
- [6. 最佳实践](#6-最佳实践)
- [7. 相关页面](#7-相关页面)

---

## 1. ERC-721 标准

ERC-721 是最经典的 NFT 标准，每个代币都有唯一的 `tokenId`。

### 1.1 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ERC-721 标准接口
interface IERC721 {
    // ===== 事件 =====
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    // ===== 查询函数 =====
    function balanceOf(address owner) external view returns (uint256 balance);
    function ownerOf(uint256 tokenId) external view returns (address owner);

    // ===== 转账函数 =====
    function transferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata data) external;

    // ===== 授权函数 =====
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address operator);
    function isApprovedForAll(address owner, address operator) external view returns (bool);
}

/// @title ERC-721 元数据扩展接口
interface IERC721Metadata {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function tokenURI(uint256 tokenId) external view returns (string memory);
}
```

### 1.2 完整 ERC-721 实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/// @title 艺术品 NFT 合约
contract ArtNFT is ERC721, ERC721URIStorage, ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MINT_PRICE = 0.05 ether;

    struct ArtPiece {
        uint256 tokenId;
        address creator;
        string title;
        uint256 mintedAt;
    }

    mapping(uint256 => ArtPiece) public artPieces;
    mapping(address => uint256[]) public ownedTokens;

    event Minted(address indexed creator, uint256 indexed tokenId, string tokenURI);

    constructor() ERC721("Art Collection", "ART") {}

    // ===== 铸造 NFT =====
    function mint(string memory _tokenURI) public payable returns (uint256) {
        uint256 currentId = _tokenIdCounter.current();
        require(currentId < MAX_SUPPLY, "Max supply reached");
        require(msg.value >= MINT_PRICE, "Insufficient ETH");

        _tokenIdCounter.increment();
        uint256 newTokenId = _tokenIdCounter.current();

        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, _tokenURI);

        artPieces[newTokenId] = ArtPiece(newTokenId, msg.sender, "", block.timestamp);
        ownedTokens[msg.sender].push(newTokenId);

        emit Minted(msg.sender, newTokenId, _tokenURI);
        return newTokenId;
    }

    // ===== 批量铸造 =====
    function batchMint(string[] memory _tokenURIs) public payable onlyOwner {
        for (uint256 i = 0; i < _tokenURIs.length; i++) {
            _tokenIdCounter.increment();
            uint256 newTokenId = _tokenIdCounter.current();
            _safeMint(msg.sender, newTokenId);
            _setTokenURI(newTokenId, _tokenURIs[i]);
        }
    }

    // ===== 版税 (ERC-2981) =====
    function royaltyInfo(uint256 /* tokenId */, uint256 salePrice)
        external
        view
        returns (address receiver, uint256 royaltyAmount)
    {
        return (owner(), (salePrice * 500) / 10000); // 5% 版税
    }

    // ===== 提取合约资金 =====
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        (bool success, ) = owner().call{value: balance}("");
        require(success, "Withdraw failed");
    }

    // ===== 重写必需函数 (多继承) =====
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }
}
```

---

## 2. ERC-1155 多代币标准

ERC-1155 允许在单个合约中管理**多种代币类型**（同质化 + 非同质化），大幅降低 Gas 成本。

### 2.1 标准接口

```solidity
interface IERC1155 {
    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);
    event TransferBatch(address indexed operator, address indexed from, address indexed to, uint256[] ids, uint256[] values);
    event ApprovalForAll(address indexed account, address indexed operator, bool approved);
    event URI(string value, uint256 indexed id);

    function balanceOf(address account, uint256 id) external view returns (uint256);
    function balanceOfBatch(address[] calldata accounts, uint256[] calldata ids)
        external view returns (uint256[] memory);
    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external;
    function safeBatchTransferFrom(address from, address to, uint256[] calldata ids, uint256[] calldata amounts, bytes calldata data) external;
}
```

### 2.2 完整 ERC-1155 实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/// @title 游戏道具 NFT (ERC-1155)
contract GameItems is ERC1155, Ownable {
    using Strings for uint256;

    // 道具 ID 枚举
    uint256 public constant GOLD = 0;
    uint256 public constant SWORD = 1;
    uint256 public constant SHIELD = 2;
    uint256 public constant HEALTH_POTION = 3;
    uint256 public constant RARE_CHEST = 4;

    // 每种道具的最大供应量 (0 = 无限)
    mapping(uint256 => uint256) public maxSupply;
    // 铸造价格
    mapping(uint256 => uint256) public mintPrices;

    event ItemMinted(address indexed to, uint256 indexed id, uint256 amount);

    constructor() ERC1155("https://game-api.example.com/api/item/{id}.json") {
        // 初始化供应量
        maxSupply[SWORD] = 100;
        maxSupply[SHIELD] = 200;
        maxSupply[HEALTH_POTION] = 10000;
        maxSupply[RARE_CHEST] = 10;

        // 初始化价格
        mintPrices[SWORD] = 0.1 ether;
        mintPrices[SHIELD] = 0.08 ether;
        mintPrices[HEALTH_POTION] = 0.01 ether;
        mintPrices[RARE_CHEST] = 1 ether;

        // 给合约部署者铸造初始道具
        _mint(msg.sender, GOLD, 1000000 * 10**18, "");
        _mint(msg.sender, SWORD, 10, "");
        _mint(msg.sender, SHIELD, 20, "");
        _mint(msg.sender, HEALTH_POTION, 100, "");
    }

    // ===== 单个铸造 =====
    function mint(uint256 id, uint256 amount) external payable {
        require(mintPrices[id] > 0, "Not mintable");
        require(msg.value >= mintPrices[id] * amount, "Insufficient payment");

        uint256 currentSupply = ERC1155(this).balanceOf(msg.sender, id);
        if (maxSupply[id] > 0) {
            require(currentSupply + amount <= maxSupply[id], "Exceeds max supply");
        }

        _mint(msg.sender, id, amount, "");
        emit ItemMinted(msg.sender, id, amount);
    }

    // ===== 批量铸造 =====
    function mintBatch(uint256[] memory ids, uint256[] memory amounts) external payable onlyOwner {
        _mintBatch(msg.sender, ids, amounts, "");
    }

    // ===== 动态 URI =====
    function uri(uint256 id) public view override returns (string memory) {
        return string(abi.encodePacked("https://game-api.example.com/api/item/", id.toString(), ".json"));
    }

    // ===== 提取资金 =====
    function withdraw() external onlyOwner {
        (bool success, ) = owner().call{value: address(this).balance}("");
        require(success, "Withdraw failed");
    }
}
```

### ERC-721 vs ERC-1155 对比

| 特性 | ERC-721 | ERC-1155 |
|------|---------|----------|
| 代币类型 | 仅 NFT (唯一) | NFT + FT (混合) |
| 合约数量 | 每个集合一个合约 | 多个集合合一合约 |
| 批量转账 | 需多次交易 | 单次 `safeBatchTransferFrom` |
| Gas 成本 | 较高 (每个NFT独立存储) | 较低 (共享存储) |
| 适用场景 | 艺术品、PFP、收藏品 | 游戏道具、奖励凭证 |
| 半同质化 | 不支持 | 支持 (可设置 supply) |

---

## 3. IPFS 去中心化存储

### 3.1 为什么用 IPFS 存 NFT

```
问题: NFT 元数据 (图片、视频、属性) 通常太大，无法直接存链上
方案: 链上存储 IPFS CID (内容标识符)，实际文件存 IPFS

传统 HTTP 存储:
  tokenURI → "https://example.com/image.png"
  ❌ 服务器宕机 → NFT 图片丢失

IPFS 存储:
  tokenURI → "ipfs://QmXxx...yyy/image.png"
  ✅ 内容寻址 → 只要有一个节点存储就不会丢失

最佳实践:
  1. 上传文件到 IPFS
  2. 使用 IPNS 或固定服务 (Pinata, nft.storage) 保持文件可访问
  3. 链上存储 ipfs:// URI
```

### 3.2 JavaScript 上传到 IPFS

```typescript
// 使用 Pinata API 上传到 IPFS
import { PinataSDK } from "pinata-web3";
import * as fs from "fs";

const pinata = new PinataSDK({
  pinataJwtKey: process.env.PINATA_JWT!,
  pinataGateway: "example.mypinata.cloud",
});

// === 上传单个文件 ===
async function uploadFile(filePath: string): Promise<string> {
  const file = fs.createReadStream(filePath);
  const upload = await pinata.upload.file(file);
  console.log("Uploaded CID:", upload.IpfsHash);
  return upload.IpfsHash;
}

// === 上传 JSON 元数据 ===
async function uploadMetadata(
  name: string,
  description: string,
  imageCID: string,
  attributes: object[]
): Promise<string> {
  const metadata = {
    name,
    description,
    image: `ipfs://${imageCID}`,
    attributes,
  };

  const upload = await pinata.upload.json(metadata);
  console.log("Metadata CID:", upload.IpfsHash);
  return upload.IpfsHash;
}

// === 完整流程: 上传图片 + 元数据 ===
async function mintNFT(
  imagePath: string,
  name: string,
  description: string,
  attributes: object[]
) {
  // 1. 上传图片
  const imageCID = await uploadFile(imagePath);

  // 2. 上传元数据
  const metadataCID = await uploadMetadata(name, description, imageCID, attributes);

  // 3. 构造 tokenURI
  const tokenURI = `ipfs://${metadataCID}`;
  console.log("Token URI:", tokenURI);

  // 4. 铸造 NFT (调用合约)
  // const tx = await contract.mint(tokenURI);
  return tokenURI;
}

// 批量上传
async function batchUploadNFTs(items: Array<{ image: string; name: string; desc: string }>) {
  const uris: string[] = [];
  for (const item of items) {
    const uri = await mintNFT(item.image, item.name, item.desc, []);
    uris.push(uri);
  }
  console.log(`Uploaded ${uris.length} NFTs`);
  return uris;
}
```

### 3.3 Python 上传到 IPFS

```python
import requests
import json
from pathlib import Path

class IPFSUploader:
    """使用 Pinata API 上传文件到 IPFS"""
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token
        self.base_url = "https://api.pinata.cloud"

    def upload_file(self, file_path: str) -> str:
        """上传单个文件"""
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/pinning/pinFileToIPFS",
                headers=headers,
                files={"file": f}
            )
        response.raise_for_status()
        cid = response.json()["IpfsHash"]
        print(f"Uploaded {file_path} → ipfs://{cid}")
        return cid

    def upload_json(self, data: dict, name: str = "") -> str:
        """上传 JSON 元数据"""
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        payload = {"pinataContent": data, "pinataMetadata": {"name": name}}
        response = requests.post(
            f"{self.base_url}/pinning/pinJSONToIPFS",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        cid = response.json()["IpfsHash"]
        print(f"Uploaded metadata → ipfs://{cid}")
        return cid

    def create_and_upload_metadata(
        self, image_cid: str, name: str, description: str, attributes: list
    ) -> str:
        """创建完整元数据并上传"""
        metadata = {
            "name": name,
            "description": description,
            "image": f"ipfs://{image_cid}",
            "attributes": attributes
        }
        return self.upload_json(metadata, name=name)


# === 使用示例 ===
uploader = IPFSUploader(jwt_token="YOUR_JWT_TOKEN")

# 上传图片
image_cid = uploader.upload_file("artwork_001.png")

# 上传元数据
metadata_cid = uploader.create_and_upload_metadata(
    image_cid=image_cid,
    name="Cosmic Dreams #001",
    description="A generative art piece exploring cosmic themes",
    attributes=[
        {"trait_type": "Background", "value": "Deep Space"},
        {"trait_type": "Color", "value": "Purple"},
        {"trait_type": "Rarity", "value": "Rare"}
    ]
)

print(f"\nFinal Token URI: ipfs://{metadata_cid}")
```

---

## 4. 元数据规范

### 4.1 标准 NFT 元数据 JSON

```json
{
  "name": "Cosmic Dreams #001",
  "description": "A generative art piece exploring cosmic themes and the beauty of the universe.",
  "image": "ipfs://QmXxx...yyy/image.png",
  "external_url": "https://cosmicdreams.io/1",
  "animation_url": "ipfs://QmXxx...yyy/video.mp4",
  "attributes": [
    { "trait_type": "Background", "value": "Deep Space" },
    { "trait_type": "Color Palette", "value": "Purple & Gold" },
    { "trait_type": "Rarity", "value": "Rare", "display_type": "string" },
    { "trait_type": "Power", "value": 85, "display_type": "number" },
    { "trait_type": "Birthday", "value": 1672531200, "display_type": "date" },
    { "trait_type": "Boost", "value": 1.5, "display_type": "boost_number" }
  ]
}
```

### 4.2 链上元数据 (Base64 编码)

无需 IPFS，直接将元数据编码在合约中：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/// @title 链上 SVG NFT (完全链上元数据)
contract OnChainNFT {
    using Strings for uint256;

    function tokenURI(uint256 tokenId) public view returns (string memory) {
        string memory image = _generateSVG(tokenId);
        string memory json = string(
            abi.encodePacked(
                '{"name": "OnChain Art #', tokenId.toString(), '",',
                '"description": "Fully on-chain generative art",',
                '"image": "data:image/svg+xml;base64,',
                Base64.encode(bytes(image)), '"',
                '}'
            )
        );
        return string(
            abi.encodePacked(
                "data:application/json;base64,",
                Base64.encode(bytes(json))
            )
        );
    }

    function _generateSVG(uint256 tokenId) internal pure returns (string memory) {
        // 根据 tokenId 生成不同的 SVG 图像
        uint256 hue = (tokenId * 137) % 360;
        return string(
            abi.encodePacked(
                '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">',
                '<rect width="500" height="500" fill="hsl(', hue.toString(), ',70%,50%)"/>',
                '<circle cx="250" cy="250" r="100" fill="white" opacity="0.5"/>',
                '<text x="250" y="260" font-size="24" text-anchor="middle" fill="black">',
                '#', tokenId.toString(),
                '</text></svg>'
            )
        );
    }
}
```

### 4.3 动态元数据

```solidity
// 根据链上状态动态生成元数据
contract DynamicNFT {
    enum Level { Novice, Apprentice, Expert, Master }

    mapping(uint256 => Level) public tokenLevels;
    mapping(uint256 => uint256) public tokenXP;

    function tokenURI(uint256 tokenId) external view returns (string memory) {
        Level level = tokenLevels[tokenId];
        uint256 xp = tokenXP[tokenId];

        // 根据 level 返回不同的图片和属性
        string memory imageName;
        if (level == Level.Novice) imageName = "novice.svg";
        else if (level == Level.Apprentice) imageName = "apprentice.svg";
        else if (level == Level.Expert) imageName = "expert.svg";
        else imageName = "master.svg";

        // ... 构建 JSON 元数据
    }

    function addXP(uint256 tokenId, uint256 xp) external {
        tokenXP[tokenId] += xp;
        _checkLevelUp(tokenId);
    }

    function _checkLevelUp(uint256 tokenId) internal {
        uint256 xp = tokenXP[tokenId];
        if (xp >= 10000) tokenLevels[tokenId] = Level.Master;
        else if (xp >= 5000) tokenLevels[tokenId] = Level.Expert;
        else if (xp >= 1000) tokenLevels[tokenId] = Level.Apprentice;
    }
}
```

---

## 5. NFT 市场合约

### 5.1 NFT 市场核心合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title 去中心化 NFT 市场
contract NFTMarketplace is ReentrancyGuard, Ownable {
    struct Listing {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 price;
        bool active;
    }

    struct Auction {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 startPrice;
        uint256 highestBid;
        address highestBidder;
        uint256 endTime;
        bool ended;
    }

    uint256 public constant PLATFORM_FEE_BPS = 250; // 2.5%
    uint256 public constant BPS_DENOMINATOR = 10000;
    address public feeReceiver;

    // 固定价格上架列表
    mapping(uint256 => Listing) public listings;       // listingId => Listing
    mapping(address => uint256[]) public userListings; // user => listingIds

    // 拍卖列表
    mapping(uint256 => Auction) public auctions;       // auctionId => Auction

    uint256 public nextListingId = 1;
    uint256 public nextAuctionId = 1;

    event Listed(uint256 indexed listingId, address indexed seller, address nftContract, uint256 tokenId, uint256 price);
    event Sold(uint256 indexed listingId, address indexed buyer, uint256 price);
    event Cancelled(uint256 indexed listingId);
    event AuctionCreated(uint256 indexed auctionId, address indexed seller, uint256 startPrice, uint256 endTime);
    event BidPlaced(uint256 indexed auctionId, address indexed bidder, uint256 amount);
    event AuctionEnded(uint256 indexed auctionId, address winner, uint256 finalPrice);

    constructor() {
        feeReceiver = msg.sender;
    }

    // ===== 固定价格: 上架 =====
    function listNFT(address nftContract, uint256 tokenId, uint256 price) external returns (uint256) {
        require(price > 0, "Price must be > 0");

        // 将 NFT 转入市场托管
        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);

        uint256 listingId = nextListingId++;
        listings[listingId] = Listing(msg.sender, nftContract, tokenId, price, true);
        userListings[msg.sender].push(listingId);

        emit Listed(listingId, msg.sender, nftContract, tokenId, price);
        return listingId;
    }

    // ===== 固定价格: 购买 =====
    function buyNFT(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(msg.value >= listing.price, "Insufficient payment");
        require(msg.sender != listing.seller, "Cannot buy your own");

        listing.active = false;

        // 计算手续费
        uint256 fee = (listing.price * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
        uint256 sellerProceeds = listing.price - fee;

        // 转移 NFT
        IERC721(listing.nftContract).transferFrom(address(this), msg.sender, listing.tokenId);

        // 支付 (CEI 模式)
        (bool feePaid, ) = feeReceiver.call{value: fee}("");
        (bool sellerPaid, ) = listing.seller.call{value: sellerProceeds}("");
        require(feePaid && sellerPaid, "Payment failed");

        // 退还多余 ETH
        if (msg.value > listing.price) {
            (bool refunded, ) = msg.sender.call{value: msg.value - listing.price}("");
            require(refunded, "Refund failed");
        }

        emit Sold(listingId, msg.sender, listing.price);
    }

    // ===== 固定价格: 取消上架 =====
    function cancelListing(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Not active");
        require(listing.seller == msg.sender, "Not seller");

        listing.active = false;
        IERC721(listing.nftContract).transferFrom(address(this), msg.sender, listing.tokenId);

        emit Cancelled(listingId);
    }

    // ===== 拍卖: 创建 =====
    function createAuction(
        address nftContract,
        uint256 tokenId,
        uint256 startPrice,
        uint256 duration
    ) external returns (uint256) {
        require(startPrice > 0 && duration > 0, "Invalid params");

        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);

        uint256 auctionId = nextAuctionId++;
        auctions[auctionId] = Auction({
            seller: msg.sender,
            nftContract: nftContract,
            tokenId: tokenId,
            startPrice: startPrice,
            highestBid: 0,
            highestBidder: address(0),
            endTime: block.timestamp + duration,
            ended: false
        });

        emit AuctionCreated(auctionId, msg.sender, startPrice, block.timestamp + duration);
        return auctionId;
    }

    // ===== 拍卖: 出价 =====
    function placeBid(uint256 auctionId) external payable nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(!auction.ended, "Auction ended");
        require(block.timestamp < auction.endTime, "Auction expired");
        require(msg.value > auction.highestBid, "Bid too low");
        require(msg.sender != auction.seller, "Seller cannot bid");

        // 退还前一个最高出价者
        if (auction.highestBidder != address(0)) {
            (bool refunded, ) = auction.highestBidder.call{value: auction.highestBid}("");
            require(refunded, "Refund failed");
        }

        auction.highestBid = msg.value;
        auction.highestBidder = msg.sender;

        emit BidPlaced(auctionId, msg.sender, msg.value);
    }

    // ===== 拍卖: 结束 =====
    function endAuction(uint256 auctionId) external nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(!auction.ended, "Already ended");
        require(block.timestamp >= auction.endTime, "Not yet ended");

        auction.ended = true;

        if (auction.highestBidder != address(0)) {
            uint256 fee = (auction.highestBid * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
            uint256 sellerProceeds = auction.highestBid - fee;

            IERC721(auction.nftContract).transferFrom(address(this), auction.highestBidder, auction.tokenId);

            (bool feePaid, ) = feeReceiver.call{value: fee}("");
            (bool sellerPaid, ) = auction.seller.call{value: sellerProceeds}("");
            require(feePaid && sellerPaid, "Payment failed");

            emit AuctionEnded(auctionId, auction.highestBidder, auction.highestBid);
        } else {
            // 无人出价，NFT 退还卖家
            IERC721(auction.nftContract).transferFrom(address(this), auction.seller, auction.tokenId);
            emit AuctionEnded(auctionId, address(0), 0);
        }
    }
}
```

### 5.2 前端市场交互 (React + Ethers.js)

```tsx
// src/components/Marketplace.tsx
import { useState, useEffect } from "react";
import { ethers, Contract, BrowserProvider } from "ethers";

const MARKETPLACE_ABI = [
  "function listNFT(address nftContract, uint256 tokenId, uint256 price) returns (uint256)",
  "function buyNFT(uint256 listingId) payable",
  "function listings(uint256) view returns (address seller, address nftContract, uint256 tokenId, uint256 price, bool active)",
];

const MARKETPLACE_ADDRESS = "0x1234...";

export function Marketplace() {
  const [listings, setListings] = useState<any[]>([]);
  const [account, setAccount] = useState("");

  const loadListings = async () => {
    const provider = new BrowserProvider(window.ethereum);
    const contract = new Contract(MARKETPLACE_ADDRESS, MARKETPLACE_ABI, provider);

    // 从事件中获取所有上架记录
    const filter = contract.filters.Listed();
    const events = await contract.queryFilter(filter);

    const items = await Promise.all(
      events.map(async (event) => {
        const listingId = (event as any).args.listingId;
        const listing = await contract.listings(listingId);
        return {
          listingId: listingId.toString(),
          seller: listing.seller,
          nftContract: listing.nftContract,
          tokenId: listing.tokenId.toString(),
          price: ethers.formatEther(listing.price),
          active: listing.active,
        };
      })
    );

    setListings(items.filter((item) => item.active));
  };

  const buyNFT = async (listingId: string, price: string) => {
    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const contract = new Contract(MARKETPLACE_ADDRESS, MARKETPLACE_ABI, signer);

    const tx = await contract.buyNFT(listingId, {
      value: ethers.parseEther(price),
    });
    await tx.wait();
    alert("NFT purchased!");
    loadListings();
  };

  useEffect(() => {
    loadListings();
  }, []);

  return (
    <div>
      <h2>NFT Marketplace</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
        {listings.map((item) => (
          <div key={item.listingId} style={{ border: "1px solid #ccc", padding: "16px" }}>
            <h3>Token #{item.tokenId}</h3>
            <p>Price: {item.price} ETH</p>
            <p>Seller: {item.seller.slice(0, 6)}...{item.seller.slice(-4)}</p>
            <button onClick={() => buyNFT(item.listingId, item.price)}>Buy Now</button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 6. 最佳实践

### 元数据存储最佳实践

| 实践 | 说明 |
|------|------|
| **使用 IPFS** | 避免依赖中心化服务器 |
| **固定 (Pinning)** | 使用 Pinata, nft.storage, Filecoin 确保持久化 |
| **完全链上** | 高价值 NFT 考虑完全链上存储 (SVG/JSON base64) |
| **ARWEAVE** | 考虑 Arweave 作为永久存储替代方案 |
| **元数据不可变** | 铸造后锁定 `tokenURI`，防止篡改 |
| **EIP-4906** | 实现 EIP-4906 事件通知元数据更新 |

### 合约安全最佳实践

```solidity
// ✅ 1. 使用 safeMint (检查接收者是否为合约)
_safeMint(to, tokenId);

// ✅ 2. 限制每个地址的铸造数量 (防 Bot)
mapping(address => uint256) public mintCount;
require(mintCount[msg.sender] < MAX_PER_WALLET, "Limit reached");

// ✅ 3. 使用 Merkle Tree 白名单
function presaleMint(bytes32[] calldata proof, uint256 amount) external {
    bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
    require(MerkleProof.verify(proof, merkleRoot, leaf), "Not whitelisted");
    _mint(msg.sender, currentId++);
}

// ✅ 4. 渐进式揭示
// 先设置 placeholder URI，发售完成后设置 reveal URI
string public baseURI = "ipfs://HIDDEN/";
function reveal(string calldata _revealedURI) external onlyOwner {
    baseURI = _revealedURI;
}

// ✅ 5. 版税标准 ERC-2981
function royaltyInfo(uint256, uint256 salePrice) external view returns (address, uint256) {
    return (royaltyReceiver, (salePrice * 500) / 10000); // 5%
}

// ✅ 6. 紧急暂停
bool public paused;
modifier whenNotPaused() { require(!paused, "Paused"); _; }
```

### 常用工具与平台

| 工具 | 类型 | 用途 |
|------|------|------|
| [OpenZeppelin Wizard](https://wizard.openzeppelin.com/) | 合约生成 | 快速生成安全 ERC-721/1155 合约 |
| [Pinata](https://pinata.cloud/) | IPFS 固定 | 文件上传与 IPFS 固定 |
| [nft.storage](https://nft.storage/) | IPFS + Filecoin | 免费 NFT 存储 |
| [OpenSea](https://opensea.io/) | NFT 市场 | 最大 NFT 交易市场 |
| [Blur](https://blur.io/) | NFT 市场 | 聚合器 + 零手续费 |
| [Etherscan](https://etherscan.io/) | 区块浏览器 | 合约验证与交易查询 |
| [Chainlink VRF](https://docs.chain.link/vrf) | 随机数 | 公平的随机分配 |

---

## 7. 相关页面

- [[区块链基础原理]] - 区块结构、共识机制、智能合约基础
- [[以太坊开发指南]] - Solidity、Hardhat、合约部署、Gas 优化
- [[DeFi协议设计]] - AMM、借贷协议、闪电贷
- [[Layer2扩容方案]] - Layer2 扩容降低 NFT 交易成本

---

## 参考资源

- [EIP-721: Non-Fungible Token Standard](https://eips.ethereum.org/EIPS/eip-721)
- [EIP-1155: Multi Token Standard](https://eips.ethereum.org/EIPS/eip-1155)
- [EIP-2981: NFT Royalty Standard](https://eips.ethereum.org/EIPS/eip-2981)
- [OpenZeppelin ERC721](https://docs.openzeppelin.com/contracts/4.x/erc721)
- [IPFS Documentation](https://docs.ipfs.io/)
- [Pinata Documentation](https://docs.pinata.cloud/)
