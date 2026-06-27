---
title: NFT开发指南
aliases:
  - NFT Development Guide
  - ERC-721
  - ERC-1155
  - 非同质化代币
tags:
  - blockchain
  - nft
  - erc721
  - erc1155
  - ipfs
  - metadata
  - web3
  - solidity
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: 原创
difficulty: intermediate
project: AI-Agent
---

# NFT 开发指南

## 概述

NFT（Non-Fungible Token，非同质化代币）是代表唯一数字资产所有权的加密代币。本指南涵盖 ERC-721 和 ERC-1155 标准、IPFS 存储方案、Metadata 结构设计以及完整的 NFT 项目开发流程。

---

## 一、ERC-721 标准

### 1.1 基本 ERC-721 实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyNFT is ERC721URIStorage, ERC721Burnable, ERC721Pausable, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public mintPrice = 0.05 ether;
    uint256 public maxPerWallet = 5;
    uint256 public maxPerTx = 2;

    mapping(address => uint256) public mintedPerWallet;

    event NFTMinted(address indexed minter, uint256 indexed tokenId, string tokenURI);

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    // 普通铸造
    function mint(string calldata _tokenURI) external payable whenNotPaused {
        uint256 currentId = _tokenIdCounter.current();

        require(currentId < MAX_SUPPLY, "Max supply reached");
        require(msg.value >= mintPrice, "Insufficient payment");
        require(mintedPerWallet[msg.sender] < maxPerWallet, "Wallet limit reached");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, _tokenURI);

        mintedPerWallet[msg.sender]++;

        emit NFTMinted(msg.sender, tokenId, _tokenURI);
    }

    // 批量铸造
    function batchMint(string[] calldata _tokenURIs) external payable whenNotPaused {
        uint256 quantity = _tokenURIs.length;
        require(quantity > 0 && quantity <= maxPerTx, "Invalid quantity");
        require(msg.value >= mintPrice * quantity, "Insufficient payment");
        require(mintedPerWallet[msg.sender] + quantity <= maxPerWallet, "Wallet limit reached");

        for (uint256 i = 0; i < quantity; i++) {
            uint256 tokenId = _tokenIdCounter.current();
            _tokenIdCounter.increment();

            _safeMint(msg.sender, tokenId);
            _setTokenURI(tokenId, _tokenURIs[i]);
        }

        mintedPerWallet[msg.sender] += quantity;
    }

    // Owner 铸造（免费）
    function ownerMint(address _to, string calldata _tokenURI) external onlyOwner {
        uint256 tokenId = _tokenIdCounter.current();
        require(tokenId < MAX_SUPPLY, "Max supply reached");

        _tokenIdCounter.increment();
        _safeMint(_to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
    }

    // 提取资金
    function withdraw() external onlyOwner {
        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Withdraw failed");
    }

    // 设置参数
    function setMintPrice(uint256 _price) external onlyOwner {
        mintPrice = _price;
    }

    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    // 覆盖必要函数
    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Pausable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
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
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
}
```

### 1.2 链上 Metadata（完全链上 NFT）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract OnChainNFT is ERC721, Ownable {
    using Strings for uint256;

    uint256 public constant MAX_SUPPLY = 1000;
    uint256 public mintPrice = 0.01 ether;

    struct NFTAttributes {
        uint256 strength;
        uint256 agility;
        uint256 intelligence;
        uint256 luck;
        string name;
        string imageURI;
    }

    mapping(uint256 => NFTAttributes) public nftAttributes;
    uint256 public totalMinted;

    constructor() ERC721("OnChainNFT", "OCN") Ownable(msg.sender) {}

    // 随机生成属性
    function _generateAttributes(uint256 _tokenId) internal pure returns (NFTAttributes memory) {
        uint256 seed = uint256(keccak256(abi.encodePacked(_tokenId, block.prevrandao)));
        return NFTAttributes({
            strength: (seed % 100) + 1,
            agility: ((seed >> 8) % 100) + 1,
            intelligence: ((seed >> 16) % 100) + 1,
            luck: ((seed >> 24) % 100) + 1,
            name: string(abi.encodePacked("Hero #", _tokenId.toString())),
            imageURI: ""
        });
    }

    function mint() external payable {
        require(totalMinted < MAX_SUPPLY, "Max supply reached");
        require(msg.value >= mintPrice, "Insufficient payment");

        uint256 tokenId = totalMinted + 1;
        nftAttributes[tokenId] = _generateAttributes(tokenId);
        _safeMint(msg.sender, tokenId);
        totalMinted++;
    }

    // 完全链上生成的 Metadata JSON
    function tokenURI(uint256 _tokenId) public view override returns (string memory) {
        require(_ownerOf(_tokenId) != address(0), "Token does not exist");

        NFTAttributes memory attr = nftAttributes[_tokenId];

        // 生成 SVG 图像
        string memory svg = _generateSVG(attr, _tokenId);

        // 编码为 Base64 Data URI
        string memory json = string(abi.encodePacked(
            '{"name": "', attr.name, '",',
            '"description": "Fully on-chain generative NFT",',
            '"image": "data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '",',
            '"attributes": [',
                '{"trait_type": "Strength", "value": ', attr.strength.toString(), '},',
                '{"trait_type": "Agility", "value": ', attr.agility.toString(), '},',
                '{"trait_type": "Intelligence", "value": ', attr.intelligence.toString(), '},',
                '{"trait_type": "Luck", "value": ', attr.luck.toString(), '}',
            ']}'
        ));

        return string(abi.encodePacked(
            "data:application/json;base64,",
            Base64.encode(bytes(json))
        ));
    }

    // 动态生成 SVG
    function _generateSVG(NFTAttributes memory _attr, uint256 _tokenId) internal pure returns (string memory) {
        return string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">',
            '<rect width="500" height="500" fill="#1a1a2e"/>',
            '<text x="250" y="80" font-size="32" fill="#e94560" text-anchor="middle" font-family="monospace">Hero #', _tokenId.toString(), '</text>',
            '<rect x="50" y="120" width="', _barWidth(_attr.strength), '" height="30" fill="#e94560"/>',
            '<text x="20" y="145" fill="#fff" font-size="20" font-family="monospace">STR</text>',
            '<rect x="50" y="170" width="', _barWidth(_attr.agility), '" height="30" fill="#0f3460"/>',
            '<text x="20" y="195" fill="#fff" font-size="20" font-family="monospace">AGI</text>',
            '<rect x="50" y="220" width="', _barWidth(_attr.intelligence), '" height="30" fill="#16213e"/>',
            '<text x="20" y="245" fill="#fff" font-size="20" font-family="monospace">INT</text>',
            '<rect x="50" y="270" width="', _barWidth(_attr.luck), '" height="30" fill="#533483"/>',
            '<text x="20" y="295" fill="#fff" font-size="20" font-family="monospace">LUK</text>',
            '</svg>'
        ));
    }

    function _barWidth(uint256 _value) internal pure returns (string memory) {
        uint256 width = (_value * 4); // max 400px
        return width.toString();
    }
}
```

