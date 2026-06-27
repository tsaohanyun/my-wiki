---
title: Operator开发指南
aliases:
  - Kubernetes Operator
  - Operator开发
  - CRD开发
tags:
  - 云原生
  - Operator
  - Kubernetes
  - CRD
  - Controller
type: 文档
status: 已完成
created: 2024-01-20
updated: 2024-03-20
source: 内部实践
difficulty: 高级
project: AI-Agent
---

# Operator开发指南

## 概述

Kubernetes Operator 是一种将运维知识编码为软件的模式，通过 CRD（Custom Resource Definition）扩展 Kubernetes API，使用 Controller 实现自定义资源的协调循环（Reconcile Loop）。

## CRD 设计

### CRD 定义

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: webapps.example.com
spec:
  group: example.com
  versions:
    - name: v1alpha1
      served: true
      storage: true
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Replicas
          type: integer
          jsonPath: .spec.replicas
        - name: Phase
          type: string
          jsonPath: .status.phase
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
      schema:
        openAPIV3Schema:
          type: object
          description: WebApp is the Schema for the webapps API
          properties:
            apiVersion:
              type: string
            kind:
              type: string
            metadata:
              type: object
            spec:
              description: WebAppSpec defines the desired state of WebApp
              type: object
              required:
                - image
              properties:
                image:
                  type: string
                  description: Container image to deploy
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 100
                  default: 1
                port:
                  type: integer
                  minimum: 1
                  maximum: 65535
                  default: 8080
                env:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      value:
                        type: string
                resources:
                  type: object
                  properties:
                    cpu:
                      type: string
                    memory:
                      type: string
                ingress:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                    host:
                      type: string
                    tlsSecretName:
                      type: string
            status:
              description: WebAppStatus defines the observed state of WebApp
              type: object
              properties:
                phase:
                  type: string
                  enum: [Pending, Creating, Running, Failed]
                replicas:
                  type: integer
                readyReplicas:
                  type: integer
                conditions:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                      status:
                        type: string
                      reason:
                        type: string
                      message:
                        type: string
                      lastTransitionTime:
                        type: string
                        format: date-time
  names:
    kind: WebApp
    listKind: WebAppList
    plural: webapps
    singular: webapp
    shortNames:
      - wa
  scope: Namespaced
```

### CR 示例

```yaml
apiVersion: example.com/v1alpha1
kind: WebApp
metadata:
  name: my-webapp
  namespace: default
spec:
  image: nginx:1.25
  replicas: 3
  port: 8080
  env:
    - name: ENV
      value: production
  resources:
    cpu: "500m"
    memory: "256Mi"
  ingress:
    enabled: true
    host: myapp.example.com
    tlsSecretName: myapp-tls
status:
  phase: Running
  replicas: 3
  readyReplicas: 3
```

## 使用 Kubebuilder 脚手架

```bash
# 初始化项目
mkdir webapp-operator && cd webapp-operator
go mod init github.com/example/webapp-operator

# 初始化 Kubebuilder 项目
kubebuilder init --domain example.com --repo github.com/example/webapp-operator

# 创建 API
kubebuilder create api --group example --version v1alpha1 --kind WebApp

# 生成 CRD 清单
make manifests

# 构建并推送镜像
make docker-build docker-push IMG=registry.example.com/webapp-operator:v0.1.0

# 部署
make deploy IMG=registry.example.com/webapp-operator:v0.1.0
```

## Reconciler 实现

### 核心 Reconcile 逻辑

```go
// controllers/webapp_controller.go
package controllers

import (
    "context"
    "fmt"
    "time"

    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    netv1 "k8s.io/api/networking/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/api/resource"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    "k8s.io/apimachinery/pkg/util/intstr"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    "sigs.k8s.io/controller-runtime/pkg/log"

    examplev1alpha1 "github.com/example/webapp-operator/api/v1alpha1"
)

const webappFinalizer = "example.com/finalizer"

type WebAppReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=example.com,resources=webapps,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=example.com,resources=webapps/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=networking.k8s.io,resources=ingresses,verbs=get;list;watch;create;update;patch;delete

