#!/bin/bash

# 字典管理 API 测试脚本

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

echo "=========================================="
echo "字典管理 API 测试"
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

# 2. 测试获取字典类型列表
echo ""
echo "2. 测试获取字典类型列表 (GET /dict-types)..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/dict-types?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取字典类型列表成功"
else
  echo "❌ 获取字典类型列表失败，code: $CODE"
fi

# 3. 测试创建字典类型
echo ""
echo "3. 测试创建字典类型 (POST /dict-types)..."
DICT_TYPE_CODE="test_dict_$(date +%s)"
CREATE_TYPE_RESPONSE=$(curl -s -X POST "${BASE_URL}/dict-types" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"测试字典类型\",
    \"code\": \"${DICT_TYPE_CODE}\",
    \"sort\": 100,
    \"status\": 1
  }")
echo "$CREATE_TYPE_RESPONSE" | python3 -m json.tool
if echo "$CREATE_TYPE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 创建字典类型成功"
  DICT_TYPE_ID=$(echo "$CREATE_TYPE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
  echo "   字典类型ID: $DICT_TYPE_ID"
else
  echo "❌ 创建字典类型失败"
  exit 1
fi

# 4. 测试获取字典类型详情
echo ""
echo "4. 测试获取字典类型详情 (GET /dict-types/{id})..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/dict-types/${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取字典类型详情成功"
else
  echo "❌ 获取字典类型详情失败，code: $CODE"
fi

# 5. 测试更新字典类型
echo ""
echo "5. 测试更新字典类型 (PUT /dict-types/{id})..."
UPDATE_TYPE_RESPONSE=$(curl -s -X PUT "${BASE_URL}/dict-types/${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试字典类型(已更新)",
    "sort": 200
  }')
echo "$UPDATE_TYPE_RESPONSE" | python3 -m json.tool
if echo "$UPDATE_TYPE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 更新字典类型成功"
else
  echo "❌ 更新字典类型失败"
fi

# 6. 测试创建字典数据
echo ""
echo "6. 测试创建字典数据 (POST /dict-data)..."
CREATE_DATA_RESPONSE=$(curl -s -X POST "${BASE_URL}/dict-data" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"dict_type_id\": \"${DICT_TYPE_ID}\",
    \"label\": \"测试选项1\",
    \"value\": \"test_value_1\",
    \"sort\": 1,
    \"status\": 1,
    \"css_class\": \"badge-success\",
    \"color\": \"#52c41a\",
    \"icon\": \"CheckCircleOutlined\"
  }")
echo "$CREATE_DATA_RESPONSE" | python3 -m json.tool
if echo "$CREATE_DATA_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 创建字典数据成功"
  DICT_DATA_ID=$(echo "$CREATE_DATA_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
  echo "   字典数据ID: $DICT_DATA_ID"
else
  echo "❌ 创建字典数据失败"
  exit 1
fi

# 7. 测试创建第二个字典数据
echo ""
echo "7. 测试创建第二个字典数据..."
CREATE_DATA2_RESPONSE=$(curl -s -X POST "${BASE_URL}/dict-data" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"dict_type_id\": \"${DICT_TYPE_ID}\",
    \"label\": \"测试选项2\",
    \"value\": \"test_value_2\",
    \"sort\": 2,
    \"status\": 1,
    \"css_class\": \"badge-warning\",
    \"color\": \"#faad14\"
  }")
echo "$CREATE_DATA2_RESPONSE" | python3 -m json.tool
if echo "$CREATE_DATA2_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 创建第二个字典数据成功"
else
  echo "❌ 创建第二个字典数据失败"
fi

# 8. 测试获取字典数据列表
echo ""
echo "8. 测试获取字典数据列表 (GET /dict-data)..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/dict-data?page=1&page_size=10&dict_type_id=${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取字典数据列表成功"
else
  echo "❌ 获取字典数据列表失败，code: $CODE"
fi

# 9. 测试根据类型获取字典数据（公开接口）
echo ""
echo "9. 测试根据类型获取字典数据 (GET /dict-data/type/{type_code})..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/dict-data/type/${DICT_TYPE_CODE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 根据类型获取字典数据成功"
  DATA_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('data', [])))" 2>/dev/null)
  echo "   获取到 ${DATA_COUNT} 条数据"
else
  echo "❌ 根据类型获取字典数据失败，code: $CODE"