### 1.3 Merkle Tree 白名单铸造

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract WhitelistNFT is ERC721 {
    bytes32 public merkleRoot;
    uint256 public mintPrice;
    uint256 public whitelistPrice;
    uint256 private _nextTokenId;

    mapping(address => bool) public hasMinted;

    constructor(
        bytes32 _merkleRoot,
        uint256 _mintPrice,
        uint256 _whitelistPrice
    ) ERC721("WhitelistNFT", "WLNFT") {
        merkleRoot = _merkleRoot;
        mintPrice = _mintPrice;
        whitelistPrice = _whitelistPrice;
    }

    function whitelistMint(bytes32[] calldata _proof) external payable {
        require(!hasMinted[msg.sender], "Already minted");

        // 验证 Merkle Proof
        bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(msg.sender))));
        require(MerkleProof.verify(_proof, merkleRoot, leaf), "Not whitelisted");

        require(msg.value >= whitelistPrice, "Insufficient payment");

        hasMinted[msg.sender] = true;
        uint256 tokenId = _nextTokenId++;
        _safeMint(msg.sender, tokenId);
    }

    function publicMint() external payable {
        require(msg.value >= mintPrice, "Insufficient payment");
        uint256 tokenId = _nextTokenId++;
        _safeMint(msg.sender, tokenId);
    }
}
```

```javascript
// 生成 Merkle Tree 白名单 (JavaScript)
const { MerkleTree } = require("merkletreejs");
const { keccak256 } = require("ethers");

