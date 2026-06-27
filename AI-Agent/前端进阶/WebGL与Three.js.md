---
title: WebGL与Three.js
aliases:
  - WebGL 3D开发
  - Three.js实践
tags:
  - WebGL
  - Three.js
  - 3D渲染
  - 模型加载
  - 动画
  - 性能优化
type: 文档
status: 已发布
created: 2026-06-28
updated: 2026-06-28
source: 内部知识库
difficulty: 高级
project: AI-Agent
---

# WebGL与Three.js

WebGL是一种在浏览器中渲染3D图形的API，Three.js是最流行的WebGL封装库，本文介绍3D渲染、模型加载、动画和性能优化等核心概念。

## 1. WebGL基础

### 1.1 WebGL概念

| 概念 | 说明 |
|------|------|
| Canvas | 绘制表面 |
| Context | WebGL上下文 |
| Shader | 着色器程序 |
| Buffer | 数据缓冲区 |
| Texture | 纹理贴图 |
| Framebuffer | 帧缓冲区 |

### 1.2 WebGL基础代码

```javascript
// 初始化WebGL
function initWebGL(canvas) {
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  
  if (!gl) {
    console.error('WebGL not supported');
    return null;
  }
  
  // 设置视口
  gl.viewport(0, 0, canvas.width, canvas.height);
  
  // 设置清屏颜色
  gl.clearColor(0.0, 0.0, 0.0, 1.0);
  
  // 清除颜色缓冲和深度缓冲
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  
  return gl;
}

// 创建着色器
function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error('Shader compile error:', gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  
  return shader;
}

// 创建着色器程序
function createProgram(gl, vertexShader, fragmentShader) {
  const program = gl.createProgram();
  gl.attachShader(program, vertexShader);
  gl.attachShader(program, fragmentShader);
  gl.linkProgram(program);
  
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error('Program link error:', gl.getProgramInfoLog(program));
    gl.deleteProgram(program);
    return null;
  }
  
  return program;
}

// 顶点着色器
const vertexShaderSource = `
  attribute vec4 a_position;
  attribute vec4 a_color;
  
  uniform mat4 u_matrix;
  
  varying vec4 v_color;
  
  void main() {
    gl_Position = u_matrix * a_position;
    v_color = a_color;
  }
`;

// 片元着色器
const fragmentShaderSource = `
  precision mediump float;
  
  varying vec4 v_color;
  
  void main() {
    gl_FragColor = v_color;
  }
`;

// 使用示例
const canvas = document.getElementById('canvas');
const gl = initWebGL(canvas);

const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
const program = createProgram(gl, vertexShader, fragmentShader);

gl.useProgram(program);
```

## 2. Three.js基础

### 2.1 Three.js核心概念

| 概念 | 说明 |
|------|------|
| Scene | 场景，所有对象的容器 |
| Camera | 相机，定义观察视角 |
| Renderer | 渲染器，负责绘制 |
| Mesh | 网格，几何体+材质 |
| Light | 光源 |
| Material | 材质 |
| Geometry | 几何体 |

### 2.2 Three.js基础场景