func (r *WebAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    logger := log.FromContext(ctx)

    // 1. 获取 WebApp 实例
    webapp := &examplev1alpha1.WebApp{}
    if err := r.Get(ctx, req.NamespacedName, webapp); err != nil {
        if errors.IsNotFound(err) {
            return ctrl.Result{}, nil
        }
        return ctrl.Result{}, err
    }

    // 2. 处理 Finalizer（清理逻辑）
    if webapp.ObjectMeta.DeletionTimestamp.IsZero() {
        if !controllerutil.ContainsFinalizer(webapp, webappFinalizer) {
            controllerutil.AddFinalizer(webapp, webappFinalizer)
            if err := r.Update(ctx, webapp); err != nil {
                return ctrl.Result{}, err
            }
        }
    } else {
        if controllerutil.ContainsFinalizer(webapp, webappFinalizer) {
            // 执行清理逻辑
            if err := r.cleanupExternalResources(ctx, webapp); err != nil {
                return ctrl.Result{}, err
            }
            controllerutil.RemoveFinalizer(webapp, webappFinalizer)
            if err := r.Update(ctx, webapp); err != nil {
                return ctrl.Result{}, err
            }
        }
        return ctrl.Result{}, nil
    }

    // 3. 协调 Deployment
    if err := r.reconcileDeployment(ctx, webapp); err != nil {
        r.updateStatus(ctx, webapp, examplev1alpha1.PhaseFailed, err.Error())
        return ctrl.Result{RequeueAfter: time.Minute * 2}, err
    }

    // 4. 协调 Service
    if err := r.reconcileService(ctx, webapp); err != nil {
        return ctrl.Result{}, err
    }

    // 5. 协调 Ingress（如果启用）
    if webapp.Spec.Ingress != nil && webapp.Spec.Ingress.Enabled {
        if err := r.reconcileIngress(ctx, webapp); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 6. 更新 Status
    if err := r.updateStatusFromDeployment(ctx, webapp); err != nil {
        return ctrl.Result{}, err
    }

    logger.Info("Reconcile completed", "webapp", req.NamespacedName)
    return ctrl.Result{RequeueAfter: time.Minute * 5}, nil
}

func (r *WebAppReconciler) reconcileDeployment(ctx context.Context, webapp *examplev1alpha1.WebApp) error {
    deploy := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      webapp.Name,
            Namespace: webapp.Namespace,
        },
    }

    _, err := controllerutil.CreateOrUpdate(ctx, r.Client, deploy, func() error {
        replicas := int32(webapp.Spec.Replicas)
        deploy.Spec = appsv1.DeploymentSpec{
            Replicas: &replicas,
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{
                    "app": webapp.Name,
                },
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{"app": webapp.Name},
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{
                        {
                            Name:  "webapp",
                            Image: webapp.Spec.Image,
                            Ports: []corev1.ContainerPort{
                                {ContainerPort: int32(webapp.Spec.Port)},
                            },
                            Env: r.buildEnvVars(webapp.Spec.Env),
                            Resources: corev1.ResourceRequirements{
                                Requests: corev1.ResourceList{
                                    corev1.ResourceCPU:    resource.MustParse(webapp.Spec.Resources.CPU),
                                    corev1.ResourceMemory: resource.MustParse(webapp.Spec.Resources.Memory),
                                },
                            },
                        },
                    },
                },
            },
        }
        return controllerutil.SetControllerReference(webapp, deploy, r.Scheme)
    })

    return err
}

func (r *WebAppReconciler) reconcileService(ctx context.Context, webapp *examplev1alpha1.WebApp) error {
    svc := &corev1.Service{
        ObjectMeta: metav1.ObjectMeta{
            Name:      webapp.Name,
            Namespace: webapp.Namespace,
        },
    }

    _, err := controllerutil.CreateOrUpdate(ctx, r.Client, svc, func() error {
        svc.Spec = corev1.ServiceSpec{
            Selector: map[string]string{"app": webapp.Name},
            Ports: []corev1.ServicePort{
                {
                    Port:       80,
                    TargetPort: intstr.FromInt(int(webapp.Spec.Port)),
                    Protocol:   corev1.ProtocolTCP,
                },
            },
            Type: corev1.ServiceTypeClusterIP,
        }
        return controllerutil.SetControllerReference(webapp, svc, r.Scheme)
    })

    return err
}

func (r *WebAppReconciler) updateStatusFromDeployment(ctx context.Context, webapp *examplev1alpha1.WebApp) error {
    deploy := &appsv1.Deployment{}
    if err := r.Get(ctx, types.NamespacedName{
        Name: webapp.Name, Namespace: webapp.Namespace,
    }, deploy); err != nil {
        return err
    }

    webapp.Status.Replicas = int(deploy.Status.Replicas)
    webapp.Status.ReadyReplicas = int(deploy.Status.ReadyReplicas)

    if deploy.Status.ReadyReplicas == deploy.Status.Replicas {
        webapp.Status.Phase = examplev1alpha1.PhaseRunning
    } else {
        webapp.Status.Phase = examplev1alpha1.PhaseCreating
    }

    return r.Status().Update(ctx, webapp)
}

func (r *WebAppReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&examplev1alpha1.WebApp{}).
        Owns(&appsv1.Deployment{}).
        Owns(&corev1.Service{}).
        Owns(&netv1.Ingress{}).
        Complete(r)
}
```

### Webhook 验证

```go
// api/v1alpha1/webapp_webhook.go
package v1alpha1

import (
    "fmt"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/webhook"
    "sigs.k8s.io/controller-runtime/pkg/webhook/admission"
)

func (r *WebApp) SetupWebhookWithManager(mgr ctrl.Manager) error {
    return ctrl.NewWebhookManagedBy(mgr).For(r).Complete()
}

// +kubebuilder:webhook:path=/mutate-example-com-v1alpha1-webapp,mutating=true,failurePolicy=fail,sideEffects=None,groups=example.com,resources=webapps,verbs=create;update,versions=v1alpha1,name=mwebapp.kb.io,admissionReviewVersions=v1