// 白名单地址列表
const whitelistAddresses = [
    "0x1234...abcd",
    "0x5678...efgh",
    // ...
];

// 生成叶子节点
const leaves = whitelistAddresses.map((addr) =>
    keccak256(Buffer.from(addr.slice(2), "hex"))
);

// 构建 Merkle Tree
const merkleTree = new MerkleTree(leaves, keccak256, { sortPairs: true });
const merkleRoot = merkleTree.getHexRoot();

console.log("Merkle Root:", merkleRoot);

// 为某个地址生成 proof
const address = "0x1234...abcd";
const leaf = keccak256(Buffer.from(address.slice(2), "hex"));
const proof = merkleTree.getHexProof(leaf);

console.log("Proof:", proof);
```

---

## 二、ERC-1155 多代币标准

### 2.1 基本 ERC-1155 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract GameItems is ERC1155, ERC1155Burnable, ERC1155Supply, Ownable {
    using Strings for uint256;

    // Token IDs
    uint256 public constant GOLD = 0;
    uint256 public constant SWORD = 1;
    uint256 public constant SHIELD = 2;
    uint256 public constant HEALTH_POTION = 3;
    uint256 public constant RARE_CHEST = 4;
    uint256 public constant LEGENDARY_KEY = 5;

    // 价格
    mapping(uint256 => uint256) public itemPrices;

    constructor() ERC1155("https://game-api.example.com/api/item/{id}.json") Ownable(msg.sender) {
        // 初始价格设置
        itemPrices[GOLD] = 0.001 ether;
        itemPrices[SWORD] = 0.05 ether;
        itemPrices[SHIELD] = 0.04 ether;
        itemPrices[HEALTH_POTION] = 0.005 ether;
        itemPrices[RARE_CHEST] = 0.1 ether;
        itemPrices[LEGENDARY_KEY] = 0.5 ether;

        // 铸造初始供应量
        _mint(msg.sender, GOLD, 1_000_000 ether, "");
        _mint(msg.sender, SWORD, 1000, "");
        _mint(msg.sender, SHIELD, 1000, "");
        _mint(msg.sender, HEALTH_POTION, 5000, "");
        _mint(msg.sender, RARE_CHEST, 100, "");
        _mint(msg.sender, LEGENDARY_KEY, 10, "");
    }

    // 购买道具
    function buyItem(uint256 _id, uint256 _amount) external payable {
        require(itemPrices[_id] > 0, "Item not for sale");
        uint256 totalPrice = itemPrices[_id] * _amount;
        require(msg.value >= totalPrice, "Insufficient payment");

        _mint(msg.sender, _id, _amount, "");
    }

    // 批量购买
    function buyItems(uint256[] calldata _ids, uint256[] calldata _amounts) external payable {
        require(_ids.length == _amounts.length, "Length mismatch");

        uint256 totalPrice = 0;
        for (uint256 i = 0; i < _ids.length; i++) {
            require(itemPrices[_ids[i]] > 0, "Item not for sale");
            totalPrice += itemPrices[_ids[i]] * _amounts[i];
        }
        require(msg.value >= totalPrice, "Insufficient payment");

        _mintBatch(msg.sender, _ids, _amounts, "");
    }

    // Owner 铸造
    function mint(address _to, uint256 _id, uint256 _amount, bytes memory _data) external onlyOwner {
        _mint(_to, _id, _amount, _data);
    }

    function mintBatch(
        address _to,
        uint256[] memory _ids,
        uint256[] memory _amounts,
        bytes memory _data
    ) external onlyOwner {
        _mintBatch(_to, _ids, _amounts, _data);
    }

    // 设置 URI
    function setURI(string memory _newURI) external onlyOwner {
        _setURI(_newURI);
    }

    // 单个 token URI
    function uri(uint256 _tokenId) public view override returns (string memory) {
        return string(abi.encodePacked(super.uri(_tokenId)));
    }

    // 提取资金
    function withdraw() external onlyOwner {
        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Withdraw failed");
    }

    // 覆盖必要函数
    function _update(address from, address to, uint256[] memory ids, uint256[] memory values)
        internal
        override(ERC1155, ERC1155Supply)
    {
        super._update(from, to, ids, values);
    }
}
```