fi

# 10. 测试获取字典数据详情
echo ""
echo "10. 测试获取字典数据详情 (GET /dict-data/{id})..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/dict-data/${DICT_DATA_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$RESPONSE" | python3 -m json.tool
CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 'N/A'))" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "✅ 获取字典数据详情成功"
else
  echo "❌ 获取字典数据详情失败，code: $CODE"
fi

# 11. 测试更新字典数据
echo ""
echo "11. 测试更新字典数据 (PUT /dict-data/{id})..."
UPDATE_DATA_RESPONSE=$(curl -s -X PUT "${BASE_URL}/dict-data/${DICT_DATA_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "测试选项1(已更新)",
    "color": "#1890ff"
  }')
echo "$UPDATE_DATA_RESPONSE" | python3 -m json.tool
if echo "$UPDATE_DATA_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 更新字典数据成功"
else
  echo "❌ 更新字典数据失败"
fi

# 12. 测试错误情况：重复的字典类型编码
echo ""
echo "12. 测试错误情况：创建重复的字典类型编码..."
DUPLICATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/dict-types" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"重复的字典类型\",
    \"code\": \"${DICT_TYPE_CODE}\",
    \"sort\": 100,
    \"status\": 1
  }")
echo "$DUPLICATE_RESPONSE" | python3 -m json.tool
if echo "$DUPLICATE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') != 200 else 1)" 2>/dev/null; then
  echo "✅ 正确拒绝了重复的字典类型编码"
else
  echo "❌ 应该拒绝重复的字典类型编码"
fi

# 13. 测试错误情况：不存在的字典类型ID
echo ""
echo "13. 测试错误情况：使用不存在的字典类型ID创建字典数据..."
INVALID_TYPE_RESPONSE=$(curl -s -X POST "${BASE_URL}/dict-data" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "dict_type_id": "invalid_type_id_999999",
    "label": "测试",
    "value": "test"
  }')
echo "$INVALID_TYPE_RESPONSE" | python3 -m json.tool
if echo "$INVALID_TYPE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') != 200 else 1)" 2>/dev/null; then
  echo "✅ 正确拒绝了不存在的字典类型ID"
else
  echo "❌ 应该拒绝不存在的字典类型ID"
fi

# 14. 测试删除字典数据
echo ""
echo "14. 测试删除字典数据 (DELETE /dict-data/{id})..."
DELETE_DATA_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/dict-data/${DICT_DATA_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$DELETE_DATA_RESPONSE" | python3 -m json.tool
if echo "$DELETE_DATA_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 删除字典数据成功"
else
  echo "❌ 删除字典数据失败"
fi

# 15. 测试删除字典类型（应该失败，因为还有关联的字典数据）
echo ""
echo "15. 测试删除字典类型（应该失败，因为还有关联的字典数据）..."
DELETE_TYPE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/dict-types/${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
echo "$DELETE_TYPE_RESPONSE" | python3 -m json.tool
if echo "$DELETE_TYPE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') != 200 else 1)" 2>/dev/null; then
  echo "✅ 正确拒绝了删除有关联数据的字典类型"
else
  echo "❌ 应该拒绝删除有关联数据的字典类型"
fi

# 16. 删除所有测试数据
echo ""
echo "16. 清理测试数据..."
# 先删除剩余的字典数据
curl -s -X GET "${BASE_URL}/dict-data?dict_type_id=${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('code') == 200:
    for item in data.get('data', {}).get('items', []):
        print(item['id'])
" | while read data_id; do
  if [ ! -z "$data_id" ]; then
    curl -s -X DELETE "${BASE_URL}/dict-data/${data_id}" \
      -H "Authorization: Bearer ${TOKEN}" > /dev/null
  fi
done

# 再删除字典类型
DELETE_TYPE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/dict-types/${DICT_TYPE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")
if echo "$DELETE_TYPE_RESPONSE" | python3 -c "import sys, json; exit(0 if json.load(sys.stdin).get('code') == 200 else 1)" 2>/dev/null; then
  echo "✅ 清理测试数据成功"
else
  echo "⚠️  清理测试数据时出现问题"
  echo "$DELETE_TYPE_RESPONSE" | python3 -m json.tool
fi

echo ""
echo "=========================================="
echo "字典管理 API 测试完成"
echo "=========================================="