var _ webhook.Defaulter = &WebApp{}

func (r *WebApp) Default() {
    if r.Spec.Replicas == 0 {
        r.Spec.Replicas = 1
    }
    if r.Spec.Port == 0 {
        r.Spec.Port = 8080
    }
}

// +kubebuilder:webhook:path=/validate-example-com-v1alpha1-webapp,mutating=false,failurePolicy=fail,sideEffects=None,groups=example.com,resources=webapps,verbs=create;update,versions=v1alpha1,name=vwebapp.kb.io,admissionReviewVersions=v1

var _ webhook.Validator = &WebApp{}

func (r *WebApp) ValidateCreate() (admission.Warnings, error) {
    return r.validate()
}

func (r *WebApp) ValidateUpdate(old runtime.Object) (admission.Warnings, error) {
    return r.validate()
}

func (r *WebApp) ValidateDelete() (admission.Warnings, error) {
    return nil, nil
}

func (r *WebApp) validate() (admission.Warnings, error) {
    var warnings admission.Warnings
    if r.Spec.Replicas > 50 {
        warnings = append(warnings, "replicas > 50 may cause high resource usage")
    }
    if r.Spec.Image == "" {
        return warnings, fmt.Errorf("image must not be empty")
    }
    return warnings, nil
}
```

## 测试

### 单元测试

```go
// controllers/webapp_controller_test.go
package controllers

import (
    "context"
    "testing"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
    appsv1 "k8s.io/api/apps/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/types"

    examplev1alpha1 "github.com/example/webapp-operator/api/v1alpha1"
)

var _ = Describe("WebApp Controller", func() {
    Context("When creating a WebApp", func() {
        It("Should create Deployment and Service", func() {
            ctx := context.Background()

            webapp := &examplev1alpha1.WebApp{
                ObjectMeta: metav1.ObjectMeta{
                    Name:      "test-webapp",
                    Namespace: "default",
                },
                Spec: examplev1alpha1.WebAppSpec{
                    Image:    "nginx:1.25",
                    Replicas: 2,
                    Port:     8080,
                },
            }

            Expect(k8sClient.Create(ctx, webapp)).Should(Succeed())

            // 验证 Deployment 创建
            deployLookupKey := types.NamespacedName{
                Name: "test-webapp", Namespace: "default",
            }
            createdDeploy := &appsv1.Deployment{}
            Eventually(func() bool {
                err := k8sClient.Get(ctx, deployLookupKey, createdDeploy)
                return err == nil
            }, time.Minute, time.Second).Should(BeTrue())

            Expect(*createdDeploy.Spec.Replicas).Should(Equal(int32(2)))
        })
    })
})
```

### envtest 配置

```go
// suite_test.go
var _ = BeforeSuite(func() {
    testEnv = &envtest.Environment{
        CRDDirectoryPaths:     []string{filepath.Join("..", "config", "crd", "bases")},
        ErrorIfCRDPathMissing: true,
    }

    cfg, err := testEnv.Start()
    Expect(err).NotTo(HaveOccurred())

    k8sClient, err = client.New(cfg, client.Options{Scheme: scheme.Scheme})
    Expect(err).NotTo(HaveOccurred())
})

var _ = AfterSuite(func() {
    testEnv.Stop()
})
```

## 部署配置

### Operator Deployment

```yaml
# config/manager/manager.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: controller-manager
  namespace: system
  labels:
    control-plane: controller-manager
spec:
  replicas: 1
  selector:
    matchLabels:
      control-plane: controller-manager
  template:
    spec:
      serviceAccountName: controller-manager
      containers:
        - name: manager
          image: registry.example.com/webapp-operator:v0.1.0
          command:
            - /manager
          args:
            - --leader-elect
            - --health-probe-bind-address=:8081
          ports:
            - containerPort: 8081
              name: health
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8081
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8081
          resources:
            limits:
              cpu: 500m
              memory: 128Mi
            requests:
              cpu: 10m
              memory: 64Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
```

## 最佳实践

1. **幂等性**：Reconcile 函数必须是幂等的，重复执行应产生相同结果
2. **最小权限**：RBAC 只配置 Operator 所需的最小权限
3. **Finalizer**：需要清理外部资源时使用 Finalizer
4. **Owner Reference**：子资源通过 OwnerReference 关联，确保级联删除
5. **Status 更新**：只更新 Status 子资源，避免竞争条件
6. **Requeue 策略**：合理设置 RequeueAfter 时间，避免过于频繁的重试
7. **Leader Election**：多副本 Operator 必须启用 Leader Election
8. **Webhook 验证**：使用 Validating/Mutating Webhook 校验 CR
9. **可观测性**：暴露 Prometheus metrics，记录关键事件
10. **渐进式交付**：使用 Conversion Webhook 支持 CRD 多版本演进

## 相关页面

- [[Helm Charts开发]] - 使用 Helm 部署 Operator
- [[服务网格实践]] - Operator 管理服务网格组件
- [[云原生存储]] - Operator 管理存储资源
- [[云原生网络]] - Operator 管理网络配置
