#!/usr/bin/env bash
set -euo pipefail

echo "==> Creating argocd namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

echo "==> Bootstrapping ArgoCD control plane..."
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "==> ArgoCD successfully bootstrapped!"