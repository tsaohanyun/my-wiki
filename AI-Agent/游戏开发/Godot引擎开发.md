---
title: Godot引擎开发
aliases: [Godot, Godot开发, GDScript]
tags: [game, godot, engine]
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: 实践经验
difficulty: intermediate
project: 游戏开发
---
# Godot 引擎开发

## 概述

Godot是开源免费的跨平台游戏引擎，支持2D和3D开发。

## 1. 节点系统

### 核心节点类型

```gdscript
# Node2D - 2D基础节点
# Sprite2D - 精灵渲染
# CharacterBody2D - 角色控制器
# RigidBody2D - 物理刚体
# Area2D - 触发区域

extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta):
    if not is_on_floor():
        velocity.y += gravity * delta
    
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    var direction = Input.get_axis("ui_left", "ui_right")
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
    
    move_and_slide()
```

### 场景树

```
GameScene (Node2D)
├── Player (CharacterBody2D)
│   ├── Sprite (Sprite2D)
│   ├── CollisionShape (CollisionShape2D)
│   └── Camera (Camera2D)
├── TileMap (TileMap)
├── Enemies (Node2D)
│   ├── Enemy1 (CharacterBody2D)
│   └── Enemy2 (CharacterBody2D)
└── UI (CanvasLayer)
    ├── ScoreLabel (Label)
    └── HealthBar (ProgressBar)
```

## 2. GDScript基础

### 信号系统

```gdscript
# 定义信号
signal health_changed(new_health: int)
signal player_died

var health: int = 100

func take_damage(amount: int):
    health -= amount
    health_changed.emit(health)
    if health <= 0:
        player_died.emit()

# 连接信号
func _ready():
    player.health_changed.connect(_on_health_changed)
    player.player_died.connect(_on_player_died)

func _on_health_changed(new_health: int):
    health_bar.value = new_health

func _on_player_died():
    get_tree().reload_current_scene()
```

## 3. 物理与碰撞

```gdscript
# 碰撞层和掩码
func _ready():
    # 设置碰撞层（第1层=玩家）
    collision_layer = 1
    # 设置碰撞掩码（检测第2层=敌人）
    collision_mask = 2

# Area2D检测
func _on_area_body_entered(body):
    if body.is_in_group("enemies"):
        take_damage(body.damage)

# RayCast射线检测
var ray = $RayCast2D
if ray.is_colliding():
    var collider = ray.get_collider()
```

## 4. 动画系统

```gdscript
# AnimationPlayer
var anim_player = $AnimationPlayer

func _ready():
    anim_player.play("idle")

func _process(delta):
    if velocity.length() > 0:
        anim_player.play("walk")
    else:
        anim_player.play("idle")

# 程序化动画（Tween）
func jump_animation():
    var tween = create_tween()
    tween.tween_property(self, "scale", Vector2(1.2, 0.8), 0.1)
    tween.tween_property(self, "scale", Vector2(1.0, 1.0), 0.1)
```

## 5. 资源管理

```gdscript
# 动态加载资源
var texture = load("res://assets/player.png")
var scene = load("res://scenes/enemy.tscn")

# 预加载
const EnemyScene = preload("res://scenes/enemy.tscn")

func spawn_enemy():
    var enemy = EnemyScene.instantiate()
    enemy.position = Vector2(100, 200)
    add_child(enemy)

# 资源池
var bullet_pool: Array = []

func get_bullet():
    for bullet in bullet_pool:
        if not bullet.visible:
            return bullet
    var new_bullet = BulletScene.instantiate()
    bullet_pool.append(new_bullet)
    return new_bullet
```

## 相关页面

- [[Unity开发入门]]
- [[Unreal Engine基础]]
- [[游戏设计模式]]
- [[游戏性能优化]]