```javascript
import * as THREE from 'three';

// 创建场景
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb); // 天蓝色背景

// 创建相机
const camera = new THREE.PerspectiveCamera(
  75, // 视野角度
  window.innerWidth / window.innerHeight, // 宽高比
  0.1, // 近裁剪面
  1000 // 远裁剪面
);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);

// 创建渲染器
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// 创建光源
const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
scene.add(directionalLight);

// 创建地面
const groundGeometry = new THREE.PlaneGeometry(20, 20);
const groundMaterial = new THREE.MeshStandardMaterial({
  color: 0x333333,
  roughness: 0.8,
});
const ground = new THREE.Mesh(groundGeometry, groundMaterial);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// 创建立方体
const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
const boxMaterial = new THREE.MeshStandardMaterial({
  color: 0xff6b6b,
  roughness: 0.5,
  metalness: 0.5,
});
const box = new THREE.Mesh(boxGeometry, boxMaterial);
box.position.set(0, 0.5, 0);
box.castShadow = true;
scene.add(box);

// 创建球体
const sphereGeometry = new THREE.SphereGeometry(0.5, 32, 32);
const sphereMaterial = new THREE.MeshStandardMaterial({
  color: 0x4ecdc4,
  roughness: 0.3,
  metalness: 0.7,
});
const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
sphere.position.set(3, 0.5, 0);
sphere.castShadow = true;
scene.add(sphere);

// 添加轨道控制器
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// 动画循环
function animate() {
  requestAnimationFrame(animate);
  
  // 旋转立方体
  box.rotation.x += 0.01;
  box.rotation.y += 0.01;
  
  // 更新控制器
  controls.update();
  
  // 渲染场景
  renderer.render(scene, camera);
}

animate();

// 窗口大小变化处理
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## 3. 模型加载

### 3.1 支持的3D格式

| 格式 | 说明 | 特点 |
|------|------|------|
| glTF/GLB | GL传输格式 | 现代标准，压缩好 |
| FBX | Autodesk格式 | 广泛支持，动画丰富 |
| OBJ | 波前对象格式 | 简单通用，无动画 |
| STL | 立体光刻格式 | 3D打印常用 |
| Collada (.dae) | 数字资产交换 | XML格式，兼容性好 |

### 3.2 GLTF/GLB加载

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

// 创建Draco解码器（用于压缩的glTF）
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/');

// 创建GLTF加载器
const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

// 加载模型
gltfLoader.load(
  'models/character.glb',
  (gltf) => {
    const model = gltf.scene;
    
    // 设置模型属性
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        
        // 优化材质
        if (child.material) {
          child.material.envMapIntensity = 1;
        }
      }
    });
    
    // 调整模型大小和位置
    model.scale.set(0.5, 0.5, 0.5);
    model.position.set(0, 0, 0);
    
    scene.add(model);
    
    // 如果有动画
    if (gltf.animations && gltf.animations.length > 0) {
      setupAnimations(model, gltf.animations);
    }
    
    console.log('Model loaded successfully');
  },
  (progress) => {
    const percent = (progress.loaded / progress.total * 100).toFixed(2);
    console.log(`Loading progress: ${percent}%`);
  },
  (error) => {
    console.error('Error loading model:', error);
  }
);

// 设置动画
function setupAnimations(model, animations) {
  const mixer = new THREE.AnimationMixer(model);
  const actions = {};
  
  animations.forEach((clip) => {
    actions[clip.name] = mixer.clipAction(clip);
  });
  
  // 播放默认动画
  if (actions['Idle']) {
    actions['Idle'].play();
  }
  
  // 动画更新
  const clock = new THREE.Clock();
  function updateAnimation() {
    const delta = clock.getDelta();
    mixer.update(delta);
    requestAnimationFrame(updateAnimation);
  }
  updateAnimation();
  
  return { mixer, actions };
}
```

### 3.3 FBX加载

```javascript
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';

const fbxLoader = new FBXLoader();

fbxLoader.load(
  'models/character.fbx',
  (fbx) => {
    // 调整模型比例（FBX通常需要缩放）
    fbx.scale.set(0.01, 0.01, 0.01);
    
    // 遍历模型
    fbx.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        
        // 修复材质（FBX材质可能需要调整）
        if (child.material) {
          child.material.side = THREE.DoubleSide;
        }
      }
    });
    
    scene.add(fbx);
  },
  (progress) => {
    console.log(`Loading: ${(progress.loaded / progress.total * 100).toFixed(2)}%`);
  },
  (error) => {
    console.error('Error:', error);
  }
);
```

### 3.4 OBJ+MTL加载

```javascript
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';

// 先加载材质
const mtlLoader = new MTLLoader();
mtlLoader.load('models/model.mtl', (materials) => {
  materials.preload();
  
  // 再加载模型
  const objLoader = new OBJLoader();
  objLoader.setMaterials(materials);
  
  objLoader.load(
    'models/model.obj',
    (obj) => {
      obj.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
      
      scene.add(obj);
    },
    (progress) => {
      console.log(`Loading: ${(progress.loaded / progress.total * 100).toFixed(2)}%`);
    },
    (error) => {
      console.error('Error:', error);
    }
  );
});
```

