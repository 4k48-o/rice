#!/bin/bash

# 菜单管理 API 测试脚本

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

echo "=========================================="
echo "菜单管理 API 测试"
echo "=========================================="

# 1. 登录获取 token
echo ""
echo "1. 登录获取 token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo "$LOGIN_RESPONSE" | python3 -m json.tool
  exit 1
fi

echo "✅ 登录成功，Token: ${TOKEN:0:50}..."

# 2. 测试获取菜单列表
echo ""
echo "2. 测试获取菜单列表 (GET /menus)..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/menus?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取菜单列表成功"
else
  echo "❌ 获取菜单列表失败，code: $CODE"
fi

# 3. 测试获取完整菜单树
echo ""
echo "3. 测试获取完整菜单树 (GET /menus/tree/all)..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/menus/tree/all" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取完整菜单树成功"
else
  echo "❌ 获取完整菜单树失败，code: $CODE"
fi

# 4. 测试获取用户菜单树
echo ""
echo "4. 测试获取用户菜单树 (GET /menus/user)..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/menus/user" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取用户菜单树成功"
else
  echo "❌ 获取用户菜单树失败，code: $CODE"
fi

# 5. 测试创建菜单
echo ""
echo "5. 测试创建菜单 (POST /menus)..."
CREATE_DATA='{
  "name": "test_menu_'$(date +%s)'",
  "title": "测试菜单",
  "type": 2,
  "path": "/test/menu",
  "component": "TestMenu",
  "sort": 100,
  "status": 1,
  "visible": 1
}'
RESPONSE=$(curl -s -X POST "${BASE_URL}/menus" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$CREATE_DATA")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 创建菜单成功"
  MENU_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
  echo "   菜单ID: $MENU_ID"
else
  echo "❌ 创建菜单失败，code: $CODE"
  MENU_ID=""
fi

# 6. 测试获取单个菜单
if [ -n "$MENU_ID" ]; then
  echo ""
  echo "6. 测试获取单个菜单 (GET /menus/{menu_id})..."
  RESPONSE=$(curl -s -X GET "${BASE_URL}/menus/${MENU_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json")
  echo "$RESPONSE" | python3 -m json.tool
  CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
  if [ "$CODE" = "200" ]; then
    echo "✅ 获取单个菜单成功"
  else
    echo "❌ 获取单个菜单失败，code: $CODE"
  fi
fi

# 7. 测试更新菜单
if [ -n "$MENU_ID" ]; then
  echo ""
  echo "7. 测试更新菜单 (PUT /menus/{menu_id})..."
  UPDATE_DATA='{
    "title": "更新后的测试菜单",
    "sort": 200
  }'
  RESPONSE=$(curl -s -X PUT "${BASE_URL}/menus/${MENU_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$UPDATE_DATA")
  echo "$RESPONSE" | python3 -m json.tool
  CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
  if [ "$CODE" = "200" ]; then
    echo "✅ 更新菜单成功"
  else
    echo "❌ 更新菜单失败，code: $CODE"
  fi
fi

# 8. 测试删除菜单
if [ -n "$MENU_ID" ]; then
  echo ""
  echo "8. 测试删除菜单 (DELETE /menus/{menu_id})..."
  RESPONSE=$(curl -s -X DELETE "${BASE_URL}/menus/${MENU_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json")
  echo "$RESPONSE" | python3 -m json.tool
  CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
  if [ "$CODE" = "200" ]; then
    echo "✅ 删除菜单成功"
  else
    echo "❌ 删除菜单失败，code: $CODE"
  fi
fi

# 9. 测试无效父菜单验证
echo ""
echo "9. 测试无效父菜单验证..."
INVALID_PARENT_DATA='{
  "name": "test_invalid_parent",
  "title": "无效父菜单测试",
  "type": 2,
  "parent_id": "999999999999999999",
  "path": "/test/invalid",
  "status": 1
}'
RESPONSE=$(curl -s -X POST "${BASE_URL}/menus" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$INVALID_PARENT_DATA")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "400" ]; then
  echo "✅ 正确拒绝了无效父菜单"
else
  echo "❌ 应该返回 400，但返回了 code: $CODE"
fi

# 10. 测试循环引用验证
echo ""
echo "10. 测试循环引用验证..."
# 先创建一个父菜单
PARENT_DATA='{
  "name": "test_parent_'$(date +%s)'",
  "title": "父菜单",
  "type": 1,
  "path": "/test/parent",
  "sort": 100,
  "status": 1
}'
PARENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/menus" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PARENT_DATA")
PARENT_ID=$(echo $PARENT_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data']['id'] if d.get('code')==200 else '')" 2>/dev/null)

if [ -n "$PARENT_ID" ]; then
  # 创建子菜单
  CHILD_DATA='{
    "name": "test_child_'$(date +%s)'",
    "title": "子菜单",
    "type": 2,
    "parent_id": "'${PARENT_ID}'",
    "path": "/test/child",
    "status": 1
  }'
  CHILD_RESPONSE=$(curl -s -X POST "${BASE_URL}/menus" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$CHILD_DATA")
  CHILD_ID=$(echo $CHILD_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data']['id'] if d.get('code')==200 else '')" 2>/dev/null)
  
  if [ -n "$CHILD_ID" ]; then
    # 尝试将父菜单的父ID设置为子菜单（循环引用）
    CIRCULAR_UPDATE='{"parent_id": "'${CHILD_ID}'"}'
    RESPONSE=$(curl -s -X PUT "${BASE_URL}/menus/${PARENT_ID}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$CIRCULAR_UPDATE")
    echo "$RESPONSE" | python3 -m json.tool
    CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
    if [ "$CODE" = "400" ]; then
      echo "✅ 正确拒绝了循环引用"
    else
      echo "❌ 应该返回 400，但返回了 code: $CODE"
    fi
    
    # 清理：删除子菜单和父菜单
    curl -s -X DELETE "${BASE_URL}/menus/${CHILD_ID}" -H "Authorization: Bearer ${TOKEN}" > /dev/null
    curl -s -X DELETE "${BASE_URL}/menus/${PARENT_ID}" -H "Authorization: Bearer ${TOKEN}" > /dev/null
  fi
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

