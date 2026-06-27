---
title: Unreal Engine基础
aliases:
  - UE5 Getting Started
  - UE基础
  - Unreal Engine Tutorial
tags:
  - unreal-engine
  - ue5
  - cpp
  - blueprint
  - game-development
type: wiki
status: active
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent知识库
difficulty: intermediate
project: 游戏开发
---

# Unreal Engine 基础

Unreal Engine 5（UE5）是 Epic Games 开发的 AAA 级游戏引擎，以其强大的图形渲染（Lumen/Nanite）和可视化脚本（Blueprint）著称。

---

## 一、C++ 与 Blueprint 协作

### 1.1 基础 Actor 类

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
    AMyActor();

    // Blueprint 可编辑属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Config")
    float MoveSpeed = 600.f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* MeshComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USphereComponent* CollisionComp;

    // Blueprint 可调用函数
    UFUNCTION(BlueprintCallable, Category = "Gameplay")
    void ApplyDamage(float Amount);

    // Blueprint 可实现事件
    UFUNCTION(BlueprintImplementableEvent, Category = "Gameplay")
    void OnDamageReceived(float Amount);

protected:
    virtual void BeginPlay() override;

    // Blueprint 可重写
    UFUNCTION(BlueprintNativeEvent, Category = "Gameplay")
    void InitializeActor();
    virtual void InitializeActor_Implementation();

public:
    virtual void Tick(float DeltaTime) override;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建组件层级
    CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
    RootComponent = CollisionComp;
    CollisionComp->SetSphereRadius(50.f);
    CollisionComp->SetCollisionProfileName(TEXT("Pawn"));

    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    MeshComp->SetupAttachment(RootComponent);
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    InitializeActor();
}

void AMyActor::InitializeActor_Implementation()
{
    UE_LOG(LogTemp, Log, TEXT("AMyActor initialized with speed: %f"), MoveSpeed);
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    FVector Forward = GetActorForwardVector();
    AddActorWorldOffset(Forward * MoveSpeed * DeltaTime);
}

void AMyActor::ApplyDamage(float Amount)
{
    UE_LOG(LogTemp, Warning, TEXT("Damage applied: %f"), Amount);
    OnDamageReceived(Amount); // 调用 Blueprint 实现的事件
}
```

### 1.2 委托（Delegate）系统

```cpp
// 声明多播委托
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
    FOnHealthChanged, float, NewHealth, float, MaxHealth);

UCLASS()
class ACharacterBase : public ACharacter
{
    GENERATED_BODY()

public:
    // Blueprint 可绑定的事件
    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnHealthChanged OnHealthChanged;