## 4. 动画系统

### 4.1 基础动画

```javascript
// 位置动画
function animatePosition(object, target, duration = 1000) {
  const start = {
    x: object.position.x,
    y: object.position.y,
    z: object.position.z,
  };
  
  const startTime = Date.now();
  
  function update() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 缓动函数（easeInOutCubic）
    const eased = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    object.position.x = start.x + (target.x - start.x) * eased;
    object.position.y = start.y + (target.y - start.y) * eased;
    object.position.z = start.z + (target.z - start.z) * eased;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  update();
}

// 旋转动画
function animateRotation(object, axis, angle, duration = 1000) {
  const startRotation = object.rotation[axis];
  const startTime = Date.now();
  
  function update() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    object.rotation[axis] = startRotation + angle * progress;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  update();
}

// 缩放动画
function animateScale(object, targetScale, duration = 1000) {
  const startScale = {
    x: object.scale.x,
    y: object.scale.y,
    z: object.scale.z,
  };
  
  const startTime = Date.now();
  
  function update() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    object.scale.x = startScale.x + (targetScale.x - startScale.x) * progress;
    object.scale.y = startScale.y + (targetScale.y - startScale.y) * progress;
    object.scale.z = startScale.z + (targetScale.z - startScale.z) * progress;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  update();
}
```

### 4.2 GSAP动画库

```javascript
import gsap from 'gsap';

// 位置动画
gsap.to(box.position, {
  x: 5,
  y: 2,
  z: 0,
  duration: 2,
  ease: 'power2.inOut',
  onComplete: () => {
    console.log('Animation complete');
  },
});

// 旋转动画
gsap.to(box.rotation, {
  y: Math.PI * 2,
  duration: 3,
  ease: 'none',
  repeat: -1, // 无限循环
});

// 缩放动画
gsap.fromTo(
  box.scale,
  { x: 0, y: 0, z: 0 },
  {
    x: 1,
    y: 1,
    z: 1,
    duration: 1,
    ease: 'back.out(1.7)',
  }
);

// 材质动画
gsap.to(box.material.color, {
  r: 0,
  g: 1,
  b: 0,
  duration: 2,
});

// 动画时间线
const timeline = gsap.timeline();

timeline
  .to(box.position, { x: 3, duration: 1 })
  .to(box.position, { y: 2, duration: 1 }, '-=0.5') // 提前0.5秒开始
  .to(box.rotation, { y: Math.PI * 2, duration: 2 })
  .to(box.scale, { x: 2, y: 2, z: 2, duration: 1 });

// 控制动画
timeline.pause();
timeline.play();
timeline.reverse();
timeline.timeScale(2); // 2倍速
```

### 4.3 骨骼动画

```javascript
// 骨骼动画系统
class SkeletonAnimation {
  constructor(model) {
    this.model = model;
    this.mixer = null;
    this.actions = {};
    this.currentAction = null;
  }

  // 初始化动画
  init(animations) {
    this.mixer = new THREE.AnimationMixer(this.model);
    
    animations.forEach((clip) => {
      this.actions[clip.name] = this.mixer.clipAction(clip);
    });
  }

  // 播放动画
  play(name, options = {}) {
    const { loop = true, crossFadeDuration = 0.3 } = options;
    
    const newAction = this.actions[name];
    if (!newAction) {
      console.warn(`Animation not found: ${name}`);
      return;
    }
    
    // 设置循环
    newAction.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce);
    newAction.clampWhenFinished = !loop;
    
    // 交叉淡入淡出
    if (this.currentAction && this.currentAction !== newAction) {
      newAction.reset();
      newAction.play();
      this.currentAction.crossFadeTo(newAction, crossFadeDuration);
    } else {
      newAction.play();
    }
    
    this.currentAction = newAction;
  }

  // 停止动画
  stop(name) {
    if (name) {
      this.actions[name]?.stop();
    } else {
      Object.values(this.actions).forEach(action => action.stop());
    }
  }

  // 更新动画
  update(delta) {
    this.mixer?.update(delta);
  }

  // 获取动画列表
  getAnimationNames() {
    return Object.keys(this.actions);
  }
}

// 使用示例
const skeletonAnim = new SkeletonAnimation(model);
skeletonAnim.init(gltf.animations);

// 播放动画
skeletonAnim.play('Walk');
skeletonAnim.play('Run', { crossFadeDuration: 0.5 });
```