---

## 三、IPFS 存储

### 3.1 使用 Pinata 上传

```javascript
// 使用 Pinata 上传 NFT 资源到 IPFS
const axios = require("axios");
const fs = require("fs");
const FormData = require("form-data");

const PINATA_API_KEY = "your_pinata_api_key";
const PINATA_SECRET = "your_pinata_secret";

// 上传单个文件
async function uploadToIPFS(filePath) {
    const formData = new FormData();
    formData.append("file", fs.createReadStream(filePath));

    const response = await axios.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        formData,
        {
            headers: {
                ...formData.getHeaders(),
                pinata_api_key: PINATA_API_KEY,
                pinata_secret_api_key: PINATA_SECRET,
            },
        }
    );

    return `ipfs://${response.data.IpfsHash}`;
}

// 上传文件夹（批量）
async function uploadFolderToIPFS(folderPath) {
    const formData = new FormData();

    // 读取文件夹中所有文件
    const files = fs.readdirSync(folderPath);
    for (const file of files) {
        const filePath = `${folderPath}/${file}`;
        formData.append("file", fs.createReadStream(filePath), {
            filepath: `images/${file}`,
        });
    }

    const response = await axios.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        formData,
        {
            maxBodyLength: Infinity,
            headers: {
                ...formData.getHeaders(),
                pinata_api_key: PINATA_API_KEY,
                pinata_secret_api_key: PINATA_SECRET,
            },
        }
    );

    const folderHash = response.data.IpfsHash;
    return `ipfs://${folderHash}`;
}

// 上传 Metadata JSON
async function uploadMetadata(metadata) {
    const response = await axios.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        metadata,
        {
            headers: {
                pinata_api_key: PINATA_API_KEY,
                pinata_secret_api_key: PINATA_SECRET,
            },
        }
    );

    return `ipfs://${response.data.IpfsHash}`;
}

module.exports = { uploadToIPFS, uploadFolderToIPFS, uploadMetadata };
```

### 3.2 批量生成 Metadata

```javascript
// 批量生成 NFT Metadata 并上传到 IPFS
const { uploadMetadata } = require("./ipfs");
const fs = require("fs");

// 生成 Metadata JSON
function generateMetadata(tokenId, imageCID, attributes) {
    return {
        name: `CollectionName #${tokenId}`,
        description: "A unique digital collectible",
        image: `ipfs://${imageCID}/${tokenId}.png`,
        external_url: `https://myproject.com/${tokenId}`,
        attributes: [
            { trait_type: "Background", value: attributes.background },
            { trait_type: "Body", value: attributes.body },
            { trait_type: "Eyes", value: attributes.eyes },
            { trait_type: "Mouth", value: attributes.mouth },
            { trait_type: "Rarity", value: attributes.rarity },
            {
                display_type: "number",
                trait_type: "Generation",
                value: 1,
            },
            {
                display_type: "date",
                trait_type: "Birthday",
                value: Math.floor(Date.now() / 1000),
            },
        ],
    };
}