    UFUNCTION(BlueprintCallable)
    void SetHealth(float NewHealth)
    {
        CurrentHealth = FMath::Clamp(NewHealth, 0.f, MaxHealth);
        OnHealthChanged.Broadcast(CurrentHealth, MaxHealth);
    }

private:
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};
```

---

## 二、材质系统

### 2.1 运行时动态材质

```cpp
// 动态材质实例控制
UCLASS()
class AMaterialController : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Material")
    UMaterialInterface* BaseMaterial;

    UPROPERTY(VisibleAnywhere, Category = "Components")
    UStaticMeshComponent* MeshComp;

    UPROPERTY()
    UMaterialInstanceDynamic* DynMaterial;

    virtual void BeginPlay() override
    {
        Super::BeginPlay();

        if (BaseMaterial && MeshComp)
        {
            DynMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, this);
            MeshComp->SetMaterial(0, DynMaterial);
        }
    }

    UFUNCTION(BlueprintCallable, Category = "Material")
    void SetEmissiveColor(FLinearColor Color, float Intensity)
    {
        if (DynMaterial)
        {
            DynMaterial->SetVectorParameterValue(FName("EmissiveColor"), Color);
            DynMaterial->SetScalarParameterValue(FName("EmissiveIntensity"), Intensity);
        }
    }

    UFUNCTION(BlueprintCallable, Category = "Material")
    void SetDamageEffect(float Amount)
    {
        if (DynMaterial)
        {
            // 溶解效果参数
            DynMaterial->SetScalarParameterValue(FName("DissolveAmount"), Amount);
            DynMaterial->SetVectorParameterValue(FName("EdgeColor"),
                FLinearColor(1.f, 0.3f, 0.f, 1.f));
        }
    }
};
```

### 2.2 材质参数集合（Material Parameter Collection）

```cpp
// 全局材质参数 - 影响所有引用该 Collection 的材质
void AMyGameMode::UpdateGlobalWind(float WindStrength)
{
    UMaterialParameterCollection* MPC = LoadObject<UMaterialParameterCollection>(
        nullptr, TEXT("/Game/Materials/MPC_Global"));

    if (MPC)
    {
        UMaterialParameterCollectionInstance* Instance =
            GetWorld()->GetParameterCollectionInstance(MPC);
        Instance->SetScalarParameterValue(FName("WindStrength"), WindStrength);
    }
}
```

---

## 三、动画系统

### 3.1 动画蓝图（Animation Blueprint）中的 C++ 接口

```cpp
// 自定义 AnimInstance
UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 动画蓝图可读取的属性
    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    float Speed = 0.f;

    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    float Direction = 0.f;

    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    bool bIsFalling = false;

    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    bool bIsDead = false;

    // 每帧更新动画数据
    virtual void NativeUpdateAnimation(float DeltaSeconds) override
    {
        Super::NativeUpdateAnimation(DeltaSeconds);

        APawn* OwnerPawn = TryGetPawnOwner();
        if (!OwnerPawn) return;

        // 获取速度
        FVector Velocity = OwnerPawn->GetVelocity();
        Speed = Velocity.Size2D();

        // 获取朝向
        FRotator AimRot = OwnerPawn->GetBaseAimRotation();
        Direction = CalculateDirection(Velocity, AimRot);

        // 是否在空中
        ACharacter* Character = Cast<ACharacter>(OwnerPawn);
        if (Character)
        {
            bIsFalling = Character->GetCharacterMovement()->IsFalling();
        }
    }

    // Blueprint 可调用的通知回调
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void AnimNotify_FootStep(USkeletalMeshComponent* MeshComp);

    UFUNCTION(BlueprintCallable, Category = "Animation")
    void AnimNotify_AttackHit();
};
```

### 3.2 动画通知（Anim Notify）

```cpp
// 自定义动画通知
UCLASS()
class UAnimNotify_PlayFootSound : public UAnimNotify
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sound")
    USoundBase* FootStepSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sound")
    float VolumeMultiplier = 1.f;

    virtual void Notify(USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference) override
    {
        Super::Notify(MeshComp, Animation, EventReference);

        if (FootStepSound && MeshComp)
        {
            UGameplayStatics::PlaySoundAtLocation(
                MeshComp->GetWorld(),
                FootStepSound,
                MeshComp->GetComponentLocation(),
                VolumeMultiplier
            );
        }
    }
};
```

### 3.3 动画蒙太奇与状态机交互

```cpp
// 播放攻击蒙太奇
UCLASS()
class ACombatCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    UAnimMontage* AttackMontage;

    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    UAnimMontage* HitReactMontage;

    UFUNCTION(BlueprintCallable, Category = "Combat")
    void PlayAttack()
    {
        if (!AttackMontage) return;

        UAnimInstance* AnimInstance = GetMesh()->GetAnimInstance();
        if (AnimInstance && !AnimInstance->Montage_IsPlaying(AttackMontage))
        {
            AnimInstance->Montage_Play(AttackMontage, 1.f);

            // 绑定蒙太奇结束回调
            FOnMontageEnded EndDelegate;
            EndDelegate.BindUObject(this, &ACombatCharacter::OnAttackEnd);
            AnimInstance->Montage_SetEndDelegate(EndDelegate, AttackMontage);
        }
    }

    UFUNCTION(BlueprintCallable, Category = "Combat")
    void PlayHitReact()
    {
        UAnimInstance* AnimInstance = GetMesh()->GetAnimInstance();
        if (AnimInstance && HitReactMontage)
        {
            AnimInstance->Montage_Play(HitReactMontage, 1.f);
        }
    }