### 4.4 变形动画

```javascript
// 变形动画（Morph Targets）
class MorphAnimation {
  constructor(mesh) {
    this.mesh = mesh;
    this.morphTargets = mesh.morphTargetDictionary;
    this.morphInfluences = mesh.morphTargetInfluences;
  }

  // 设置变形权重
  setWeight(name, value) {
    const index = this.morphTargets[name];
    if (index !== undefined) {
      this.morphInfluences[index] = value;
    }
  }

  // 获取变形权重
  getWeight(name) {
    const index = this.morphTargets[name];
    return index !== undefined ? this.morphInfluences[index] : 0;
  }

  // 动画变形
  animateMorph(name, targetWeight, duration = 1000) {
    const startWeight = this.getWeight(name);
    const startTime = Date.now();

    const update = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      this.setWeight(name, startWeight + (targetWeight - startWeight) * progress);
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };

    update();
  }

  // 获取所有变形目标
  getMorphTargets() {
    return Object.keys(this.morphTargets);
  }
}

// 使用示例
const morphAnim = new MorphAnimation(faceMesh);
morphAnim.setWeight('smile', 1.0);
morphAnim.animateMorph('blink', 1.0, 200);
```

## 5. 性能优化

### 5.1 渲染优化

```javascript
// 1. 使用LOD（Level of Detail）
class LODManager {
  constructor(camera) {
    this.camera = camera;
    this.objects = [];
  }

  addObject(object, distances) {
    // distances: [{ distance: 10, detail: 'high' }, { distance: 50, detail: 'medium' }, ...]
    this.objects.push({ object, distances });
  }

  update() {
    this.objects.forEach(({ object, distances }) => {
      const cameraDistance = this.camera.position.distanceTo(object.position);
      
      // 根据距离调整细节
      for (const { distance, detail } of distances) {
        if (cameraDistance < distance) {
          this.setDetail(object, detail);
          break;
        }
      }
    });
  }

  setDetail(object, detail) {
    // 根据细节级别调整模型
    object.traverse((child) => {
      if (child.isMesh) {
        switch (detail) {
          case 'high':
            child.visible = true;
            child.material.wireframe = false;
            break;
          case 'medium':
            child.visible = true;
            child.material.wireframe = false;
            break;
          case 'low':
            child.visible = true;
            child.material.wireframe = true;
            break;
          case 'none':
            child.visible = false;
            break;
        }
      }
    });
  }
}

// 2. 使用InstancedMesh
function createInstancedMesh(geometry, material, count) {
  const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
  
  const matrix = new THREE.Matrix4();
  const position = new THREE.Vector3();
  const rotation = new THREE.Euler();
  const scale = new THREE.Vector3(1, 1, 1);
  
  for (let i = 0; i < count; i++) {
    position.set(
      Math.random() * 100 - 50,
      Math.random() * 100 - 50,
      Math.random() * 100 - 50
    );
    
    rotation.set(
      Math.random() * Math.PI,
      Math.random() * Math.PI,
      Math.random() * Math.PI
    );
    
    matrix.compose(position, new THREE.Quaternion().setFromEuler(rotation), scale);
    instancedMesh.setMatrixAt(i, matrix);
  }
  
  instancedMesh.instanceMatrix.needsUpdate = true;
  return instancedMesh;
}

// 3. 使用几何体合并
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

function mergeMeshes(meshes) {
  const geometries = meshes.map(mesh => {
    const geo = mesh.geometry.clone();
    geo.applyMatrix4(mesh.matrixWorld);
    return geo;
  });
  
  const mergedGeometry = mergeGeometries(geometries);
  const material = meshes[0].material;
  
  return new THREE.Mesh(mergedGeometry, material);
}
```

### 5.2 内存优化

