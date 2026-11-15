# DevAgent

基于 RAG + LangGraph 的代码仓库智能体（学习项目）。

DevAgent 会把本地代码仓库扫描、切块并写入 Chroma 向量库，再通过 LLM + Function Calling 回答与仓库相关的问题。项目包含手写 ToolAgent、LangGraph GraphAgent、CLI 和 FastAPI Web 聊天页，用于完整练习一个 Agent 应用从检索、工具调用到接口化的过程。

## 功能特性

- 代码扫描与切块：按扩展名收集源码和文档，默认 500 字符一块、100 字符重叠
- 向量检索：`BAAI/bge-small-zh-v1.5` + Chroma 持久化
- 工具调用：`read_file` / `search_codebase`，由模型自主决定是否调用
- 两种 Agent 实现：ToolAgent（手写 Function Calling 循环）、GraphAgent（LangGraph 状态图）
- 多轮会话：按 `session_id` 持久化到 `data/sessions`
- 两种使用方式：命令行 `devagent`、FastAPI 接口 + 静态聊天页

## 项目结构

```text
DevAgent/
├── src/devagent/
│   ├── agent/          # tool_agent.py / graph_agent.py / session.py
│   ├── rag/            # scanner.py / splitter.py / vector_store.py
│   ├── tools/          # file_tools.py / rag_tools.py / tool_registry.py
│   ├── server/         # main.py / static/index.html
│   ├── cli.py          # 命令行入口
│   ├── config.py       # pydantic-settings 配置
│   ├── llm_client.py   # LLM 请求与重试
│   └── exceptions.py
├── test/               # 学习过程中的脚本式测试
├── async_lab/          # 异步编程练习 step1-step7
├── data/               # 运行时生成：vector_db / sessions
├── pyproject.toml
└── DevAgent（代码仓库智能体）开发文档.md
```

## 环境要求

- Python 3.12+（`vector_store.py` 使用了 Python 3.12 的 f-string 语法）
- 可访问 OpenAI 兼容接口的 LLM API
- 本地已缓存 `BAAI/bge-small-zh-v1.5`（项目默认离线加载）

## 快速开始

### 1. 安装

```bash
git clone https://github.com/ypf319/DevAgent.git
cd DevAgent

python3.12 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### 2. 配置

在项目根目录创建 `.env`：

```dotenv
SF_LLM_BASE_URL=https://api.siliconflow.cn/v1
SF_LLM_API_KEY=your_siliconflow_key
SF_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct

CLOSE_LLM_BASE_URL=https://api.openai-proxy.org/v1
CLOSE_LLM_API_KEY=your_closeai_key
CLOSE_LLM_MODEL=qwen3.8-flash
```

当前代码在导入时会同时初始化 SiliconFlow 和 CloseAI 两套配置，因此两组变量都需要填写；实际对话使用 `CLOSE_*`。任何 OpenAI 兼容接口都可以替换，只需保证 `*_LLM_BASE_URL` 指向 `/v1/chat/completions` 所在的地址。

### 3. 构建向量索引

```bash
python - <<'PY'
from devagent.rag.scanner import scan_repo
from devagent.rag.splitter import split_files
from devagent.rag.vector_store import vector_store

files = scan_repo("src")
chunks = split_files(files, chunk_size=500, chunk_overlap=100)
vector_store.add_document(chunks)
print(f"索引完成：{len(files)} 个文件，{len(chunks)} 个文本块")
PY
```

`scan_repo()` 可以传入任意仓库路径，上面用 `src` 索引本项目源码。索引会写入 `data/vector_db`，重复执行会覆盖同一批文本块。

如果本机还没有 BGE 模型缓存，可以先单独下载（该命令不会触发项目的离线设置）：

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
```

### 4. 命令行使用

```bash
devagent "这个项目的配置是怎么管理的？"
```

### 5. 启动 Web 服务

```bash
uvicorn devagent.server.main:app --reload --port 8000
```

浏览器打开：http://127.0.0.1:8000/static/index.html

可用接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat` | 同步问答，请求体 `{"query": "...", "session_id": "..."}` |
| GET | `/api/chat/stream?query=...` | SSE 流式问答（实验性，前端暂未接入） |

## 配置与数据

| 变量 / 目录 | 说明 |
| --- | --- |
| `SF_LLM_*` | SiliconFlow 配置（当前代码中预留） |
| `CLOSE_LLM_*` | CloseAI / OpenAI 代理配置（当前实际调用） |
| `data/vector_db/` | Chroma 向量库，构建索引后生成 |
| `data/sessions/` | 多轮会话记录，按 `session_id` 保存 |

`.env`、`data/`、`.venv/` 已加入 `.gitignore`，不会提交到仓库。

## 学习模块：async_lab

`async_lab/` 是配套的异步编程练习，覆盖同步阻塞、`asyncio.gather`、超时取消、异步生成器、队列流水线、线程/进程/协程对比，以及并发调用 LLM。每个脚本都可以独立运行：

```bash
python async_lab/step1_sync_vs_async.py
```

更多说明见 [`async_lab/README.md`](async_lab/README.md)。

## 已知限制

- 向量索引需要手动构建，暂未提供 `devagent index` 子命令
- Web 前端目前调用同步接口，SSE 接口只完成了后端部分
- 多轮会话加载时不会重新注入 system 提示词，第二轮之后会丢失系统设定
- 打包配置尚不完整：wheel 未包含 `server/static/index.html`，且未声明 `requires-python`

## 开发文档

详细的项目拆解和学习笔记见根目录 `DevAgent（代码仓库智能体）开发文档.md`。

## 说明

本项目为个人学习项目，暂未指定开源许可证。仅供学习交流使用。
