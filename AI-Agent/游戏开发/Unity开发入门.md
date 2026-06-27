---
title: Unity开发入门
aliases:
  - Unity Getting Started
  - Unity Tutorial
  - Unity基础
tags:
  - unity
  - csharp
  - game-development
  - game-engine
type: wiki
status: active
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent知识库
difficulty: beginner
project: 游戏开发
---

# Unity开发入门

Unity 是全球最流行的游戏引擎之一，支持 2D 和 3D 游戏开发，可部署到 PC、移动设备、主机和 VR/AR 平台。

---

## 一、C# 基础

Unity 使用 C# 作为主要脚本语言。以下是游戏开发中常用的 C# 特性：

### 1.1 MonoBehaviour 生命周期

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    // Awake: 对象实例化时调用（最早）
    void Awake()
    {
        Debug.Log("Awake - 初始化自身引用");
    }

    // OnEnable: 对象激活时调用
    void OnEnable()
    {
        Debug.Log("OnEnable");
    }

    // Start: 第一帧 Update 之前调用
    void Start()
    {
        Debug.Log("Start - 初始化依赖其他对象的逻辑");
    }

    // FixedUpdate: 固定时间间隔调用（默认0.02s），用于物理计算
    void FixedUpdate()
    {
        // 物理移动、力的施加
    }

    // Update: 每帧调用一次
    void Update()
    {
        // 输入检测、游戏逻辑
    }

    // LateUpdate: 所有 Update 之后调用
    void LateUpdate()
    {
        // 相机跟随、后处理
    }

    // OnDisable: 对象禁用时调用
    void OnDisable()
    {
        Debug.Log("OnDisable");
    }

    // OnDestroy: 对象销毁时调用
    void OnDestroy()
    {
        Debug.Log("OnDestroy");
    }
}
```

### 1.2 协程（Coroutine）

```csharp
using UnityEngine;
using System.Collections;

public class SkillCooldown : MonoBehaviour
{
    [SerializeField] private float cooldownDuration = 3f;
    private bool isReady = true;

    public void UseSkill()
    {
        if (!isReady) return;

        Debug.Log("技能释放！");
        StartCoroutine(CooldownRoutine());
    }

    private IEnumerator CooldownRoutine()
    {
        isReady = false;
        Debug.Log($"冷却中... {cooldownDuration}秒");

        yield return new WaitForSeconds(cooldownDuration);

        isReady = true;
        Debug.Log("技能就绪！");
    }
}
```

### 1.3 泛型与 ScriptableObject

```csharp
using UnityEngine;

// ScriptableObject: 数据容器，不依赖场景对象
[CreateAssetMenu(fileName = "NewItem", menuName = "Game/Item Data")]
public class ItemData : ScriptableObject
{
    public string itemName;
    public Sprite icon;
    public int maxStack = 99;
    [TextArea] public string description;
}
```

---

## 二、场景管理

### 2.1 场景加载与切换

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneLoader : MonoBehaviour
{
    // 同步加载
    public void LoadScene(string sceneName)
    {
        SceneManager.LoadScene(sceneName);
    }

    // 异步加载（带进度）
    public void LoadSceneAsync(string sceneName)
    {
        StartCoroutine(LoadSceneAsyncRoutine(sceneName));
    }

    private System.Collections.IEnumerator LoadSceneAsyncRoutine(string sceneName)
    {
        AsyncOperation operation = SceneManager.LoadSceneAsync(sceneName);
        operation.allowSceneActivation = false;

        while (!operation.isDone)
        {
            float progress = Mathf.Clamp01(operation.progress / 0.9f);
            Debug.Log($"加载进度: {progress * 100}%");

            if (operation.progress >= 0.9f)
            {
                operation.allowSceneActivation = true;
            }

            yield return null;
        }
    }

    // 叠加场景（Additive）
    public void AddScene(string sceneName)
    {
        SceneManager.LoadScene(sceneName, LoadSceneMode.Additive);
    }
}
```

### 2.2 DontDestroyOnLoad 跨场景持久对象

```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```

---

## 三、物理系统