// 批量生成并上传
async function generateAndUploadAll(totalSupply, imageFolderCID) {
    const metadataArray = [];

    for (let i = 1; i <= totalSupply; i++) {
        // 从预生成文件中加载属性
        const attributes = JSON.parse(
            fs.readFileSync(`./metadata/raw/${i}.json`, "utf-8")
        );

        const metadata = generateMetadata(i, imageFolderCID, attributes);
        const uri = await uploadMetadata(metadata);

        metadataArray.push({ tokenId: i, uri });

        console.log(`Token ${i}/${totalSupply} uploaded: ${uri}`);
    }

    // 保存 URI 映射
    fs.writeFileSync(
        "./metadata/uri_mapping.json",
        JSON.stringify(metadataArray, null, 2)
    );

    return metadataArray;
}

// 通过 Pinata 的 CID 替换 URI
function getHTTPGateway(cid) {
    return `https://gateway.pinata.cloud/ipfs/${cid}`;
}
```

### 3.3 使用 nft.storage（免费）

```javascript
// 使用 nft.storage（免费，基于 Filecoin）
const { NFTStorage, File } = require("nft.storage");

const client = new NFTStorage({ token: "YOUR_NFT_STORAGE_KEY" });

async function storeNFT(imagePath, name, description, attributes) {
    // 读取图片文件
    const imageFile = await fs.promises.readFile(imagePath);

    // 存储到 IPFS
    const metadata = await client.store({
        name,
        description,
        image: new File([imageFile], "image.png", { type: "image/png" }),
        attributes,
    });

    console.log("IPFS URL:", metadata.url);
    return metadata.url; // ipfs://CID/metadata.json
}
```

---

## 四、Metadata 标准结构

### 4.1 标准 JSON Schema

```json
{
    "name": "Token Name #1",
    "description": "A description of the token.",
    "image": "ipfs://QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/image.png",
    "external_url": "https://example.com/token/1",
    "animation_url": "ipfs://QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/animation.mp4",
    "background_color": "ffffff",
    "youtube_url": "https://youtube.com/watch?v=...",
    "attributes": [
        {
            "trait_type": "Eyes",
            "value": "Blue"
        },
        {
            "trait_type": "Hat",
            "value": "Cap"
        },
        {
            "display_type": "number",
            "trait_type": "Level",
            "value": 5
        },
        {
            "display_type": "boost_number",
            "trait_type": "Power",
            "value": 30
        },
        {
            "display_type": "boost_percentage",
            "trait_type": "Speed Boost",
            "value": 10
        },
        {
            "display_type": "date",
            "trait_type": "Mint Date",
            "value": 1700000000
        },
        {
            "trait_type": "Rarity",
            "value": "Legendary",
            "max_value": "Legendary"
        }
    ]
}
```

### 4.2 动态 Metadata

```javascript
// 动态 Metadata API（根据时间或条件变化）
const express = require("express");
const app = express();

