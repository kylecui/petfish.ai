#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8787}"

echo "== healthz =="
curl -sS "$BASE_URL/healthz" | python -m json.tool

echo "== v1 health =="
curl -sS "$BASE_URL/v1/health" | python -m json.tool

echo "== v1 version =="
curl -sS "$BASE_URL/v1/version" | python -m json.tool

echo "== route =="
curl -sS -X POST "$BASE_URL/v1/kernel/route" \
  -H 'Content-Type: application/json' \
  -d '{"user_message":"我要在 OpenCode 项目里安装 security profile","platform":"opencode"}' \
  | python -m json.tool

echo "== suggest packs =="
curl -sS -X POST "$BASE_URL/v1/catalog/suggest" \
  -H 'Content-Type: application/json' \
  -d '{"project_description":"AI security research project with docs, PPT, deploy and trust policy","platform":"opencode"}' \
  | python -m json.tool

echo "== render install =="
curl -sS -X POST "$BASE_URL/v1/install/render" \
  -H 'Content-Type: application/json' \
  -d '{"packs":["context","deploy","petfish","testdocs","trust"],"platform":"opencode","target":"."}' \
  | python -m json.tool

echo "== trust classify =="
curl -sS -X POST "$BASE_URL/v1/trust/classify" \
  -H 'Content-Type: application/json' \
  -d '{"action_text":"review a scoped file cleanup plan","target_runtime":"opencode"}' \
  | python -m json.tool

echo "== online: route =="
curl -sS -X POST "$BASE_URL/v1/kernel/route" \
  -H 'Content-Type: application/json' \
  -d '{"user_message":"Help me choose a profile for a ChatGPT-only code review project.","platform":"online"}' \
  | python -m json.tool

echo "== online: render install =="
curl -sS -X POST "$BASE_URL/v1/install/render" \
  -H 'Content-Type: application/json' \
  -d '{"packs":["companion","context","petfish","testdocs","trust"],"platform":"online"}' \
  | python -m json.tool

echo "== online: trust classify =="
curl -sS -X POST "$BASE_URL/v1/trust/classify" \
  -H 'Content-Type: application/json' \
  -d '{"action_text":"Run local tests for this ChatGPT Project.","target_runtime":"online"}' \
  | python -m json.tool
