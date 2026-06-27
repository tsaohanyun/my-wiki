---
title: Unreal Engine 基础
date: 2026-06-28
category: 游戏开发
tags:
  - UnrealEngine
  - UE5
  - C++
  - Blueprint
  - 游戏引擎
author: AI-Agent
description: Unreal Engine 5 核心概念详解，涵盖 Actor、Pawn、GameMode、Blueprint 可视化脚本、C++ 游戏开发及材质系统。
---

# Unreal Engine 基础

> Unreal Engine (UE) 是 Epic Games 开发的世界级 3D 游戏引擎，以高端渲染品质、Blueprint 可视化编程和强大的 C++ 框架著称。本文系统介绍 UE5 的核心概念。

---

## 目录

1. [Actor 与组件系统](#1-actor-与组件系统)
2. [Pawn 与 Controller](#2-pawn-与-controller)
3. [GameMode 与游戏框架](#3-gamemode-与游戏框架)
4. [Blueprint 可视化编程](#4-blueprint-可视化编程)
5. [C++ 开发](#5-c-开发)
6. [材质系统](#6-材质系统)
7. [最佳实践](#7-最佳实践)
8. [相关页面](#8-相关页面)

---

## 1. Actor 与组件系统

Actor 是 UE 中可放置到关卡中的所有对象的基类。Actor 本身不含变换信息，它由挂载的 Component 组成。

### 1.1 Actor 继承体系

```
UObject (所有对象的根类)
  └── AActor (可放置到关卡中的对象)
        ├── APawn (可被 Controller 操控)
        │     └── ACharacter (带 CharacterMovement 的高级 Pawn)
        ├── AController
        │     └── APlayerController / AAIController
        ├── AGameModeBase
        ├── AInfo
        └── ... (各类特殊 Actor)
```

### 1.2 自定义 Actor（C++）

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    // 构造函数
    AMyActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // ===== 组件声明 =====

    // 根组件（场景组件，提供变换）
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USceneComponent* DefaultRoot;

    // 静态网格组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* MeshComp;

    // 粒子组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UParticleSystemComponent* ParticleComp;

    // ===== 可编辑属性 =====

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings", meta = (ClampMin = "0.0"))
    float RotationSpeed = 90.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    bool bAutoRotate = true;

    // ===== 函数 =====

    UFUNCTION(BlueprintCallable, Category = "MyActor")
    void StartRotation();

    UFUNCTION(BlueprintCallable, Category = "MyActor")
    void StopRotation();

private:
    bool bIsRotating = false;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Kismet/GameplayStatics.h"

AMyActor::AMyActor()
{
    // 设置 Tick 频率
    PrimaryActorTick.bCanEverTick = true;

    // 创建根组件
    DefaultRoot = CreateDefaultSubobject<USceneComponent>(TEXT("DefaultRoot"));
    RootComponent = DefaultRoot;

    // 创建网格组件并附加到根
    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
    MeshComp->SetupAttachment(RootComponent);

    // 创建粒子组件
    ParticleComp = CreateDefaultSubobject<UParticleSystemComponent>(TEXT("ParticleComp"));
    ParticleComp->SetupAttachment(MeshComp);
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    UE_LOG(LogTemp, Warning, TEXT("MyActor BeginPlay! Location: %s"),
        *GetActorLocation().ToString());

    if (bAutoRotate)
    {
        StartRotation();
    }
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bIsRotating)
    {
        FRotator NewRotation = GetActorRotation();
        NewRotation.Yaw += RotationSpeed * DeltaTime;
        SetActorRotation(NewRotation);
    }
}

void AMyActor::StartRotation()
{
    bIsRotating = true;
}

void AMyActor::StopRotation()
{
    bIsRotating = false;
}
```

### 1.3 UPROPERTY 说明符速查

| 说明符 | 作用 |
|--------|------|
| `EditAnywhere` | Inspector 和 CDO 都可编辑 |
| `EditDefaultsOnly` | 仅 CDO（类默认值）可编辑 |
| `EditInstanceOnly` | 仅实例可编辑 |
| `VisibleAnywhere` | 只读显示（所有地方） |
| `BlueprintReadWrite` | Blueprint 可读写 |
| `Category = "X"` | 分组归类 |
| `meta = (ClampMin="0")` | 数值约束 |

---

## 2. Pawn 与 Controller

Pawn 是玩家或 AI 可以控制的 Actor。Character 是 Pawn 的扩展，内置角色移动组件。

### 2.1 自定义 Pawn

```cpp
// MyFlyingPawn.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MyFlyingPawn.generated.h"

UCLASS()
class MYGAME_API AMyFlyingPawn : public APawn
{
    GENERATED_BODY()

public:
    AMyFlyingPawn();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

private:
    UPROPERTY(VisibleAnywhere, Category = "Components")
    UCapsuleComponent* CapsuleComp;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    UStaticMeshComponent* PlaneMesh;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    USpringArmComponent* SpringArm;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    UCameraComponent* Camera;

    // 输入处理
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookUp(float Value);
    void LookRight(float Value);

    float CurrentForwardSpeed = 0.0f;
    float CurrentYawSpeed = 0.0f;
    float CurrentPitchSpeed = 0.0f;

    UPROPERTY(EditAnywhere, Category = "Flight")
    float MaxSpeed = 3000.0f;

    UPROPERTY(EditAnywhere, Category = "Flight")
    float Acceleration = 500.0f;
};
```

### 2.2 Character 类（C++）

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

protected:
    virtual void BeginPlay() override;

    // 摄像机
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    class USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    class UCameraComponent* FollowCamera;

    // 输入绑定
    void MoveForward(float Value);
    void MoveRight(float Value);
    void StartJump();
    void StopJump();
};
```

```cpp
// MyCharacter.cpp - 关键实现
#include "MyCharacter.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // 不旋转跟随控制器
    bUseControllerRotationYaw = false;

    // 摄像机弹簧臂
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 300.0f;
    CameraBoom->bUsePawnControlRotation = true;

    // 摄像机
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    // 角色移动配置
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);
    GetCharacterMovement()->JumpZVelocity = 600.0f;
    GetCharacterMovement()->AirControl = 0.2f;
}

void AMyCharacter::MoveForward(float Value)
{
    if (Controller && Value != 0.0f)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        AddMovementInput(Direction, Value);
    }
}

void AMyCharacter::MoveRight(float Value)
{
    if (Controller && Value != 0.0f)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
        AddMovementInput(Direction, Value);
    }
}
```

---

## 3. GameMode 与游戏框架

### 3.1 游戏框架类关系

```
GameMode (游戏规则)
  ├── 设定 DefaultPawnClass（玩家出生时的 Pawn）
  ├── 设定 PlayerControllerClass（玩家控制器）
  ├── 设定 PlayerStateClass（玩家状态数据）
  ├── 设定 GameStateClass（全局游戏状态）
  └── 设定 SpectatorClass（观战 Pawn）

GameSession (会话管理，处理登录/连接)
  └── OnlineSubsystem (Steam/Epic 等平台集成)
```

### 3.2 自定义 GameMode

```cpp
// MyGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class AMyCharacter;

UCLASS()
class MYGAME_API AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMyGameMode();

protected:
    virtual void BeginPlay() override;

    // 玩家进入游戏时调用
    virtual void PostLogin(APlayerController* NewPlayer) override;

    // 玩家退出时调用
    virtual void Logout(AController* Exiting) override;

    // 玩家死亡处理
    UFUNCTION(BlueprintCallable, Category = "GameMode")
    void OnPlayerDeath(AController* Victim, AController* Killer);

private:
    UPROPERTY(EditDefaultsOnly, Category = "Settings")
    int32 ScoreToWin = 100;

    UPROPERTY(EditDefaultsOnly, Category = "Settings")
    float RespawnDelay = 3.0f;

    void CheckWinCondition();
};
```

```cpp
// MyGameMode.cpp
#include "MyGameMode.h"
#include "GameFramework/PlayerState.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"

AMyGameMode::AMyGameMode()
{
    // 设定默认类
    DefaultPawnClass = AMyCharacter::StaticClass();

    // 可在蓝图中覆盖
    bUseSeamlessTravel = true;

    // 延迟初始化
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    UE_LOG(LogTemp, Warning, TEXT("MyGameMode BeginPlay - Game Started!"));
}

void AMyGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);

    if (NewPlayer && NewPlayer->PlayerState)
    {
        FString PlayerName = NewPlayer->PlayerState->GetPlayerName();
        UE_LOG(LogTemp, Warning, TEXT("Player joined: %s"), *PlayerName);
    }
}

void AMyGameMode::Logout(AController* Exiting)
{
    Super::Logout(Exiting);
    UE_LOG(LogTemp, Warning, TEXT("Player logged out"));
}

void AMyGameMode::OnPlayerDeath(AController* Victim, AController* Killer)
{
    if (Victim)
    {
        // 延迟重生
        FTimerHandle RespawnTimer;
        FTimerDelegate RespawnDelegate;
        RespawnDelegate.BindUFunction(this, "RestartPlayer", Victim);

        GetWorldTimerManager().SetTimer(
            RespawnTimer, RespawnDelegate, RespawnDelay, false);
    }

    if (Killer && Killer->PlayerState)
    {
        // 增加击杀分数
        Killer->PlayerState->SetScore(Killer->PlayerState->GetScore() + 10.0f);
        CheckWinCondition();
    }
}

void AMyGameMode::CheckWinCondition()
{
    for (FConstPlayerControllerIterator It = GetWorld()->GetPlayerControllerIterator(); It; ++It)
    {
        APlayerController* PC = It->Get();
        if (PC && PC->PlayerState && PC->PlayerState->GetScore() >= ScoreToWin)
        {
            UE_LOG(LogTemp, Warning, TEXT("Player %s wins!"),
                *PC->PlayerState->GetPlayerName());
            // 触发胜利逻辑...
            break;
        }
    }
}
```

---

## 4. Blueprint 可视化编程

Blueprint 是 UE 的可视化脚本系统，允许非程序员快速实现游戏逻辑。

### 4.1 Blueprint 类型

| 类型 | 说明 | 用途 |
|------|------|------|
| **Level Blueprint** | 关卡专属蓝图 | 关卡事件、过场动画 |
| **Blueprint Class** | 可实例化的类 | 角色、道具、武器 |
| **Blueprint Interface** | 接口 | 多态通信 |
| **Blueprint Function Library** | 静态函数库 | 工具函数 |
| **Blueprint Macro Library** | 宏库 | 复用节点组 |
| **Data Asset** | 数据资产 | 配置数据 |
| **Widget Blueprint (UMG)** | UI 控件 | 菜单、HUD |
| **Animation Blueprint** | 动画蓝图 | 角色动画状态机 |

### 4.2 C++ 与 Blueprint 交互

```cpp
// ===== C++ 调用 Blueprint 函数 =====

// 在 C++ 中声明为 BlueprintImplementableEvent
UFUNCTION(BlueprintImplementableEvent, Category = "Weapon")
void OnWeaponFired();

// 在 C++ 中调用（如果有 Blueprint 实现，会执行蓝图逻辑）
OnWeaponFired();


// ===== Blueprint 调用 C++ 函数 =====

// BlueprintCallable 让蓝图可以调用
UFUNCTION(BlueprintCallable, Category = "Weapon")
void Fire()
{
    if (AmmoCount > 0)
    {
        AmmoCount--;
        // 发射逻辑...
    }
}


// ===== BlueprintNativeEvent: C++ 默认实现 + Blueprint 可覆盖 =====

UFUNCTION(BlueprintNativeEvent, Category = "Character")
void OnDeath();
// 注意：实现函数名需要加 _Implementation 后缀
void AMyCharacter::OnDeath_Implementation()
{
    // C++ 默认实现
    UE_LOG(LogTemp, Warning, TEXT("Character died"));
}
```

### 4.3 Blueprint 与 C++ 对比

| 特性 | Blueprint | C++ |
|------|-----------|-----|
| 学习难度 | 低 | 高 |
| 执行性能 | 较慢 | 快 |
| 版本控制 | 不友好 | 友好 |
| 逻辑复杂度 | 适合中等 | 适合复杂 |
| 迭代速度 | 快 | 需编译 |
| 团队协作 | 较差 | 好 |

> 💡 **推荐**: 核心系统用 C++，游戏玩法逻辑用 Blueprint（"C++ 做骨架，Blueprint 做血肉"）。

---

## 5. C++ 开发

### 5.1 反射系统

UE 通过 `UCLASS`、`USTRUCT`、`UENUM`、`UFUNCTION` 宏和 `.generated.h` 文件实现 C++ 反射。

```cpp
// 枚举（可被 Blueprint 使用）
UENUM(BlueprintType)
enum class EWeaponType : uint8
{
    Sword   UMETA(DisplayName = "剑"),
    Bow     UMETA(DisplayName = "弓"),
    Staff   UMETA(DisplayName = "法杖")
};

// 结构体
USTRUCT(BlueprintType)
struct FWeaponData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    FString Name;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    int32 Damage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float Range = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    EWeaponType Type = EWeaponType::Sword;
};
```

### 5.2 委托（事件系统）

```cpp
// MyWeapon.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyWeapon.generated.h"

// 声明委托类型（多播，Blueprint 可绑定）
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAmmoChanged, int32, NewAmmo);

UCLASS()
class MYGAME_API AMyWeapon : public AActor
{
    GENERATED_BODY()

public:
    // Blueprint 可绑定的委托
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnAmmoChanged OnAmmoChanged;

    UFUNCTION(BlueprintCallable, Category = "Weapon")
    void ConsumeAmmo(int32 Amount)
    {
        CurrentAmmo = FMath::Max(0, CurrentAmmo - Amount);
        // 广播事件
        OnAmmoChanged.Broadcast(CurrentAmmo);
    }

private:
    UPROPERTY(EditAnywhere, Category = "Weapon")
    int32 CurrentAmmo = 30;
};
```

### 5.3 接口系统

```cpp
// InteractableInterface.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "InteractableInterface.generated.h"

// 此类不能被实例化，仅用于反射
UINTERFACE(BlueprintType)
class UInteractableInterface : public UInterface
{
    GENERATED_BODY()
};

class IInteractableInterface
{
    GENERATED_BODY()

public:
    // BlueprintNativeEvent: Blueprint 可覆盖，C++ 提供 _Implementation
    UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
    bool CanInteract(AActor* Interactor);

    UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
    void OnInteract(AActor* Interactor);

    UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
    FString GetInteractionText();
};

// 默认实现
inline bool IInteractableInterface::CanInteract_Implementation(AActor* Interactor) { return true; }
inline void IInteractableInterface::OnInteract_Implementation(AActor* Interactor) {}
inline FString IInteractableInterface::GetInteractionText_Implementation() { return TEXT("交互"); }
```

### 5.4 在其他 Actor 中使用接口

```cpp
// 检查并调用接口
if (AActor* HitActor = HitResult.GetActor())
{
    if (HitActor->GetClass()->ImplementsInterface(UInteractableInterface::StaticClass()))
    {
        if (IInteractableInterface::Execute_CanInteract(HitActor, this))
        {
            FString Prompt = IInteractableInterface::Execute_GetInteractionText(HitActor);
            IInteractableInterface::Execute_OnInteract(HitActor, this);
        }
    }
}
```

---

## 6. 材质系统

### 6.1 材质节点基础

UE 材质基于节点图，通过连接数学运算节点生成 Shader。

```
主要输入引脚 (Material Output Node):
├── Base Color (基础颜色)
├── Metallic (金属度 0~1)
├── Specular (高光 0~1)
├── Roughness (粗糙度 0~1)
├── Emissive Color (自发光)
├── Normal (法线贴图)
├── World Position Offset (世界位置偏移)
├── Ambient Occlusion (环境光遮蔽)
├── Refraction (折射)
├── Pixel Depth Offset (像素深度偏移)
├── Subsurface Color (次表面散射颜色)
├── Custom Data 0/1 (自定义数据)
└── Opacity / Opacity Mask (透明度/蒙版)
```

### 6.2 材质实例

```
Material (Master) - 父材质
  ├── Material Instance Dynamic (运行时可修改参数)
  └── Material Instance Constant (设计时修改参数)
```

```cpp
// 运行时修改材质参数
void AMyActor::ChangeMaterialColor(FLinearColor NewColor)
{
    UStaticMeshComponent* MeshComp = FindComponentByClass<UStaticMeshComponent>();
    if (MeshComp && MeshComp->GetMaterial(0))
    {
        // 创建动态材质实例
        UMaterialInstanceDynamic* DynMat = MeshComp->CreateDynamicMaterialInstance(0);
        if (DynMat)
        {
            DynMat->SetVectorParameterValue(FName("BaseColor"), NewColor);
            DynMat->SetScalarParameterValue(FName("EmissiveIntensity"), 2.0f);
        }
    }
}
```

### 6.3 PBR 工作流

| 通道 | 数据类型 | 范围 | 作用 |
|------|----------|------|------|
| Base Color | sRGB | 0-255 | 固有颜色（无光照） |
| Metallic | Linear (Grayscale) | 0 or 1 | 0=非金属, 1=金属 |
| Roughness | Linear (Grayscale) | 0-1 | 0=光滑镜面, 1=粗糙漫反射 |
| Normal | Linear (RGB) | -1 to 1 | 表面凹凸细节 |
| AO | Linear (Grayscale) | 0-1 | 环境光遮蔽 |

### 6.4 材质函数复用

```cpp
// 创建可复用材质节点组的 Custom HLSL 节点（高级用法）
// 在 Custom 节点中输入 HLSL 代码：

// 示例: 简单的菲涅尔效果
float fresnel = pow(1.0 - dot(normalize(Normal), normalize(ViewDir)), 3.0);
return fresnel * FresnelColor * FresnelIntensity;
```

---

## 7. 最佳实践

### 7.1 C++ 编码规范

- ✅ 类名以 `A` 开头继承 Actor，`U` 开头继承 UObject，`I` 开头为接口，`F` 开头为结构体，`E` 开头为枚举
- ✅ 使用 `UPROPERTY` 标记所有需要序列化/GC 管理的成员变量
- ✅ 使用 `UFUNCTION` 标记需要反射的函数
- ✅ 前置声明头文件，在 `.cpp` 中 `#include`（减少编译依赖）
- ✅ 使用 `TWeakObjectPtr<T>` 持有非拥有引用，避免悬垂指针
- ❌ 避免在头文件中 `#include` 不必要的 `.h`
- ❌ 避免使用原生 C++ 指针指向 UObject（使用 UPROPERTY 指针或智能指针）

### 7.2 Blueprint 最佳实践

- ✅ 将复杂逻辑拆分到多个函数节点中
- ✅ 使用 Blueprint 接口进行多态通信（比 Cast 更灵活）
- ✅ 在 C++ 中暴露 `BlueprintCallable` 函数，减少 Blueprint 中的复杂逻辑
- ✅ 使用 `BlueprintNativeEvent` 提供 C++ 默认实现 + Blueprint 覆盖能力
- ❌ 避免在 Tick 事件中做重计算
- ❌ 避免在 Blueprint 中大量使用 Cast To（用接口替代）

### 7.3 性能提示

- ✅ 关闭不需要 Tick 的 Actor：`PrimaryActorTick.bCanEverTick = false`
- ✅ 使用 `SetActorTickEnabled(false)` 暂停远距离对象
- ✅ 使用 `Async` 任务处理 IO 和重计算
- ✅ 启用 Niagara 的 GPU 粒子模拟
- ✅ 使用 Lumen GI 时合理设置 `Cast Ray Traced Shadows`

---

## 8. 相关页面

- [[Unity开发入门]] - 对比学习 Unity 的 GameObject/Component/Script 概念
- [[游戏性能优化]] - UE/通用引擎的 DrawCall、LOD、内存优化策略
- [[游戏设计模式]] - ECS、状态机、行为树在 UE 中的实现
- [[游戏服务器架构]] - UE Dedicated Server 与自定义服务器方案

---

## 参考资源

- [Unreal Engine 官方文档](https://docs.unrealengine.com/5.0/en-US/)
- [Epic Developer Community](https://dev.epicgames.com/)
- [Unreal C++ API Reference](https://docs.unrealengine.com/5.0/en-US/API/)
- [Tom Looman's UE C++ Course](https://www.tomlooman.com/)

---

> 📅 最后更新: 2026-06-28 | ✍️ 作者: AI-Agent