app.get("/api/token/:id", async (req, res) => {
    const tokenId = parseInt(req.params.id);
    const currentTime = Date.now();

    // 根据 NFT 状态返回不同 Metadata
    const nftState = await getNFTState(tokenId);

    let image, attributes;

    if (nftState.isStaking) {
        image = `${BASE_URL}/images/staking/${tokenId}.png`;
        attributes = [...nftState.baseAttributes, { trait_type: "Status", value: "Staking" }];
    } else if (nftState.level >= 10) {
        image = `${BASE_URL}/images/evolved/${tokenId}.png`;
        attributes = [...nftState.baseAttributes, { trait_type: "Evolution", value: "Stage 2" }];
    } else {
        image = `${BASE_URL}/images/base/${tokenId}.png`;
        attributes = nftState.baseAttributes;
    }

    res.json({
        name: `DynamicNFT #${tokenId}`,
        description: "A dynamic NFT that evolves over time",
        image,
        attributes,
    });
});
```

---

## 五、ERC-2981 版税标准

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RoyaltyNFT is ERC721, ERC2981, Ownable {
    uint256 private _nextTokenId;

    constructor(
        uint96 royaltyFeeNumerator, // 如 500 = 5%
        address royaltyReceiver
    ) ERC721("RoyaltyNFT", "RNFT") Ownable(msg.sender) {
        _setDefaultRoyalty(royaltyReceiver, royaltyFeeNumerator);
    }

    function mint() external {
        uint256 tokenId = _nextTokenId++;
        _safeMint(msg.sender, tokenId);
    }

    // 特定 token 的版税可以不同
    function setTokenRoyalty(uint256 tokenId, address receiver, uint96 feeNumerator) external onlyOwner {
        _setTokenRoyalty(tokenId, receiver, feeNumerator);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

---

## 六、最佳实践

### 6.1 开发流程清单

| 阶段 | 任务 |
|------|------|
| **设计** | 确定供应量、铸造机制、Metadata 结构、版税 |
| **开发** | 合约编写、单元测试、Gas 优化 |
| **资产** | 生成图片/视频、上传到 IPFS、生成 Metadata JSON |
| **测试** | 测试网部署、端到端测试、OpenSea 验证 |
| **安全** | 代码审计、模拟攻击、多签部署 |
| **部署** | 主网部署、 etherscan 验证、合约交互验证 |
| **运营** | 社区公告、白名单分配、铸造监控 |

### 6.2 安全注意事项

```solidity
pragma solidity ^0.8.20;

// ✅ 使用 _safeMint 而非 _mint
// _safeMint 会检查接收方是否实现了 IERC721Receiver 接口
// 防止代币被锁在无法处理 NFT 的合约中

// ✅ 实现接收接口（接收方合约）
contract NFTReceiver is IERC721Receiver {
    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external override returns (bytes4) {
        // 处理收到的 NFT
        return this.onERC721Received.selector;
    }
}

// ✅ 防止批量铸造时 gas 耗尽
contract SafeBatchMint {
    uint256 public constant MAX_BATCH = 20;

    function batchMint(address to, uint256 count) external {
        require(count <= MAX_BATCH, "Too many in one tx");
        for (uint256 i = 0; i < count; i++) {
            _safeMint(to, _nextId++);
        }
    }
}

// ❌ 避免：使用区块时间作为随机数（可被矿工操纵）
// function getRandom() internal returns (uint256) {
//     return uint256(keccak256(abi.encodePacked(block.timestamp))); // 不安全!
// }

// ✅ 使用 Chainlink VRF 或 commit-reveal
```

### 6.3 Gas 优化技巧

```solidity
pragma solidity ^0.8.20;

contract GasOptimizedNFT {
    // ✅ 使用 ERC721A 风格的批量铸造优化
    // 每个代币单独 _mint 需要一次 SSTORE
    // ERC721A 批量铸造 N 个只需要一次 SSTORE

    // 地址到 token 索引的映射（而非 token 到 owner 的映射）
    mapping(address => uint256) private _ownershipData;

    // 当批量铸造时，只记录起始 token 的 owner
    struct TokenOwnership {
        address addr;
        uint64 startTimestamp;
        bool burned;
    }

    mapping(uint256 => TokenOwnership) private _ownerships;

    function _mintBatch(address to, uint256 quantity) internal {
        uint256 startTokenId = _currentIndex;
        _currentIndex += quantity;

        // 只为第一个 token 写入 ownership
        _ownerships[startTokenId] = TokenOwnership({
            addr: to,
            startTimestamp: uint64(block.timestamp),
            burned: false
        });
    }

    uint256 private _currentIndex;

    // 查找 owner 时需要回溯
    function _ownershipOf(uint256 tokenId) internal view returns (TokenOwnership memory) {
        uint256 curr = tokenId;
        unchecked {
            do {
                TokenOwnership memory ownership = _ownerships[curr];
                if (!ownership.burned) {
                    return ownership;
                }
                curr--;
            } while (curr > 0);
        }
        revert("Owner not found");
    }
}
```

---

## 七、NFT 市场交互

### 7.1 通过 ethers.js 与 NFT 交互

```javascript
const { ethers } = require("ethers");

