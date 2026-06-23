# 智能编目系统

## 项目结构

```
smart_catalog/
├── backend/           # Flask 后端 (Python)
│   ├── app.py         # 入口
│   ├── models.py      # 数据模型
│   ├── utils.py       # 工具函数（分页、请求校验）
│   ├── .env.example   # 环境变量模板
│   └── routes/
│       ├── catalogs.py   # 目录管理
│       ├── duties.py     # 职能管理 + 匹配
│       ├── lines.py      # 条线管理
│       └── results.py    # 匹配结果
└── frontend/          # Vue 3 前端
    ├── src/
    │   ├── App.vue        # 布局 + 全局 CSS（字体系统、卡片、空状态）
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

## 工具函数（backend/utils.py）

| 函数 | 用途 |
|------|------|
| `bad_request(msg, status)` | 统一错误响应 `(jsonify + status code)` |
| `paginate(query, page, per_page)` | SQLAlchemy 查询分页，返回 `(items, total, page, per_page, total_pages)` |
| `jsonify_paginated(items, total, ...)` | 数组响应 + 分页 headers（向前端兼容） |
| `expect_body(*names)` | 装饰器：校验 JSON body 必填字段 |
| `expect_file(name)` | 装饰器：校验上传文件必填 |

所有 GET 列表接口支持 `?page=&per_page=` 分页查询参数，分页信息通过响应头返回：
- `X-Total-Count` — 总记录数
- `X-Page` — 当前页码
- `X-Per-Page` — 每页条数
- `X-Total-Pages` — 总页数


## 外部接口对接

匹配功能的核心入口在 `backend/routes/duties.py` 的 `_call_external_api` 函数（约第 167 行）。

### 接口说明

对接的是「职能匹配文件形式」智能体，采用 **多文件上传模式**：

```
POST http://2.142.92.117:30486/scene_gateway/ad441c290aef406fa9350344f513461c
Content-Type: multipart/form-data
AuthToken: f2fa523939374d8392c9eb50a6dcb245

keyword=职能匹配
requestId=20260623001
sceneKey=ad441c290aef406fa9350344f513461c
zhineng=@职能文件.xlsx
mulu=@目录文件.xlsx
```

### 实现逻辑

1. 从 `catalog_items` / `duty_items` 动态生成临时 xlsx（通过 openpyxl 写入 BytesIO）
2. 用 `requests` 以 `multipart/form-data` 上传
3. 解析返回的 `data` 数组，提取 `【数据目录名称】` 和 `【匹配内设机构】`
4. 按内设机构名称匹配到本地 duty 记录
5. 返回 `{目录名: 职能名}` 字典

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MATCH_MODE` | 匹配模式：`api`（调外部接口，失败即报错）或 `local`（本地随机，开发/演示用） | `api` |
| `MATCH_API_URL` | 智能体接口地址 | 见上方 POST URL |
| `MATCH_AUTH_TOKEN` | 授权密钥 | `f2fa523939374d8392c9eb50a6dcb245` |
| `MATCH_SCENE_KEY` | 应用 ID | `ad441c290aef406fa9350344f513461c` |

可通过 `.env` 或系统环境变量覆盖。设 `MATCH_MODE=local` 可跳过外部接口，使用本地随机匹配。

### 响应格式

每条数据格式为纯文本块，包含：
```
【数据目录名称】：目录名
【匹配内设机构】：机构名
【对应核心职能原文】：职能描述
【匹配依据】：推理依据
```

对每个目录名，查找本地 duty 中 `inner_org` 匹配的记录，取 `duty_name` 存入匹配结果。

### 三条铁律

| 规则 | 说明 | 位置 |
|------|------|------|
| 铁律一 | 职责-部门映射唯一性校验 | `duties.py:_validate_duty_unique` |
| 铁律三 | 按条线分组，逐组匹配 | `duties.py:match_duties` 第 235 行起 |

> 铁律二（手动条线选择限制）已在用户要求下移除，当前 1 条映射时自动选择。
