# diploma

`redis-lock` - название которое я даю релизам
```
helm install redis-lock bitnami/redis -f k8s/helm/redis-lock/values.yaml
```

Полистить созданный ресурс можно через:
```
kubectl get all -l "app.kubernetes.io/instance=redis-lock-v1" -n default
```

Применить манифест:
```
kubectl apply -f k8s/manifests/redis-cluster.yaml
```

```
neevin@i111033924:~/uni/diploma$ helm install redis-lock-v2 bitnami/redis -f k8s/helm/redis-lock/values.yaml
NAME: redis-lock-v2
LAST DEPLOYED: Fri Apr 26 19:29:31 2024
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: redis
CHART VERSION: 19.1.3
APP VERSION: 7.2.4

** Please be patient while the chart is being deployed **

Redis&reg; can be accessed on the following DNS names from within your cluster:

    redis-lock-v2-master.default.svc.cluster.local for read/write operations (port 6379)
    redis-lock-v2-replicas.default.svc.cluster.local for read-only operations (port 6379)



To get your password run:

    export REDIS_PASSWORD=$(kubectl get secret --namespace default redis-lock-v2 -o jsonpath="{.data.redis-password}" | base64 -d)

To connect to your Redis&reg; server:

1. Run a Redis&reg; pod that you can use as a client:

   kubectl run --namespace default redis-client --restart='Never'  --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:7.2.4-debian-12-r12 --command -- sleep infinity

   Use the following command to attach to the pod:

   kubectl exec --tty -i redis-client \
   --namespace default -- bash

2. Connect using the Redis&reg; CLI:
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-lock-v2-master
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-lock-v2-replicas

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace default svc/redis-lock-v2-master 6379:6379 &
    REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - master.resources
  - replica.resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

```