### 3.1 Rigidbody 移动与碰撞

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class PlayerMovement : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 8f;

    private Rigidbody rb;
    private bool isGrounded;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        rb.freezeRotation = true; // 防止物理旋转
    }

    void FixedUpdate()
    {
        float h = Input.GetAxisRaw("Horizontal");
        float v = Input.GetAxisRaw("Vertical");

        Vector3 direction = new Vector3(h, 0, v).normalized;
        rb.MovePosition(rb.position + direction * moveSpeed * Time.fixedDeltaTime);

        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            isGrounded = false;
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
    }
}
```

### 3.2 射线检测（Raycast）

```csharp
using UnityEngine;

public class Weapon : MonoBehaviour
{
    [SerializeField] private float range = 100f;
    [SerializeField] private int damage = 25;
    [SerializeField] private LayerMask hitLayers;

    public void Shoot()
    {
        Ray ray = new Ray(transform.position, transform.forward);

        if (Physics.Raycast(ray, out RaycastHit hit, range, hitLayers))
        {
            Debug.Log($"命中: {hit.collider.name}, 距离: {hit.distance}");

            IDamageable target = hit.collider.GetComponent<IDamageable>();
            target?.TakeDamage(damage);

            // 可视化调试
            Debug.DrawRay(ray.origin, ray.direction * range, Color.red, 1f);
        }
    }
}

public interface IDamageable
{
    void TakeDamage(int amount);
}
```

### 3.3 触发器（Trigger）

```csharp
using UnityEngine;

public class PickupItem : MonoBehaviour
{
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            Debug.Log("拾取物品！");
            // 播放音效、更新UI
            Destroy(gameObject);
        }
    }
}
```

---

## 四、UI系统（UGUI）

### 4.1 基础 HUD

```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class HealthUI : MonoBehaviour
{
    [SerializeField] private Slider healthBar;
    [SerializeField] private TextMeshProUGUI healthText;
    [SerializeField] private Image damageFlash;

    public void UpdateHealth(int current, int max)
    {
        healthBar.maxValue = max;
        healthBar.value = current;
        healthText.text = $"{current}/{max}";

        // 低血量闪烁
        if (current < max * 0.3f)
        {
            damageFlash.color = new Color(1, 0, 0, 0.3f);
        }
        else
        {
            damageFlash.color = Color.clear;
        }
    }
}
```

### 4.2 动态列表（ScrollView + 对象池复用）

```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class InventoryUI : MonoBehaviour
{
    [SerializeField] private Transform contentParent;
    [SerializeField] private GameObject slotPrefab;

    private List<GameObject> slots = new List<GameObject>();

    public void RefreshInventory(List<ItemData> items)
    {
        // 回收已有
        foreach (var slot in slots)
            slot.SetActive(false);

        for (int i = 0; i < items.Count; i++)
        {
            GameObject slot;
            if (i < slots.Count)
            {
                slot = slots[i];
                slot.SetActive(true);
            }
            else
            {
                slot = Instantiate(slotPrefab, contentParent);
                slots.Add(slot);
            }

            // 更新槽位显示
            slot.GetComponentInChildren<Image>().sprite = items[i].icon;
            slot.GetComponentInChildren<TextMeshProUGUI>().text = items[i].itemName;
        }
    }
}
```

---

## 五、最佳实践

| 实践 | 说明 |
|------|------|
| **使用 `[SerializeField]` 代替 public 字段** | 在 Inspector 中暴露但不破坏封装 |
| **缓存组件引用** | `Awake()` 中 `GetComponent`，避免每帧调用 |
| **使用 ScriptableObject 管理配置** | 数据与逻辑分离，便于策划调整 |
| **善用 LayerMask 过滤物理检测** | 减少不必要的碰撞计算 |
| **场景用 Additive 加载** | 大型项目拆分场景，按需加载 |
| **避免 `Find` / `FindObjectOfType`** | 性能差，改用依赖注入或单例 |
| **使用 Addressables 管理资源** | 替代 Resources.Load，支持热更新 |
| **协程替代 Invoke** | 协程可控、可追踪，Invoke 不可靠 |

---

## 六、相关页面

- [[Unreal Engine基础]] - 对比学习另一主流引擎
- [[游戏设计模式]] - Unity 中常用的设计模式实现
- [[游戏性能优化]] - Unity 性能分析与优化技巧
- [[游戏网络同步]] - Unity 多人游戏网络方案（Netcode for GameObjects）
