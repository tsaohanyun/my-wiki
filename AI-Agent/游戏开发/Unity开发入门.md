---
title: Unity 开发入门
date: 2026-06-28
category: 游戏开发
tags:
  - Unity
  - 游戏引擎
  - C#
  - 入门
author: AI-Agent
description: Unity 引擎核心概念详解，涵盖 GameObject、Component、Scene、脚本编写、物理引擎与 UI 系统，附完整代码示例。
---

# Unity 开发入门

> Unity 是全球使用最广泛的跨平台游戏引擎之一，支持 2D/3D、AR/VR 以及各类交互式内容的开发。本文系统介绍 Unity 的核心概念与开发实践。

---

## 目录

1. [GameObject（游戏对象）](#1-gameobject游戏对象)
2. [Component（组件）](#2-component组件)
3. [Scene（场景）](#3-scene场景)
4. [脚本编程](#4-脚本编程)
5. [物理引擎](#5-物理引擎)
6. [UI 系统](#6-ui-系统)
7. [最佳实践](#7-最佳实践)
8. [相关页面](#8-相关页面)

---

## 1. GameObject（游戏对象）

GameObject 是 Unity 场景中所有实体的基础。每个 GameObject 本身不做任何事情，它的行为由挂载的 Component 决定。

### 1.1 核心属性

| 属性 | 说明 |
|------|------|
| `name` | 对象名称 |
| `transform` | 位置、旋转、缩放 |
| `activeSelf` | 对象自身是否激活 |
| `activeInHierarchy` | 在层级中是否激活 |
| `tag` | 对象标签 |
| `layer` | 对象层 |

### 1.2 创建与管理 GameObject

```csharp
using UnityEngine;

public class GameObjectDemo : MonoBehaviour
{
    void Start()
    {
        // 创建空 GameObject
        GameObject emptyGo = new GameObject("MyEmptyObject");

        // 创建带组件的 GameObject
        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = "PlayerCube";
        cube.transform.position = new Vector3(0, 1, 0);

        // 通过名称查找对象（性能较低，不建议在 Update 中使用）
        GameObject found = GameObject.Find("PlayerCube");

        // 通过标签查找
        GameObject tagged = GameObject.FindGameObjectWithTag("Player");

        // 查找所有标签对象
        GameObject[] enemies = GameObject.FindGameObjectsWithTag("Enemy");

        // 销毁对象
        Destroy(cube, 2f); // 延迟 2 秒销毁
    }
}
```

### 1.3 父子层级

```csharp
// 设置父子关系
childTransform.SetParent(parentTransform);

// 解除父子关系
childTransform.SetParent(null);

// 获取所有子对象
foreach (Transform child in parentTransform)
{
    Debug.Log(child.name);
}
```

---

## 2. Component（组件）

Component 是赋予 GameObject 功能的模块。每个组件负责一类特定行为（渲染、物理、音频等）。

### 2.1 常用组件一览

| 组件 | 功能 |
|------|------|
| `Transform` | 位置/旋转/缩放（每个 GameObject 必备） |
| `MeshRenderer` | 渲染网格 |
| `MeshFilter` | 存储网格数据 |
| `Rigidbody` | 物理模拟 |
| `Collider` | 碰撞检测 |
| `Camera` | 摄像机 |
| `Light` | 灯光 |
| `AudioSource` | 音频播放 |
| `Animator` | 动画控制 |

### 2.2 获取与添加组件

```csharp
using UnityEngine;

public class ComponentDemo : MonoBehaviour
{
    void Start()
    {
        // 获取组件
        Rigidbody rb = GetComponent<Rigidbody>();
        Renderer renderer = GetComponent<Renderer>();

        // 获取子对象上的组件
        Collider childCollider = GetComponentInChildren<Collider>();

        // 获取父对象上的组件
        Canvas parentCanvas = GetComponentInParent<Canvas>();

        // 添加组件（运行时）
        if (rb == null)
        {
            rb = gameObject.AddComponent<Rigidbody>();
            rb.mass = 5f;
            rb.useGravity = true;
            rb.linearDamping = 0.5f;
        }

        // 获取所有同类组件
        Collider[] colliders = GetComponents<Collider>();

        // 获取所有子对象上的同类组件
        Collider[] childColliders = GetComponentsInChildren<Collider>();
    }
}
```

---

## 3. Scene（场景）

Scene 是 Unity 项目的组织单元，每个场景代表游戏的一个独立关卡或界面。

### 3.1 场景管理 API

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneManagementDemo : MonoBehaviour
{
    // 加载场景（需要在 Build Settings 中添加）
    public void LoadGameScene()
    {
        SceneManager.LoadScene("GameScene");
    }

    // 异步加载（带进度条）
    public void LoadSceneAsync()
    {
        StartCoroutine(LoadSceneCoroutine("Level1"));
    }

    private System.Collections.IEnumerator LoadSceneCoroutine(string sceneName)
    {
        AsyncOperation operation = SceneManager.LoadSceneAsync(sceneName);
        operation.allowSceneActivation = false;

        while (!operation.isDone)
        {
            float progress = Mathf.Clamp01(operation.progress / 0.9f);
            Debug.Log($"加载进度: {progress * 100}%");

            if (progress >= 0.9f)
            {
                operation.allowSceneActivation = true;
            }

            yield return null;
        }
    }

    // 重新加载当前场景
    public void RestartLevel()
    {
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }

    // 加载下一个场景
    public void LoadNextLevel()
    {
        int nextIndex = SceneManager.GetActiveScene().buildIndex + 1;
        if (nextIndex < SceneManager.sceneCountInBuildSettings)
        {
            SceneManager.LoadScene(nextIndex);
        }
    }
}
```

> ⚠️ **注意**: 使用 `SceneManager.LoadScene` 前必须将场景添加到 **File → Build Settings → Scenes In Build**。

---

## 4. 脚本编程

Unity 脚本使用 C# 编写，继承自 `MonoBehaviour`。

### 4.1 生命周期函数

```csharp
using UnityEngine;

public class LifecycleDemo : MonoBehaviour
{
    // ============ 初始化阶段 ============

    /// <summary>对象被创建时调用（即使未激活），仅一次</summary>
    private void Awake()
    {
        Debug.Log("Awake: 初始化引用和状态");
    }

    /// <summary>Start 在第一次 Update 之前调用，仅一次</summary>
    private void Start()
    {
        Debug.Log("Start: 初始化逻辑");
    }

    /// <summary>对象变为激活状态时调用</summary>
    private void OnEnable()
    {
        Debug.Log("OnEnable");
    }

    /// <summary>对象变为非激活状态时调用</summary>
    private void OnDisable()
    {
        Debug.Log("OnDisable");
    }

    // ============ 每帧循环 ============

    /// <summary>每帧调用一次（帧率相关）</summary>
    private void Update()
    {
        // 帧率无关移动
        float moveSpeed = 5f;
        transform.Translate(Vector3.forward * moveSpeed * Time.deltaTime);
    }

    /// <summary>固定时间间隔调用（默认 0.02s），用于物理计算</summary>
    private void FixedUpdate()
    {
        // 物理相关代码放这里
    }

    /// <summary>所有 Update 之后调用，适合跟随逻辑</summary>
    private void LateUpdate()
    {
        // 摄像机跟随等
    }

    // ============ 销毁阶段 ============

    /// <summary>对象被销毁时调用</summary>
    private void OnDestroy()
    {
        Debug.Log("OnDestroy: 清理资源");
    }
}
```

### 4.2 生命周期流程图

```
Awake → OnEnable → Start → FixedUpdate(s) → Update(s) → LateUpdate(s) → ... → OnDisable → OnDestroy
```

### 4.3 完整角色控制器示例

```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    [Header("移动设置")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float rotationSpeed = 10f;
    [SerializeField] private float jumpHeight = 2f;
    [SerializeField] private float gravity = -9.81f;

    [Header("地面检测")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundDistance = 0.4f;
    [SerializeField] private LayerMask groundMask;

    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        // 地面检测
        isGrounded = Physics.CheckSphere(groundCheck.position, groundDistance, groundMask);

        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f; // 保持贴地
        }

        // WASD 输入
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        Vector3 move = transform.right * x + transform.forward * z;
        controller.Move(move * moveSpeed * Time.deltaTime);

        // 跳跃
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        // 重力
        velocity.y += gravity * Time.deltaTime;
        controller.Move(velocity * Time.deltaTime);
    }
}
```

---

## 5. 物理引擎

Unity 使用 NVIDIA PhysX 物理引擎，提供刚体动力学、碰撞检测和关节约束。

### 5.1 Rigidbody 基础

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class PhysicsDemo : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void Start()
    {
        // Rigidbody 配置
        rb.mass = 1f;
        rb.linearDamping = 0.05f;       // 线性阻尼
        rb.angularDamping = 0.05f;     // 角阻尼
        rb.useGravity = true;
        rb.interpolation = RigidbodyInterpolation.Interpolate;
        rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
    }

    private void Update()
    {
        // 施加力
        if (Input.GetKeyDown(KeyCode.Space))
        {
            rb.AddForce(Vector3.up * 500f, ForceMode.Impulse);
        }

        // 施加方向力
        if (Input.GetKey(KeyCode.W))
        {
            rb.AddForce(transform.forward * 10f, ForceMode.Force);
        }
    }
}
```

### 5.2 碰撞检测

```csharp
using UnityEngine;

public class CollisionDemo : MonoBehaviour
{
    /// <summary>当碰撞体进入触发器时调用（双方至少有一个 isTrigger = true）</summary>
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Pickup"))
        {
            Debug.Log($"拾取了: {other.gameObject.name}");
            Destroy(other.gameObject);
        }
    }

    /// <summary>当碰撞体离开触发器时调用</summary>
    private void OnTriggerExit(Collider other)
    {
        Debug.Log($"离开了触发器: {other.name}");
    }

    /// <summary>物理碰撞时调用（双方都有 Collider 且无 isTrigger）</summary>
    private void OnCollisionEnter(Collision collision)
    {
        ContactPoint contact = collision.contacts[0];
        Debug.Log($"碰撞对象: {collision.gameObject.name}, 接触点: {contact.point}");

        // 碰撞冲击力
        float impactForce = collision.relativeVelocity.magnitude;
        if (impactForce > 5f)
        {
            // 高速碰撞逻辑
        }
    }
}
```

### 5.3 射线检测

```csharp
using UnityEngine;

public class RaycastDemo : MonoBehaviour
{
    private Camera mainCamera;

    private void Start()
    {
        mainCamera = Camera.main;
    }

    private void Update()
    {
        // 鼠标点击射线
        if (Input.GetMouseButtonDown(0))
        {
            Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);

            if (Physics.Raycast(ray, out RaycastHit hit, 100f))
            {
                Debug.Log($"射线命中: {hit.collider.gameObject.name} at {hit.point}");

                // 获取命中物体的脚本
                var interactable = hit.collider.GetComponent<IInteractable>();
                interactable?.Interact();
            }
        }

        // 球形射线检测（范围检测）
        Collider[] hits = Physics.OverlapSphere(transform.position, 5f);
        foreach (var hit in hits)
        {
            if (hit.CompareTag("Enemy"))
            {
                Debug.Log($"发现敌人: {hit.name}");
            }
        }
    }
}

public interface IInteractable
{
    void Interact();
}
```

### 5.4 力模式对比

| ForceMode | 说明 | 适用场景 |
|-----------|------|----------|
| `Force` | 连续力（考虑质量） | 推动物体 |
| `Impulse` | 瞬间冲量（考虑质量） | 跳跃、爆炸冲击 |
| `Acceleration` | 连续加速度（忽略质量） | 风力、磁力 |
| `VelocityChange` | 瞬间速度变化（忽略质量） | 弹射、传送 |

---

## 6. UI 系统

Unity 使用 **uGUI**（基于 Canvas）作为主要 UI 系统。

### 6.1 Canvas 与基础控件

```
Canvas
├── EventSystem
├── Panel (背景面板)
│   ├── Text / TextMeshPro (文字)
│   ├── Button (按钮)
│   ├── Image (图片)
│   ├── Slider (滑块)
│   └── Toggle (复选框)
```

### 6.2 UI 交互脚本

```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UIManager : MonoBehaviour
{
    [Header("UI 引用")]
    [SerializeField] private Button startButton;
    [SerializeField] private Button quitButton;
    [SerializeField] private TMP_Text scoreText;
    [SerializeField] private Slider healthSlider;
    [SerializeField] private GameObject gameOverPanel;

    private int score = 0;

    private void Start()
    {
        // 按钮点击事件
        startButton.onClick.AddListener(OnStartClicked);
        quitButton.onClick.AddListener(OnQuitClicked);

        // Slider 值变化事件
        healthSlider.onValueChanged.AddListener(OnHealthChanged);

        UpdateScoreDisplay();
    }

    private void OnStartClicked()
    {
        Debug.Log("开始游戏");
        gameOverPanel.SetActive(false);
    }

    private void OnQuitClicked()
    {
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }

    private void OnHealthChanged(float value)
    {
        Debug.Log($"血量变化: {value}");
    }

    public void AddScore(int points)
    {
        score += points;
        UpdateScoreDisplay();
    }

    private void UpdateScoreDisplay()
    {
        scoreText.text = $"分数: {score}";
    }

    private void OnDestroy()
    {
        // 移除事件监听，防止内存泄漏
        startButton.onClick.RemoveListener(OnStartClicked);
        quitButton.onClick.RemoveListener(OnQuitClicked);
        healthSlider.onValueChanged.RemoveListener(OnHealthChanged);
    }
}
```

### 6.3 动态创建 UI

```csharp
using UnityEngine;
using UnityEngine.UI;

public class DynamicUI : MonoBehaviour
{
    [SerializeField] private GameObject buttonPrefab;
    [SerializeField] private Transform buttonContainer; // ScrollView 的 Content

    private void Start()
    {
        string[] levelNames = { "第一关", "第二关", "第三关", "第四关" };

        foreach (string name in levelNames)
        {
            GameObject newButton = Instantiate(buttonPrefab, buttonContainer);
            newButton.GetComponentInChildren<TMPro.TMP_Text>().text = name;

            string capturedName = name; // 闭包陷阱：必须捕获局部变量
            newButton.GetComponent<Button>().onClick.AddListener(() =>
            {
                Debug.Log($"选择了: {capturedName}");
            });
        }
    }
}
```

---

## 7. 最佳实践

### 7.1 编码规范

- ✅ 使用 `[SerializeField] private` 代替 `public` 来暴露字段到 Inspector
- ✅ 使用 `RequireComponent` 确保依赖组件存在
- ✅ 在 `Awake` 中获取引用，在 `Start` 中初始化逻辑
- ✅ 使用 `Time.deltaTime` 实现帧率无关
- ✅ 在 `OnDestroy` 中注销事件监听
- ❌ 避免在 `Update` 中使用 `GameObject.Find()`、`GetComponent()`
- ❌ 避免使用 `GameObject.Find` 进行频繁查找

### 7.2 性能技巧

```csharp
// ❌ 错误：每帧调用 GetComponent
void Update()
{
    var renderer = GetComponent<Renderer>(); // 每帧分配查找
}

// ✅ 正确：缓存引用
private Renderer myRenderer;

void Awake()
{
    myRenderer = GetComponent<Renderer>();
}
```

```csharp
// ✅ 使用对象池减少实例化开销
public class SimpleObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject prefab;
    [SerializeField] private int poolSize = 20;

    private readonly Queue<GameObject> pool = new();

    private void Awake()
    {
        for (int i = 0; i < poolSize; i++)
        {
            GameObject obj = Instantiate(prefab, transform);
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }

    public GameObject Get()
    {
        if (pool.Count > 0)
        {
            GameObject obj = pool.Dequeue();
            obj.SetActive(true);
            return obj;
        }
        return Instantiate(prefab, transform);
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

---

## 8. 相关页面

- [[Unreal Engine基础]] - 对比学习虚幻引擎的 Actor/Pawn/GameMode 概念
- [[游戏性能优化]] - DrawCall 优化、对象池、内存管理深入实践
- [[游戏设计模式]] - ECS 架构、状态机、行为树在游戏中的应用
- [[游戏服务器架构]] - 与 Unity 客户端配合的服务端设计方案

---

## 参考资源

- [Unity 官方文档](https://docs.unity3d.com/Manual/index.html)
- [Unity Scripting API](https://docs.unity3d.com/ScriptReference/)
- [Unity Learn](https://learn.unity.com/)

---

> 📅 最后更新: 2026-06-28 | ✍️ 作者: AI-Agent
