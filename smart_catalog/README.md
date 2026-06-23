# 智能编目系统

## 项目结构

```
smart_catalog/
├── backend/           # Flask 后端 (Python)
│   ├── app.py         # 入口
│   ├── models.py      # 数据模型
│   └── routes/
│       ├── catalogs.py   # 目录管理
│       ├── duties.py     # 职能管理 + 匹配
│       ├── lines.py      # 条线管理
│       └── results.py    # 匹配结果
└── frontend/          # Vue 3 前端
    ├── src/
    │   ├── App.vue
    │   ├── views/
    │   │   ├── CatalogManagement.vue
    │   │   ├── DutyManagement.vue
    │   │   ├── LineManagement.vue
    │   │   └── MatchResults.vue
    │   ├── api/index.js
    │   └── router/index.js
    └── package.json
```

## 启动方式

### 后端

```bash
cd smart_catalog/backend
pip install -r requirements.txt
python app.py
```

监听 http://localhost:5000，数据库自动创建为 `backend/intellicat.db`。

### 前端

```bash
cd smart_catalog/frontend
npm install
npm run dev
```

监听 http://localhost:3000，/api 请求自动代理到后端 5000 端口。

## 外部接口对接

匹配功能的核心入口在 `backend/routes/duties.py` 的 `_call_external_api` 函数（约第 163 行）。

### 当前占位实现

```python
def _call_external_api(catalog_items, duty_items):
    api_url = current_app.config.get('MATCH_API_URL', '')
    if api_url:
        # 有 MATCH_API_URL 时发 POST 请求
        payload = {
            'catalogs': [{'name': c['name'], 'fields': c.get('fields', [])} for c in catalog_items],
            'duties': [{'name': d['name']} for d in duty_items]
        }
        resp = requests.post(api_url, json=payload, timeout=60)
        return resp.json()
    # 无配置时随机匹配（占位）
    ...
```

### 入参说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `catalog_items` | `list[dict]` | 目录项列表，每项 `{name: str, fields: list[str]}` |
| `duty_items` | `list[dict]` | 职能列表，每项 `{name: str, id: int}` |

被调用前已按条线分组，每次调用是一个条线下的全部目录和职能。

### 期望返回值

```python
# key=目录名称, value=匹配的职能名称
{"目录A": "负责全市财政预算编制", "目录B": "负责全市税收征管"}
```

### 对接步骤

拿到接口文档后，修改 `_call_external_api` 函数：

1. **构造请求参数** — 根据接口文档调整 payload 的字段名和结构（`duties.py:174-176`）
2. **调用接口** — 修改 URL、方法、超时等（`duties.py:178`）
3. **解析响应** — 将接口返回数据映射为 `{目录名: 职能名}` 格式（`duties.py:179-180`）

### 环境变量

| 变量 | 说明 |
|------|------|
| `MATCH_API_URL` | 外部匹配接口地址，设置后自动使用 |

可通过 `.env` 文件或系统环境变量设置。

### 三条铁律

| 规则 | 说明 | 位置 |
|------|------|------|
| 铁律一 | 职责-部门映射唯一性校验 | `duties.py:_validate_duty_unique` |
| 铁律三 | 按条线分组，逐组匹配 | `duties.py:match_duties` 第 231 行起 |

> 铁律二（手动条线选择限制）已在用户要求下移除，当前 1 条映射时自动选择。
