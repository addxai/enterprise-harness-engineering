---
name: k8s-ops
description: Manage Kubernetes cluster resources via kubectl. Use when user needs to view, troubleshoot, or modify K8s workloads across multiple clusters.
---

# k8s-ops

Assists operations engineers in managing K8s cluster resources via kubectl. Supports viewing, troubleshooting, and change operations.

**Applicable scenarios:**

- View Pod/Deployment/Service/Node and other resource statuses
- View logs and events for troubleshooting
- Execute change operations (scale, rollout restart, apply, etc.)
- Troubleshooting operations (exec, port-forward, describe, etc.)

## Setup

Before using this skill, configure your cluster contexts in the table below. Replace the example entries with your actual clusters:

| Cluster | Context | Cloud Provider | k8s Repo Directory |
|---------|---------|---------------|-------------------|
| prod-1  | `your-eks-context-here` | AWS EKS | `clusters/prod-1/` |
| staging | `your-gke-context-here` | GCP GKE | `clusters/staging/` |
| dev     | `your-aks-context-here` | Azure AKS | `clusters/dev/` |

> Add all clusters your team manages. The context value should match the output of `kubectl config get-contexts`.

## Execution Flow

### Step 1: Environment Check

On first operation, the Agent should automatically check the environment:

1. Run `kubectl version --client` to confirm kubectl is installed
2. Run `kubectl config get-contexts` to list configured contexts

**If kubectl is not installed**: Guide the user to install it (`brew install kubectl` / `apt install kubectl` / official documentation).

**If the target context is not configured**:
- AWS EKS clusters: Guide the user to run `aws eks update-kubeconfig --name <cluster-name> --region <region>`
- GCP GKE clusters: Guide the user to run `gcloud container clusters get-credentials <cluster-name> --region <region> --project <project>`, and ensure `gke-gcloud-auth-plugin` is installed
- Azure AKS clusters: Guide the user to run `az aks get-credentials --resource-group <rg> --name <cluster-name>`
- Other clusters: Guide the user to download kubeconfig through the corresponding cloud platform console

**If already configured**: Proceed directly to Step 2.

### Step 2: Confirm Operation Target

Confirm the following information with the user (proactively ask if not provided):

1. **Target cluster**: Match the cluster table above based on the user's description; determine the context
2. **Target namespace**: Use `default` if not specified, or infer from the service name
3. **Operation content**: View, change, troubleshoot, etc.

### Step 3: Switch Context

Use the `--context` parameter to specify the cluster — **do not modify the current default context**:

```bash
kubectl --context <context-name> -n <namespace> <command>
```

### Step 4: Execute Operation

#### View Operations (execute directly)

View operations carry no risk and can be executed directly:

```bash
# View Pod status
kubectl --context <ctx> -n <ns> get pods

# View Deployments
kubectl --context <ctx> -n <ns> get deployments

# View Pod logs
kubectl --context <ctx> -n <ns> logs <pod-name> --tail=100

# View events
kubectl --context <ctx> -n <ns> get events --sort-by='.lastTimestamp'

# View resource details
kubectl --context <ctx> -n <ns> describe pod <pod-name>

# View Node status
kubectl --context <ctx> get nodes

# View resource usage
kubectl --context <ctx> -n <ns> top pods
```

#### Change Operations (must confirm first)

**All change operations must show the user the command to be executed; execution only after user confirmation.**

```bash
# Scale
kubectl --context <ctx> -n <ns> scale deployment <name> --replicas=<N>

# Rolling restart
kubectl --context <ctx> -n <ns> rollout restart deployment <name>

# Apply configuration
kubectl --context <ctx> -n <ns> apply -f <file>

# Edit ConfigMap
kubectl --context <ctx> -n <ns> edit configmap <name>

# Delete resource (high risk)
kubectl --context <ctx> -n <ns> delete <resource> <name>
```

#### Troubleshooting Operations

```bash
# Enter a container
kubectl --context <ctx> -n <ns> exec -it <pod-name> -- /bin/sh

# Port forwarding
kubectl --context <ctx> -n <ns> port-forward <pod-name> <local>:<remote>

# View all containers in a Pod
kubectl --context <ctx> -n <ns> get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

### Step 5: Confirm Results

- **View operations**: Display output directly; format or summarize as needed
- **Change operations**: Verify results after execution (e.g., check Pod count after scale, check rollout status after restart)
- **On failure**: Display error information, analyze the cause, and suggest a fix

## Security Rules

1. **Prohibit executing `delete namespace` on prod clusters**
2. **Prohibit executing `kubectl drain` unless the user explicitly requests and confirms**
3. **All change operations must show the complete command before execution and wait for user confirmation**
4. **Batch operations (e.g., scaling multiple deployments simultaneously) must list each one and confirm**
5. **Prefer using `--context` parameter to specify the cluster; avoid `kubectl config use-context` which modifies global state**

## Examples

### Bad

#### 1. Executing changes without confirmation

```
User: Help me restart payment-service on Production
AI: Rolling restart executed.
```

**Problem**: Change operation executed without user confirmation.

#### 2. Modifying global context

```bash
kubectl config use-context my-prod-context
kubectl -n prod get pods
```

**Problem**: Modified the global context, potentially affecting the user's other terminal sessions. Should use the `--context` parameter.

#### 3. Executing high-risk operations on prod without confirmation

```bash
kubectl --context my-prod-context delete namespace monitoring
```

**Problem**: Deleting an entire namespace on a production cluster without confirmation.

### Good

#### 1. Confirming before changes

```
User: Help me restart payment-service on Prod

AI: I will execute the following on the Prod cluster:
    - Cluster: prod-1 (my-prod-context)
    - Namespace: prod
    - Command: kubectl --context my-prod-context -n prod rollout restart deployment payment-service

    Confirm execution?

User: Confirmed

AI: Executed. Checking rollout status...
    deployment "payment-service" successfully rolled out
```

#### 2. Guiding configuration after environment check

```
User: Help me check the Pod status on Staging

AI: Let me check the kubectl environment...
    kubectl is installed (v1.28.2)
    But the Staging context was not found. Please run the following command to configure it:

    aws eks update-kubeconfig --name staging-cluster --region <your-region>

    Let me know when configuration is complete, and I will continue.
```

#### 3. Troubleshooting flow

```
User: The api-gateway on Staging keeps CrashLoopBackOff

AI: Let me investigate:

    1. Checking Pod status...
       NAME                          READY   STATUS             RESTARTS   AGE
       api-gateway-5d4f6c7b8-x2k9z  0/1     CrashLoopBackOff   5          10m

    2. Checking recent logs...
       Error: failed to connect to database at <ip>:5432

    3. Checking events...
       Back-off restarting failed container

    Analysis: Pod cannot connect to database at <ip>:5432. Recommended checks:
    - Is the database service running normally
    - Is a NetworkPolicy blocking the connection
    - Is the database address correct in the ConfigMap/Secret
```

## Exemptions

| Scenario | Condition |
|------|------|
| Emergency incident recovery | User explicitly states an emergency — confirmation steps may be skipped |
| Non-managed clusters | User provides a context not in the Setup list above |

Exemption method: `/override skill=k8s-ops reason="emergency incident recovery"`