```javascript
// 1. 纹理优化
class TextureOptimizer {
  constructor(renderer) {
    this.renderer = renderer;
    this.textureCache = new Map();
  }

  // 加载优化纹理
  loadTexture(url, options = {}) {
    const {
      maxSize = 1024,
      format = 'webp',
      quality = 0.8,
    } = options;

    // 检查缓存
    if (this.textureCache.has(url)) {
      return this.textureCache.get(url);
    }

    const loader = new THREE.TextureLoader();
    
    return new Promise((resolve, reject) => {
      loader.load(
        url,
        (texture) => {
          // 调整纹理大小
          if (texture.image.width > maxSize || texture.image.height > maxSize) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            const ratio = Math.min(maxSize / texture.image.width, maxSize / texture.image.height);
            canvas.width = texture.image.width * ratio;
            canvas.height = texture.image.height * ratio;
            
            ctx.drawImage(texture.image, 0, 0, canvas.width, canvas.height);
            
            texture.image = canvas;
          }

          // 设置纹理参数
          texture.minFilter = THREE.LinearMipmapLinearFilter;
          texture.magFilter = THREE.LinearFilter;
          texture.anisotropy = Math.min(4, this.renderer.capabilities.getMaxAnisotropy());
          texture.generateMipmaps = true;
          
          this.textureCache.set(url, texture);
          resolve(texture);
        },
        undefined,
        reject
      );
    });
  }

  // 释放纹理
  disposeTexture(url) {
    const texture = this.textureCache.get(url);
    if (texture) {
      texture.dispose();
      this.textureCache.delete(url);
    }
  }
}

// 2. 几何体优化
class GeometryOptimizer {
  // 简化几何体
  static simplify(geometry, ratio = 0.5) {
    // 使用SimplifierModifier
    const modifier = new THREE.SimplifyModifier();
    const simplified = modifier.modify(geometry, geometry.attributes.position.count * ratio);
    return simplified;
  }

  // 合并顶点
  static mergeVertices(geometry) {
    return THREE.BufferGeometryUtils.mergeVertices(geometry);
  }

  // 计算包围盒
  static computeBoundingBox(geometry) {
    geometry.computeBoundingBox();
    return geometry.boundingBox;
  }
}

// 3. 材质优化
class MaterialOptimizer {
  // 创建共享材质
  static createSharedMaterial(options) {
    return new THREE.MeshStandardMaterial({
      ...options,
      // 优化设置
      precision: 'mediump',
      flatShading: false,
    });
  }

  // 材质实例化
  static instantiateMaterial(material) {
    const newMaterial = material.clone();
    newMaterial.needsUpdate = true;
    return newMaterial;
  }
}
```

### 5.3 场景优化