private:
    void OnAttackEnd(UAnimMontage* Montage, bool bInterrupted)
    {
        UE_LOG(LogTemp, Log, TEXT("Attack finished, interrupted: %d"), bInterrupted);
    }
};
```

---

## 四、增强输入系统（Enhanced Input）

```cpp
// UE5 推荐的输入系统
UCLASS()
class AInputCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, Category = "Input")
    UInputMappingContext* DefaultMappingContext;

    UPROPERTY(EditDefaultsOnly, Category = "Input")
    UInputAction* MoveAction;

    UPROPERTY(EditDefaultsOnly, Category = "Input")
    UInputAction* LookAction;

    UPROPERTY(EditDefaultsOnly, Category = "Input")
    UInputAction* JumpAction;

protected:
    virtual void BeginPlay() override
    {
        Super::BeginPlay();

        APlayerController* PC = Cast<APlayerController>(GetController());
        if (PC)
        {
            UEnhancedInputLocalPlayerSubsystem* Subsystem =
                ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(
                    PC->GetLocalPlayer());
            if (Subsystem)
            {
                Subsystem->AddMappingContext(DefaultMappingContext, 0);
            }
        }
    }

    virtual void SetupPlayerInputComponent(UInputComponent* InputComp) override
    {
        Super::SetupPlayerInputComponent(InputComp);

        UEnhancedInputComponent* EnhancedInput =
            Cast<UEnhancedInputComponent>(InputComp);

        if (EnhancedInput)
        {
            EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered,
                this, &AInputCharacter::HandleMove);
            EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered,
                this, &AInputCharacter::HandleLook);
            EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started,
                this, &ACharacter::Jump);
        }
    }

private:
    void HandleMove(const FInputActionValue& Value)
    {
        FVector2D MoveInput = Value.Get<FVector2D>();
        AddMovementInput(GetActorForwardVector(), MoveInput.Y);
        AddMovementInput(GetActorRightVector(), MoveInput.X);
    }

    void HandleLook(const FInputActionValue& Value)
    {
        FVector2D LookInput = Value.Get<FVector2D>();
        AddControllerYawInput(LookInput.X);
        AddControllerPitchInput(LookInput.Y);
    }
};
```

---

## 五、最佳实践

| 实践 | 说明 |
|------|------|
| **C++ 定义框架，Blueprint 实现逻辑** | C++ 负责性能关键路径和数据结构，Blueprint 负责快速迭代 |
| **善用 UPROPERTY 标记** | `EditAnywhere`/`VisibleAnywhere` 控制编辑器可见性 |
| **使用 Gameplay Ability System (GAS)** | 官方技能框架，处理冷却、伤害、效果 |
| **组件化设计** | 使用 ActorComponent 组合功能，避免继承过深 |
| **引用类型用 TSoftObjectPtr** | 避免硬引用导致资源无法卸载 |
| **善用 DataTable 管理数据表** | CSV/JSON 导入，策划友好 |
| **使用 Enhanced Input** | UE5 新输入系统，取代旧的 Action/Axis Mapping |
| **内存管理用 TSharedPtr/TWeakObjectPtr** | 避免野指针和循环引用 |

---

## 六、相关页面

- [[Unity开发入门]] - 对比学习另一主流引擎
- [[游戏设计模式]] - UE 中常用的设计模式
- [[游戏性能优化]] - UE5 性能分析工具与优化技巧
- [[游戏网络同步]] - UE 网络复制（Replication）机制
