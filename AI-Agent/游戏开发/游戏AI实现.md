---
title: 游戏AI实现
aliases: [游戏AI, A*寻路, 行为树, NavMesh]
tags: [game, ai, pathfinding, behavior-tree]
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: 实践经验
difficulty: advanced
project: 游戏开发
---
# 游戏 AI 实现

## 概述

本指南涵盖游戏中常用的AI技术：寻路、行为树、状态机和群体AI。

## 1. A*寻路算法

### Python实现

```python
import heapq

def astar(grid, start, goal):
    """A*寻路算法"""
    rows, cols = len(grid), len(grid[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def neighbors(node):
        r, c = node
        result = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                result.append((nr, nc))
        return result
    
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for neighbor in neighbors(current):
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None  # 无路径

# 使用
grid = [
    [0,0,0,0,0],
    [0,1,1,0,0],
    [0,0,0,0,1],
    [0,1,0,0,0],
    [0,0,0,1,0]
]
path = astar(grid, (0,0), (4,4))
print(f"路径: {path}")
```

## 2. 有限状态机（FSM）

```python
from enum import Enum

class State(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"

class EnemyAI:
    def __init__(self):
        self.state = State.IDLE
        self.health = 100
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
    
    def update(self, delta_time):
        # 状态转换
        if self.state == State.IDLE:
            if self.can_see_player():
                self.state = State.CHASE
            else:
                self.state = State.PATROL
        
        elif self.state == State.PATROL:
            if self.can_see_player():
                self.state = State.CHASE
            else:
                self.patrol()
        
        elif self.state == State.CHASE:
            if self.in_attack_range():
                self.state = State.ATTACK
            elif not self.can_see_player():
                self.state = State.PATROL
            elif self.health < 30:
                self.state = State.FLEE
            else:
                self.move_toward(self.target)
        
        elif self.state == State.ATTACK:
            if not self.in_attack_range():
                self.state = State.CHASE
            else:
                self.attack()
        
        elif self.state == State.FLEE:
            if self.health > 60:
                self.state = State.CHASE
            else:
                self.move_away_from(self.target)
    
    def can_see_player(self):
        # 视线检测逻辑
        pass
    
    def in_attack_range(self):
        # 攻击距离检测
        pass
```

## 3. 行为树（Behavior Tree）

```python
from enum import Enum

class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class BTNode:
    def execute(self, context):
        return NodeStatus.FAILURE

class SequenceNode(BTNode):
    """顺序节点：依次执行子节点，全部成功才成功"""
    def __init__(self, children=None):
        self.children = children or []
    
    def execute(self, context):
        for child in self.children:
            status = child.execute(context)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS

class SelectorNode(BTNode):
    """选择节点：依次执行子节点，任一成功即成功"""
    def __init__(self, children=None):
        self.children = children or []
    
    def execute(self, context):
        for child in self.children:
            status = child.execute(context)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE

class ActionNode(BTNode):
    def __init__(self, action_func):
        self.action = action_func
    
    def execute(self, context):
        return self.action(context)

class ConditionNode(BTNode):
    def __init__(self, condition_func):
        self.condition = condition_func
    
    def execute(self, context):
        return NodeStatus.SUCCESS if self.condition(context) else NodeStatus.FAILURE

# 构建行为树
def build_enemy_bt():
    return SelectorNode([
        # 优先：攻击
        SequenceNode([
            ConditionNode(lambda ctx: ctx.in_attack_range()),
            ActionNode(lambda ctx: ctx.attack()),
        ]),
        # 其次：追击
        SequenceNode([
            ConditionNode(lambda ctx: ctx.can_see_player()),
            ActionNode(lambda ctx: ctx.chase()),
        ]),
        # 最后：巡逻
        ActionNode(lambda ctx: ctx.patrol()),
    ])
```

## 4. NavMesh导航

```csharp
// Unity NavMesh示例
using UnityEngine;
using UnityEngine.AI;

public class EnemyNavigation : MonoBehaviour
{
    private NavMeshAgent agent;
    public Transform target;
    public float detectionRange = 10f;
    
    void Start()
    {
        agent = GetComponent<NavMeshAgent>();
    }
    
    void Update()
    {
        float distance = Vector3.Distance(transform.position, target.position);
        
        if (distance <= detectionRange)
        {
            agent.SetDestination(target.position);
        }
        else
        {
            // 随机巡逻
            if (!agent.hasPath)
            {
                Vector3 randomPoint = GetRandomPoint();
                agent.SetDestination(randomPoint);
            }
        }
    }
    
    Vector3 GetRandomPoint()
    {
        Vector3 randomDir = Random.insideUnitSphere * 10f;
        randomDir += transform.position;
        NavMeshHit hit;
        NavMesh.SamplePosition(randomDir, out hit, 10f, NavMesh.AllAreas);
        return hit.position;
    }
}
```

## 5. 群体AI（Flocking）

```python
import numpy as np

class Boid:
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.random.randn(2) * 2
        self.acceleration = np.zeros(2)
    
    def flock(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohere(boids)
        separation = self.separate(boids)
        
        self.acceleration = alignment + cohesion + separation
    
    def align(self, boids, perception_radius=50):
        steering = np.zeros(2)
        total = 0
        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if other != self and d < perception_radius:
                steering += other.velocity
                total += 1
        if total > 0:
            steering /= total
            steering = steering - self.velocity
        return steering
    
    def cohere(self, boids, perception_radius=50):
        steering = np.zeros(2)
        total = 0
        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if other != self and d < perception_radius:
                steering += other.position
                total += 1
        if total > 0:
            steering /= total
            steering = steering - self.position
        return steering
    
    def separate(self, boids, separation_radius=25):
        steering = np.zeros(2)
        total = 0
        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if other != self and d < separation_radius and d > 0:
                diff = self.position - other.position
                diff /= d * d  # 距离越远影响越小
                steering += diff
                total += 1
        if total > 0:
            steering /= total
        return steering
    
    def update(self, max_speed=4, max_force=0.1):
        self.velocity += self.acceleration
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = self.velocity / speed * max_speed
        self.position += self.velocity
        self.acceleration = np.zeros(2)
```

## 相关页面

- [[Unity开发入门]]
- [[游戏设计模式]]
- [[游戏服务器架构]]
- [[Godot引擎开发]]
