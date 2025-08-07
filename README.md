# kubeflow 설치 준비

1. helm cert-manager 설치

```shell
helm repo add jetstack https://charts.jetstack.io
helm repo update

kubectl create namespace cert-manager

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.18.2 \
  --set installCRDs=true
```

2. kubeflow-issuer ClusterIssuer 생성

Self signed
```shell
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: kubeflow-selfsigned
spec:
  selfSigned: {}
```

// kubeflow-issuer.yaml
```shell
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: kubeflow-issuer
spec:
  acme:
    email: admin@neworo.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: kubeflow-issuer-key
    solvers:
    - http01:
        ingress:
          class: istio
```
적용
```shell
kubectl apply -f kubeflow-issuer.yaml
```

3. k8s g/w용 인증서 요청
```shell
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: kubeflow-tls
  namespace: istio-system
spec:
  secretName: kubeflow-tls
  dnsNames:
  - "kubeflow.local"  # 내부 로컬용
  issuerRef:
    name: kubeflow-selfsigned
    kind: ClusterIssuer
```
---
## Istio 설치
```shell
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.26.*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=default -y
```

베어메탈인 경우,
```shell
kubectl patch svc istio-ingressgateway -n istio-system \
  -p '{"spec": {"type": "NodePort"}}'
```

자동주입
```shell
kubectl label namespace kubeflow istio-injection=enabled
```
---
## kustomize 설치

리눅스버전
```shell
curl -s "https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest" \
  | grep browser_download_url \
  | grep linux_amd64 \
  | cut -d '"' -f 4 \
  | xargs curl -L -o kustomize.tar.gz

tar -xzf kustomize.tar.gz
chmod +x kustomize
sudo mv kustomize /usr/local/bin/
```
---
Dex
oauth2-proxy
kubeflow-namespace
kubeflow-roles
kubeflow-istio-resources
```shell
git clone -b v1.10.2 https://github.com/kubeflow/manifests.git
cd manifests
kustomize build common/cert-manager/base | kubectl apply -f - 
kustomize build common/cert-manager/kubeflow-issuer/base | kubectl apply -f -

kustomize build common/istio/istio-crds/base | kubectl apply -f -
kustomize build common/istio/istio-namespace/base | kubectl apply -f -
kustomize build common/istio/istio-install/base | kubectl apply -f -
kustomize build common/istio/istio-install/overlays/oauth2-proxy \
  | kubectl apply -f -

kustomize build common/dex/overlays/istio | kubectl apply -f -

kustomize build common/oauth2-proxy/base | kubectl apply -f -

kustomize build common/kubeflow-namespace/base | kubectl apply -f -
kustomize build common/kubeflow-roles/base | kubectl apply -f -

kustomize build common/istio/kubeflow-istio-resources/base | kubectl apply -f - 

kustomize build applications/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user | kubectl apply -f -

kustomize build applications/katib/upstream/installs/katib-with-kubeflow | kubectl apply -f -

kustomize build applications/centraldashboard/upstream/overlays/istio | kubectl apply -f -


#pod 생성 안되는 이슈
kubectl label namespace kubeflow pod-security.kubernetes.io/enforce=privileged --overwrite
kubectl label namespace kubeflow pod-security.kubernetes.io/audit=privileged --overwrite
kubectl label namespace kubeflow pod-security.kubernetes.io/warn=privileged --overwrite

kustomize build applications/admission-webhook/upstream/overlays/cert-manager | kubectl apply -f -

kustomize build applications/jupyter/notebook-controller/upstream/overlays/kubeflow | kubectl apply -f -

kustomize build applications/jupyter/jupyter-web-app/upstream/overlays/istio | kubectl apply -f -

kustomize build applications/profiles/upstream/overlays/kubeflow | kubectl apply -f -

kustomize build applications/volumes-web-app/upstream/overlays/istio | kubectl apply -f -

kustomize build applications/tensorboard/tensorboards-web-app/upstream/overlays/istio | kubectl apply -f -
kustomize build applications/tensorboard/tensorboard-controller/upstream/overlays/kubeflow | kubectl apply -f -

kustomize build applications/training-operator/upstream/overlays/kubeflow | kubectl apply -f - 

kustomize build common/user-namespace/base | kubectl apply -f -

kustomize build common/oauth2-proxy/overlays/m2m-dex-only \
  | kubectl apply -f -
```
# kubeflow dashboard ui
kubeflow dashboard ui를 위한 포트포워딩
```shell
 kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80
 #이후 localhost:8080접속
 ```

# 수행
```shell
python3 5.pipeline.py
```