```javascript
// 1. 视锥体剔除
class FrustumCuller {
  constructor(camera) {
    this.camera = camera;
    this.frustum = new THREE.Frustum();
    this.projScreenMatrix = new THREE.Matrix4();
  }

  update() {
    this.projScreenMatrix.multiplyMatrices(
      this.camera.projectionMatrix,
      this.camera.matrixWorldInverse
    );
    this.frustum.setFromProjectionMatrix(this.projScreenMatrix);
  }

  isVisible(object) {
    if (!object.geometry) return true;
    
    if (!object.geometry.boundingSphere) {
      object.geometry.computeBoundingSphere();
    }
    
    const sphere = object.geometry.boundingSphere.clone();
    sphere.applyMatrix4(object.matrixWorld);
    
    return this.frustum.intersectsSphere(sphere);
  }

  cull(scene) {
    scene.traverse((object) => {
      if (object.isMesh) {
        object.visible = this.isVisible(object);
      }
    });
  }
}

// 2. 遮挡剔除
class OcclusionCuller {
  constructor(renderer, camera) {
    this.renderer = renderer;
    this.camera = camera;
    this.occlusionMap = new Map();
  }

  // 使用GPU遮挡查询
  async checkOcclusion(object) {
    const gl = this.renderer.getContext();
    const query = gl.createQuery();
    
    gl.beginQuery(gl.ANY_SAMPLES_PASSED_CONSERVATIVE, query);
    
    // 渲染对象的包围盒
    this.renderBoundingBox(object);
    
    gl.endQuery(gl.ANY_SAMPLES_PASSED_CONSERVATIVE);
    
    // 等待结果
    const available = gl.getQueryParameter(query, gl.QUERY_RESULT_AVAILABLE);
    if (available) {
      const visible = gl.getQueryParameter(query, gl.QUERY_RESULT);
      return visible > 0;
    }
    
    return true; // 默认可见
  }

  renderBoundingBox(object) {
    // 渲染包围盒逻辑...
  }
}

// 3. 场景分块
class SceneChunking {
  constructor(scene, chunkSize = 100) {
    this.scene = scene;
    this.chunkSize = chunkSize;
    this.chunks = new Map();
  }

  // 添加对象到分块
  addObject(object) {
    const chunkKey = this.getChunkKey(object.position);
    
    if (!this.chunks.has(chunkKey)) {
      this.chunks.set(chunkKey, []);
    }
    
    this.chunks.get(chunkKey).push(object);
  }

  // 获取可见分块
  getVisibleChunks(camera) {
    const visibleChunks = [];
    const cameraPosition = camera.position;
    
    this.chunks.forEach((objects, key) => {
      const [x, z] = key.split(',').map(Number);
      const distance = Math.sqrt(
        Math.pow(cameraPosition.x - x * this.chunkSize, 2) +
        Math.pow(cameraPosition.z - z * this.chunkSize, 2)
      );
      
      // 只加载距离内的分块
      if (distance < this.chunkSize * 3) {
        visibleChunks.push(key);
      }
    });
    
    return visibleChunks;
  }

  // 获取分块Key
  getChunkKey(position) {
    const x = Math.floor(position.x / this.chunkSize);
    const z = Math.floor(position.z / this.chunkSize);
    return `${x},${z}`;
  }
}
```

## 6. 最佳实践

### 6.1 性能优化最佳实践
1. **减少Draw Call**：使用InstancedMesh和几何体合并
2. **纹理优化**：使用合适的纹理格式和大小
3. **LOD使用**：根据距离调整模型细节
4. **视锥体剔除**：只渲染可见对象
5. **内存管理**：及时释放不用的资源

### 6.2 加载优化最佳实践
1. **预加载**：提前加载常用资源
2. **懒加载**：按需加载远处资源
3. **压缩资源**：使用Draco压缩glTF
4. **缓存策略**：合理使用缓存

### 6.3 渲染质量最佳实践
1. **抗锯齿**：开启抗锯齿提升画质
2. **阴影优化**：合理设置阴影参数
3. **后处理**：使用后处理效果提升视觉效果
4. **光照优化**：合理设置光源数量和类型

### 6.4 开发调试最佳实践
1. **性能监控**：使用stats.js监控帧率
2. **场景调试**：使用dat.GUI调整参数
3. **错误处理**：添加错误边界和降级方案
4. **兼容性测试**：测试不同设备和浏览器

## 7. 常见问题

### Q1: Three.js性能差怎么办？
**A**: 
1. 减少Draw Call
2. 使用LOD和视锥体剔除
3. 优化纹理和材质
4. 使用Web Worker处理计算

### Q2: 如何处理大模型加载？
**A**: 
1. 使用glTF格式和Draco压缩
2. 分块加载和懒加载
3. 使用LOD多级模型
4. 优化模型拓扑结构

### Q3: 如何实现物理效果？
**A**: 
1. 使用Cannon.js或Ammo.js
2. 简化碰撞体形状
3. 使用物理世界步进
4. 合理设置物理参数

## 8. 相关页面

- [前端工程化](前端工程化.md)
- [微前端架构](微前端架构.md)
- [前端监控体系](前端监控体系.md)
- [低代码平台设计](低代码平台设计.md)

## 9. 参考资料

- [Three.js官方文档](https://threejs.org/docs/)
- [WebGL基础教程](https://webglfundamentals.org/)
- [Three.js示例](https://threejs.org/examples/)
- [glTF格式规范](https://www.khronos.org/gltf/)
- [Three.js性能优化](https://discoverthreejs.com/tips-and-tricks/)