// NFT 合约 ABI
const nftAbi = [
    "function mint() payable",
    "function tokenURI(uint256 tokenId) view returns (string)",
    "function ownerOf(uint256 tokenId) view returns (address)",
    "function balanceOf(address owner) view returns (uint256)",
    "function totalSupply() view returns (uint256)",
    "event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)",
];

// 连接合约
const provider = new ethers.JsonRpcProvider("https://mainnet.infura.io/v3/YOUR_KEY");
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
const nftContract = new ethers.Contract(nftAddress, nftAbi, wallet);

// 铸造 NFT
async function mintNFT() {
    const price = await nftContract.mintPrice();
    const tx = await nftContract.mint({ value: price });
    console.log("TX Hash:", tx.hash);

    const receipt = await tx.wait();
    console.log("Minted in block:", receipt.blockNumber);

    // 从事件中获取 tokenId
    const event = receipt.logs.find(log => nftContract.interface.parseLog(log)?.name === "Transfer");
    const parsedLog = nftContract.interface.parseLog(event);
    const tokenId = parsedLog.args.tokenId;
    console.log("Token ID:", tokenId.toString());

    return tokenId;
}

// 获取 Metadata
async function getMetadata(tokenId) {
    const uri = await nftContract.tokenURI(tokenId);
    // 如果是 IPFS URI，替换为 HTTP 网关
    const httpUrl = uri.replace("ipfs://", "https://ipfs.io/ipfs/");
    const response = await fetch(httpUrl);
    return response.json();
}

// 监听铸造事件
async function listenToMints() {
    nftContract.on("Transfer", (from, to, tokenId, event) => {
        console.log(`Minted: Token #${tokenId} to ${to}`);
    });
}
```

### 7.2 Seaport（OpenSea 协议）交互

```javascript
// 使用 Seaport 进行 NFT 交易
const { ethers } = require("ethers");

const seaportAbi = [
    "function fulfillOrder((...)) payable",
    "function cancel((address,uint256)[] offers)",
];

// 创建挂单
async function createListing(tokenId, price) {
    const order = {
        offer: [{
            itemType: 2, // ERC721
            token: nftAddress,
            identifierOrCriteria: tokenId,
            startAmount: 1,
            endAmount: 1,
        }],
        consideration: [{
            itemType: 0, // Native ETH
            token: ethers.ZeroAddress,
            identifierOrCriteria: 0,
            startAmount: price,
            endAmount: price,
            recipient: sellerAddress,
        }],
        startTime: Math.floor(Date.now() / 1000),
        endTime: Math.floor(Date.now() / 1000) + 7 * 24 * 3600, // 7 天
        zone: ethers.ZeroAddress,
        zoneHash: ethers.ZeroHash,
        salt: ethers.randomBytes(32),
        conduitKey: ethers.ZeroHash,
        totalOriginalConsiderationItems: 1,
    };

    // 签名订单
    const signature = await wallet._signTypedData(domainData, types, order);
    return { parameters: order, signature };
}
```

---

## 相关页面

- [[智能合约开发]] - Solidity 基础与开发框架
- [[DeFi协议指南]] - NFT-Fi 与衍生协议
- [[Web3后端开发]] - NFT 索引与 API 服务
- [[Layer2与扩容方案]] - L2 NFT 生态
