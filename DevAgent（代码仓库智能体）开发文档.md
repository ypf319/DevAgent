# 1.项目结构与设计

🚀 项目：DevAgent —— 你的"代码仓库智能体"
一句话愿景：往任意代码仓库里跑一条命令，它就能读懂项目、回答问题、生成总结、跑测试，并通过 Agent 协作 + 知识库给出带出处的答案，最后变成可部署的网页服务。
最终架构（我们要逐步建成的样子）
用户输入 ──▶ CLI / Web 界面
                │
                ▼
        ┌───────────────────────┐
        │   LANGRAPH 编排层       │  多步骤工作流、条件分支、循环
        │  理解Agent → 检索Agent │
        │  审查Agent → 总结Agent │  多智能体协作
        └───────┬───────────────┘
                │  ReAct循环（思考→行动→观察）
                ▼
        ┌───────────────────────┐
        │   工具层(函数/函数工具) │  search_code / read_file / run_tests
        │   + MCP服务器          │  git_log / ask_knowledge_base ...
        └───────┬───────────────┘
                ▼
     ┌─────────────────────┬───────────────┐
     │  RAG 知识库           │  Memory 记忆   │
     │  代码嵌入+语义检索     │  会话/向量记忆  │
     │  重排 rerank          │               │
     └─────────────────────┴───────────────┘
                ▼
         LLM（DeepSeek / SiliconFlow）+ BGE 向量/重排模型
技术栈全覆盖清单
阶段    复用你已学的
基础    装饰器/JSON/os/异常/.env
调用    requests + retry、多轮上下文、调参
工具    Function Calling 手写循环
检索    Chroma 基础 RAG
编排    —
交付    pandas/openpyxl 导出
质量    —
分阶段路线图（每阶段有交付物，边做边学）

- Phase 0 · 搭骨架：新建项目、重建 api_retry + LLMClient（重学 d01/04/13/18）、环境变量、目录结构
- Phase 1 · CLI 问答版：devagent "这个项目干嘛的？" —— 工具搜索代码、Function Calling、结构化输出、带出处回答（重学 module 1–6, 9）
- Phase 2 · 知识库+记忆版：代码向量化检索、rerank 重排、会话记忆落盘（重学 module 10 + 进阶 RAG）
- Phase 3 · Agent 化版：LangGraph 编排 + ReAct 循环 + 三 Agent 协作 + MCP 工具服务器（补最大的缺口）
- Phase 4 · 流式+服务化版：asyncio 流式输出、FastAPI + 网页聊天框、LLM-as-judge 评估 + trace、Docker 部署

# 第一阶段：基础篇——最小可运行原型

第一阶段共 4 个小结，目标是把「项目骨架 → 配置 → 能调用大模型」这条最小链路先跑通：

| 小结 | 名称 | 核心产出 | 对应知识点 |
| --- | --- | --- | --- |
| 小结一 | 项目初始化与环境搭建 | 标准项目目录 + 虚拟环境 | Python 项目规范、虚拟环境 |
| 小结二 | 配置与异常封装 | `.env` + `config.py` + `exceptions.py` | 环境变量、自定义异常 |
| 小结三 | LLM 客户端封装 | `llm_client.py`（带重试） | API 调用、失败重试 |
| 小结四 | 第一个工具与最简问答链路 | `read_file` 工具 + `simple_qa` 脚本 | 工具本质、核心问答链路 |

当前进度：✅ 第一阶段四个小结全部完成（4/16），下一阶段为「第二阶段：规范篇——自动工具调用 Agent」。

---

## 小结一：项目初始化与环境搭建

### 1. 本小结目标

从零搭出标准的 Python 项目目录，创建独立虚拟环境。完成后拥有一个干净、隔离的项目 workspace，后续所有代码和依赖都只在这个环境里运行。

### 2. 为什么先做这一步

这是所有工业级 Python 项目的标准起点。虚拟环境可以把本项目的依赖和你电脑上其他项目完全隔离，避免出现「版本冲突」「换个地方就跑不起来」的问题。

### 3. 创建项目根目录

本项目的实际位置：

```text
/Users/mac/Documents/DevAgent
```

以后所有命令默认都在这个目录下执行。

### 4. 创建虚拟环境

```bash
python3 -m venv .venv
```

> `venv` 是 Python 自带的模块，`.venv` 是项目专属的「独立工具箱」，后面装的所有库都只放在这里。

### 5. 激活虚拟环境

macOS / Linux：

```bash
source .venv/bin/activate
```

Windows：

```bash
.venv\Scripts\activate
```

激活成功的标志：终端每一行的开头出现 `(.venv)`。

### 6. 升级 pip

```bash
pip install --upgrade pip
```

> pip 是 Python 的包管理工具，升级到最新版最稳定。

### 7. 预期结果

- 有一个 `DevAgent` 文件夹；
- 里面有 `.venv` 文件夹；
- 终端开头显示 `(.venv)`；
- `python --version` 输出 `Python 3.12.14`（本项目实测）；
- `pip --version` 能正常显示版本号，没有报错。

### 8. 本项目实际踩过的坑：`python` 被别名劫持

`~/.zshrc` 里原本有：

```bash
alias python='/opt/homebrew/bin/python3'
```

这会让 `python` 永远指向 Homebrew 的解释器。即使激活了虚拟环境，`python` 也不会使用 `.venv` 里的版本，`pip install` 也会装到错误的位置。

已改为：

```bash
alias python='python3'
```

改完后执行 `source ~/.zshrc`，或者新开一个终端。验证方式：

```bash
source .venv/bin/activate
python --version   # 应输出 Python 3.12.14
which python       # 应指向 .../DevAgent/.venv/bin/python
```

> 注意：系统自带的 `python3` 是 3.14.6，而项目 `.venv` 建在 3.12.14 上。**必须先激活虚拟环境，再执行 `python`**，否则用的仍是系统解释器。

### 9. 小结

小结一只做了一件事：把「地盘」和「独立工具箱」准备好。后面所有代码都必须在 `.venv` 激活的前提下运行。

---

## 小结二：配置与异常封装

### 1. 本小结目标

完成项目的基础配置体系和异常体系，产出 3 个核心文件：`.env`、`config.py`、`exceptions.py`，同时搭好标准的源码目录结构。

完成后，密钥、接口地址、模型名等配置统一管理，报错有统一的类型，后面所有功能都基于这套基础设施开发。

### 2. 为什么做这一步

1. **安全**：API 密钥这类敏感信息不能直接写死在代码里，万一上传到 Git 就泄露了，放在 `.env` 里单独管理更安全。
2. **方便**：所有配置集中在一个文件，以后改地址、换模型，只改 `.env` 就行，不用动代码。
3. **好维护**：自定义异常可以让人一眼看出是哪个模块出了问题，而不是只看到一堆系统自带的报错。

### 3. 新建依赖配置文件 `pyproject.toml`

这是 Python 项目的标准配置文件，告诉 Python 项目叫什么、需要安装哪些第三方库。在项目根目录新建 `pyproject.toml`：

```toml
[project]
name = "devagent"
version = "0.1.0"
dependencies = [
    "pydantic-settings>=2.0",# 用来读取 .env 配置文件
    "requests>=2.31.0",
    "tenacity>=8.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

> 小结二只需要 `pydantic-settings`；`requests` 和 `tenacity` 是小结三才用到的，这里提前一起写上，后面不用再改。

### 4. 新建 `.env` 环境变量文件

这个文件专门存敏感配置。在项目根目录新建，文件名**必须是 `.env`**（前面有一个点，Windows 不要存成 `.env.txt`）。

本项目使用的是 SiliconFlow，实际内容如下（密钥已打码）：

```env
LLM_API_KEY=sk-替换成你自己的key
LLM_BASE_URL=https://api.siliconflow.cn/v1/chat/completions
LLM_MODEL=deepseek-ai/DeepSeek-V4-Flash
```

> 这里 `LLM_BASE_URL` 直接写的是**完整的接口地址**（包含 `/chat/completions`），所以后面的代码不需要再拼接路径。如果换成 DeepSeek 等其他平台，只改这三行即可，代码不用动。

### 5. 搭建源码目录结构

所有功能代码都放在 `src/devagent/` 下，这是 Python 项目的标准 `src` 布局：

```text
DevAgent/
├── .env
├── pyproject.toml
├── src/
│   └── devagent/
│       ├── __init__.py
│       ├── config.py
│       ├── exceptions.py
│       └── llm_client.py
└── test/
    ├── test_config.py
    └── llm_client_test.py
```

`__init__.py` 是一个标识文件，告诉 Python 这个文件夹是一个可以导入的代码包。空文件即可。

> 本项目把测试脚本放在了 `test/` 子目录，而不是教程里的项目根目录。执行时要注意路径和运行目录，见下文「本项目实际踩过的坑」。

### 6. 编写 `config.py` —— 配置读取器

这个文件负责把 `.env` 里的配置读成 Python 里可以直接用的变量。后面所有文件要用配置，导入它即可。在 `src/devagent/` 下新建 `config.py`：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

# 定义配置类，自动从 .env 文件读取对应变量
class Settings(BaseSettings):
    # 告诉配置类去读根目录的 .env 文件，编码用 utf-8
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 下面三个变量名必须和 .env 文件里的名字完全一致
    llm_base_url: str
    llm_api_key: str
    llm_model: str

# 创建一个全局的配置实例，后面所有文件直接导入这个对象用
settings = Settings()
```

关键点：

- 变量名 `llm_base_url` / `llm_api_key` / `llm_model` 必须和 `.env` 里的 `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` 对应（pydantic-settings 默认不区分大小写）。
- `env_file=".env"` 是**相对路径**，按「当前运行目录」解析，不是按 `config.py` 所在目录解析。

### 7. 编写 `exceptions.py` —— 自定义异常

在 `src/devagent/` 下新建 `exceptions.py`：

```python
# 项目所有异常的基类，后面所有自定义错误都继承它
class DevAgentBaseError(Exception):
    """DevAgent 项目基础异常类"""
    pass

# 大模型调用相关的错误
class LLMRequestError(DevAgentBaseError):
    """大模型请求失败异常"""
    pass
```

这样上层只要捕获 `DevAgentBaseError`，就能统一处理本项目抛出的所有业务异常。

### 8. 安装依赖

在项目根目录、虚拟环境已激活的前提下执行：

```bash
pip install -e .
```

> `-e` 是开发模式（editable）。项目以 `devagent` 的名字安装，实际通过 `.pth` 文件指向 `src/`，以后改代码不用重新安装，直接生效。

### 9. 验证配置能读出来

在 `test/` 下新建 `test_config.py`：

```python
from src.devagent.config import settings

def test_config():
    print("配置读取成功！")
    print(f"接口地址：{settings.llm_base_url}")
    print(f"模型名称：{settings.llm_model}")
    # 密钥只打印前几位，避免泄露
    print(f"API密钥前5位：{settings.llm_api_key[:5]}...")

if __name__ == "__main__":
    test_config()
```

在**项目根目录**运行：

```bash
python test/test_config.py
```

预期结果：

```text
配置读取成功！
接口地址：https://api.siliconflow.cn/v1/chat/completions
模型名称：deepseek-ai/DeepSeek-V4-Flash
API密钥前5位：sk-xx...
```

终端正常打印出三项配置、没有任何报错，说明配置文件、目录结构、依赖安装都没问题。

### 10. 本项目实际踩过的坑

1. **`ModuleNotFoundError: No module named 'pydantic_setting'`**
   导入时把 `pydantic_settings` 少写了一个 `s`。包名是 `pydantic_settings`，不是 `pydantic_setting`。

2. **`ValidationError: 3 validation errors ... Field required`**
   说明 `Settings()` 一个字段都没读到。常见原因有两个：
   - `.env` 里的变量名和 `config.py` 里的字段名不一致；
   - **运行目录不对**，`.env` 没被找到。本项目实测：在项目根目录执行正常，在 `/tmp` 下执行同样命令就会报 3 个 `Field required`。

3. **`.env` 是按「运行目录」找的**
   `env_file=".env"` 是相对路径。以下方式都能正常运行：

   ```bash
   # 方式一：先进入项目根目录
   cd /Users/mac/Documents/DevAgent
   python test/test_config.py
   ```

   ```bash
   # 方式二：PyCharm 运行配置里把 Working directory 设为项目根目录
   /Users/mac/Documents/DevAgent
   ```

   如果 Working directory 是 `test/`，就会找不到 `.env`。这个问题不能靠改代码绕过（本项目约定不改 `config.py`），只能靠运行配置解决。

4. **`from src.devagent...` 会加载两份模块**
   `src/` 下没有 `__init__.py`，`src` 不是一个包。`from src.devagent.config import settings` 和 `from devagent.config import settings` 会各自加载一份模块，导致 `settings is settings` 为 `False`。正确写法是安装后直接 `from devagent.config import settings`。本项目当前测试脚本仍使用 `src.devagent...`，暂时能跑通，但后续应统一改为 `devagent...`。

### 11. 小结

小结二把「配置」和「异常」两块基础设施搭好了：配置集中在 `.env`，代码通过 `settings` 读取；异常有了统一基类。后面写任何新功能，都直接复用这两样东西。

---

## 小结三：LLM 客户端封装

### 1. 本小结目标

封装一个稳定、可复用的大模型调用客户端，产出核心文件 `llm_client.py`。它自带失败自动重试、统一异常处理。后面整个项目所有需要调用大模型的地方，都直接用它，不用重复写请求代码。

### 2. 为什么做这一步

1. **复用性**：如果每次调用大模型都手写一遍网络请求，代码会重复又混乱。封装成一个类，后面一行导入就能用。
2. **稳定性**：网络请求偶尔会超时、失败，加上自动重试机制，不用手动重新运行，程序自己就能修复临时故障。
3. **统一性**：所有大模型调用都走同一个入口，以后换模型、改地址、加日志，只改这一个文件就行。

### 3. 更新依赖并重新安装

需要两个新库：`requests`（发 HTTP 请求）、`tenacity`（实现自动重试）。`pyproject.toml` 里已经写好，直接重新安装：

```bash
pip install -e .
```

### 4. 编写 `llm_client.py`

在 `src/devagent/` 下新建 `llm_client.py`：

```python
import requests
# 从tenacity导入重试相关的装饰器和配置
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List, Dict, Any
from src.devagent.config import settings
from src.devagent.exceptions import LLMRequestError

class LLMClient:
    def __init__(self):
        self.llm_base_url = settings.llm_base_url
        self.llm_api_key = settings.llm_api_key
        self.llm_model = settings.llm_model
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization':f"Bearer {self.llm_api_key}"
        }
    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type(requests.exceptions.RequestException)
           )
    def chat(self,meg: List[Dict[str, Any]],) -> dict:

        payload = {
            'messages': meg,
            "model": self.llm_model,
        }

        try:
            response = requests.post(url=self.llm_base_url,
                                 headers=self.headers,
                                 json=payload,
                                 timeout=60
                                 )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise LLMRequestError(f"调用大模型失败：{str(e)}")


llm_client = LLMClient()
```

### 5. 逐块理解

**（1）`__init__`：把配置搬进实例**

从 `settings` 读取接口地址、密钥、模型名，并组装请求头。`Authorization` 用 `Bearer` 认证，`Content-Type` 固定为 `application/json`。

**（2）`@retry`：失败自动重试**

```python
@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type(requests.exceptions.RequestException))
```

- `stop_after_attempt(3)`：最多尝试 3 次（首次 + 2 次重试）；
- `wait_exponential(... min=1, max=10)`：等待时间指数递增，最少 1 秒，最多 10 秒，避免把服务器挤爆；
- `retry_if_exception_type(...)`：只有网络请求异常才重试。

**（3）`payload`：请求体**

```python
payload = {
    'messages': meg,
    "model": self.llm_model,
}
```

`messages` 是对话历史，格式为：

```python
[{"role": "user", "content": "你好"}]
```

**（4）`requests.post`：真正发请求**

```python
response = requests.post(url=self.llm_base_url,
                         headers=self.headers,
                         json=payload,
                         timeout=60)
```

- `url` 直接用 `.env` 里的完整地址，不再拼接 `/chat/completions`；
- `timeout=60`：60 秒超时，避免程序一直卡住。

**（5）`raise_for_status()` + `response.json()`**

状态码是 4xx / 5xx（比如密钥错、服务不可用）时自动抛异常；成功则返回解析好的 JSON 字典。

**（6）统一异常**

```python
except requests.exceptions.RequestException as e:
    raise LLMRequestError(f"调用大模型失败：{str(e)}")
```

把 `requests` 的原生异常包装成项目自己的 `LLMRequestError`，上层只认项目异常。

**（7）模块级单例**

```python
llm_client = LLMClient()
```

模块导入时就创建一个全局实例，后面直接 `from devagent.llm_client import llm_client` 使用，不用每次新建。

### 6. 验证调用

在 `test/` 下新建 `llm_client_test.py`：

```python
from src.devagent.llm_client import LLMClient

def test_llm_client(content:str):
    print("loading...")
    messages = [
        {"role": "user", "content": content},
    ]
    res = LLMClient().chat(messages)

    ans = res["choices"][0]["message"]["content"]
    print(ans)

if __name__ == '__main__':
    test_llm_client("用一句话解释什么是api调用")
```

在**项目根目录**运行：

```bash
python test/llm_client_test.py
```

预期结果：

```text
loading...
API 调用就是你的程序向另一个服务发一个请求，对方处理后把结果返回给你。
```

终端先打印 `loading...`，稍等几秒后打印出模型的回答，没有任何报错，说明网络请求、重试机制、配置读取、异常处理都正常工作。

### 7. 常见问题排查

1. **401 Unauthorized**：API 密钥填错了。检查 `.env` 里的 `LLM_API_KEY`，确认没有多余空格。
2. **404 Not Found**：检查 `LLM_BASE_URL` 和模型名是否正确，路径有没有多写或少写。
3. **连接超时**：检查网络能否访问对应平台，或者换一个国内可访问的大模型 API。
4. **超时重试没生效**：确认 `@retry` 装饰器写在函数定义上方，没有缩进错误；同时注意本项目的已知问题（见下一节第 1 条）。

### 8. 本项目实际踩过的坑

1. **重试实际上不会触发（已知问题，暂未修改）**
   `@retry` 只对 `requests.exceptions.RequestException` 生效，但函数内部已经把该异常 `raise` 成了 `LLMRequestError`。tenacity 看到的是 `LLMRequestError`，不匹配重试条件，所以网络失败时不会重试。
   如果要让重试生效，需要调整异常转换与重试条件的配合（例如把重试条件改为 `LLMRequestError`，或只对未包装的异常重试）。当前阶段先记录，不改代码。

2. **`self.model` → `self.llm_model`**
   `__init__` 里属性名是 `llm_model`，`payload` 里如果写成 `self.model` 会直接 `AttributeError`。已修正。

3. **`'message'` → `'messages'`**
   OpenAI 兼容接口的请求字段是 `messages`（复数）。写成单数会被服务端判为参数错误。已修正。

4. **`LLM_BASE_URL` 是完整地址**
   本项目 `.env` 里写的是 `https://api.siliconflow.cn/v1/chat/completions`，所以代码里 `requests.post(url=self.llm_base_url, ...)` 直接使用，不能再拼 `/chat/completions`，否则会变成 `.../chat/completions/chat/completions`。

5. **`from src.devagent...` 与 `from devagent...` 混用**
   与小结二第 4 条相同：`src` 不是包，会加载两份模块。当前测试脚本先能跑通，后续统一改为 `from devagent...`。

### 9. 验收清单

- [x] `.venv` 创建并激活，`python --version` 为 3.12.14；
- [x] `pip install -e .` 安装成功；
- [x] `.env` 三项配置能被 `settings` 正确读取；
- [x] `exceptions.py` 定义 `DevAgentBaseError` 和 `LLMRequestError`；
- [x] `LLMClient().chat(messages)` 能拿到模型返回；
- [x] 测试脚本能打印出模型回答；
- [ ] 重试机制真正生效（已知问题，待后续修正）；
- [ ] 导入路径统一为 `from devagent...`（待后续统一）。

### 10. 小结

小结三把「调用大模型」这件事收口到了一个类里：配置从 `settings` 来，请求走 `requests`，失败有 `tenacity` 兜底，异常统一成 `LLMRequestError`。

到这里，第一阶段的前三个小结完成：**环境 → 配置/异常 → 模型调用** 的最小链路已经打通。下一个小结（小结四）会把「工具」接进来，跑通第一条完整的问答链路。

---

## 小结四：第一个工具与最简问答链路

### 1. 本小结目标

把「读取本地文件」封装成一个工具函数，再写一个 `simple_qa.py`，把「读文件 → 拼提示词 → 调大模型 → 取回答」串成第一条完整的问答链路。

本小结产出：

- `src/devagent/tools/file_tools.py`：`read_file()` 工具；
- `simple_qa.py`：最简问答脚本；
- `test/file_tools_test.py`：工具测试脚本。

### 2. 工具的本质

大模型本身只能看到「你发给它的文本」，它看不到你电脑上的文件，也不能直接执行命令。所以需要工具：

> **工具本质上就是一个普通的 Python 函数**，负责替模型完成「本地才能做」的动作，比如读文件、搜代码、跑测试、查数据库。

本小结的链路是「手动调用工具」：

```text
用户问题
   │
   ▼
simple_qa.py 判断有没有传文件路径
   │
   ├── 有路径 ──▶ read_file() 读出文件内容
   │
   ▼
把「文件内容 + 问题」拼成 prompt
   │
   ▼
llm_client.chat(messages) 调用大模型
   │
   ▼
从返回 JSON 里取出回答，返回给用户
```

注意：这一小结里，**是代码决定要读哪个文件**，模型并不参与「选工具」的决策。让模型自己决定调用哪个工具，是第二阶段 Function Calling 的内容。

### 3. 创建 tools 包

在 `src/devagent/` 下新建 `tools/` 目录，并放入一个空的 `__init__.py`：

```text
src/devagent/
├── __init__.py
├── config.py
├── exceptions.py
├── llm_client.py
└── tools/
    ├── __init__.py
    └── file_tools.py
```

`__init__.py` 的作用是告诉 Python：`tools` 是一个可以导入的包。

### 4. 编写 `read_file` 工具

在 `src/devagent/tools/file_tools.py` 中写入：

```python
import os
from ..exceptions import DevAgentBaseError


def read_file(path):
    if not os.path.exists(path):
        raise DevAgentBaseError("File not found: {}".format(path))

    if not os.path.isfile(path):
        raise DevAgentBaseError("its not file: {}".format(path))

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content
    except Exception as e:
        raise DevAgentBaseError("文件读取失败: {}".format(e))
```

### 5. 逐块理解

**（1）先判断路径是否存在**

```python
if not os.path.exists(path):
    raise DevAgentBaseError("File not found: {}".format(path))
```

如果路径不存在，直接抛项目自己的异常，而不是让 `open()` 抛出一长串系统错误。

**（2）再判断是不是文件**

```python
if not os.path.isfile(path):
    raise DevAgentBaseError("its not file: {}".format(path))
```

路径存在，但可能是文件夹。`isfile()` 只对普通文件返回 `True`。

**（3）读取文件**

```python
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
```

- `encoding="utf-8"`：按 UTF-8 解码；
- `errors="ignore"`：遇到无法解码的字节就跳过，避免直接报错（代价是可能丢字符，后面处理二进制文件时要改进）；
- `with` 会自动关闭文件。

**（4）统一异常**

读取失败时包装成 `DevAgentBaseError`，这样上层只需要认项目自己的异常类型。

**（5）返回值**

`read_file()` 返回的是**字符串**，正好可以拼进 prompt。

### 6. 验证工具

在 `test/` 下新建 `file_tools_test.py`：

```python
from src.devagent.tools.file_tools import read_file

if __name__ == '__main__':
    content = read_file("/Users/mac/Documents/DevAgent/src/devagent/config.py")
    print(content)
```

在项目根目录运行：

```bash
python test/file_tools_test.py
```

预期结果：终端完整打印出 `config.py` 的内容。说明工具能正常读文件。

### 7. 编写最简问答脚本 `simple_qa.py`

在项目根目录新建 `simple_qa.py`：

```python
from src.devagent.tools.file_tools import read_file
from src.devagent.llm_client import llm_client


def simple_file_qa(question, path=None):
    if not path:
        content = ""
    else:
        print("正在读取文件。。。")
        content = read_file(path)

    print("正在调用大模型分析。。。")
    messages = [
        {
            "role":"user",
            "content":f"""
            请根据以下内容回答问题：
            文件内容：
            {content}
            问题：
            {question}
            """
        }
    ]

    result = llm_client.chat(messages)
    answers = result["choices"][0]["message"]["content"]
    return answers

if __name__ == '__main__':
    # ans = simple_file_qa(path = "/Users/mac/Documents/DevAgent/src/devagent/config.py", question="从最基础的底层原理解释一下这段代码，500字以内")
    ans2 = simple_file_qa(question="距离跨年还有几天")
    print(ans2)
```

### 8. 逐块理解

**（1）`path=None` 表示「不读文件」**

```python
def simple_file_qa(question, path=None):
    if not path:
        content = ""
```

`if not path` 同时覆盖 `None` 和空字符串两种情况，比 `if path == ""` 更稳。

**（2）有路径才调用工具**

```python
    else:
        print("正在读取文件。。。")
        content = read_file(path)
```

工具在这一步被手动调用，读到的内容存进 `content`。

**（3）把内容和问题拼成 prompt**

```python
    messages = [
        {
            "role":"user",
            "content":f"""
            请根据以下内容回答问题：
            文件内容：
            {content}
            问题：
            {question}
            """
        }
    ]
```

`f"""..."""` 会把 `content` 和 `question` 直接替换进字符串。这是最朴素的「检索增强」：先从本地拿到资料，再让模型基于资料回答。

**（4）调用大模型**

```python
    result = llm_client.chat(messages)
```

直接复用小结三封装好的全局单例 `llm_client`，不重复写网络请求。

**（5）从返回结果里取回答**

```python
    answers = result["choices"][0]["message"]["content"]
    return answers
```

OpenAI 兼容接口的返回结构：

```text
result["choices"][0]["message"]["content"]
        │            │          │        │
      候选列表     第 1 个     消息对象   正文
```

### 9. 验证两种用法

**用法一：带文件提问**

```python
ans = simple_file_qa(
    path="/Users/mac/Documents/DevAgent/src/devagent/config.py",
    question="从最基础的底层原理解释一下这段代码，500字以内",
)
print(ans)
```

预期结果：

```text
正在读取文件。。。
正在调用大模型分析。。。
（模型基于 config.py 内容给出的解释）
```

**用法二：不带文件，纯问答**

```python
ans2 = simple_file_qa(question="用一句话解释什么是 API 调用")
print(ans2)
```

预期结果：

```text
正在调用大模型分析。。。
（模型的直接回答）
```

在项目根目录运行：

```bash
python simple_qa.py
```

### 10. 本小结踩过的坑 / 已知问题

1. **参数顺序反了（已修）**
   最初定义是 `simple_file_qa(question, path="")`，调用却写成 `simple_file_qa("文件路径", "问题")`，导致 `question` 变成路径、`path` 变成问题，`read_file()` 直接抛 `File not found`。
   现在统一用关键字传参：

   ```python
   simple_file_qa(path="...", question="...")
   ```

   这样即使以后调整参数顺序也不会传错。

2. **无文件时 prompt 里仍有空的「文件内容：」**
   当前 `content = ""`，提示词会变成「文件内容：\n问题：...」。模型通常能理解，但容易答偏。后面可以给「有文件 / 无文件」准备两套提示词。学习阶段先不处理。

3. **文件内容一次性全塞进 prompt**
   `config.py` 这种小文件没问题；读大文件会超出上下文窗口，也会消耗大量 token。后续第三阶段做代码切块 / 检索时再解决。

4. **测试脚本的 `src` 导入问题**
   用 `python test/xxx.py` 运行时，`sys.path` 的第一项是 `test/`，可能出现：

   ```text
   ModuleNotFoundError: No module named 'src'
   ```

   临时办法：在项目根目录加 `PYTHONPATH=.` 运行，或改用：

   ```python
   from devagent.tools.file_tools import read_file
   ```

   因为项目已经 `pip install -e .`，`devagent` 包本身是可导入的。学习阶段先记录，后续统一调整导入路径。

5. **没有捕获异常、没有校验返回结构**
   `read_file()` 的 `DevAgentBaseError`、`llm_client` 的 `LLMRequestError` / `RetryError` 目前都会直接冒出来；`result["choices"][0]` 也假设结构一定正确。后面做 CLI 时再统一处理。

6. **`read_file` 可以读任意路径**
   现在传 `/etc/passwd` 也能读。作为本地学习脚本问题不大，后面接入 Web / Agent 工具时，必须限制在代码仓库根目录内。

7. **示例问题「距离跨年还有几天」不是工具问题**
   模型没有实时日期能力，也没有联网工具，答案不可靠。这属于测试用例选择，不是代码 bug。

### 11. 本小结验收清单

- [x] `tools/` 包和 `__init__.py` 创建完成；
- [x] `read_file()` 能读出 `config.py` 的内容；
- [x] `simple_file_qa(path=..., question=...)` 能基于文件回答；
- [x] `simple_file_qa(question=...)` 能不带文件直接回答；
- [x] 参数顺序已修正，统一使用关键字传参；
- [ ] 模型自动选择工具（第二阶段 Function Calling）；
- [ ] 大文件切块 / 检索（第三阶段 RAG）。

### 12. 小结

小结四把前面三块基础设施真正串了起来：

```text
环境与依赖
   │
配置 / 异常
   │
LLM 客户端
   │
本地工具 read_file
   │
simple_qa：问题 → 读文件 → 拼 prompt → 调模型 → 回答
```

第一阶段到这里完成（4/16）。当前能力边界：

- 工具是**代码手动调用**的，模型不参与决策；
- 文件内容**一次性**塞进 prompt，没有检索、没有分块；
- 没有会话记忆，每次问答都是独立的；
- 没有 CLI / Web 入口。

这正好对应下一阶段要解决的问题：

| 第二阶段小结 | 要解决的问题 |
| --- | --- |
| 工具标准化改造 | 给工具加名称、描述、参数说明，让模型「看得懂」 |
| Function Calling 核心逻辑 | 让模型自己决定调用哪个工具，手写调用循环 |
| 结构化输出与出处标注 | 回答里带上文件路径，方便核对 |
| CLI 命令行入口 | 终端直接 `devagent "问题"` |

---

# 第二阶段：规范篇——自动工具调用 Agent

第二阶段目标：从「代码手动调用工具」过渡到「模型自动决定调用工具」。

当前进度：工具注册表、Agent 框架已搭建，待完善 `llm_client` 对 `tools` 的支持并跑通闭环。

---

## 小结五：工具标准化改造

### 1. 本小结目标

给工具函数加上**元数据描述**，把工具封装成大模型能看懂的「说明书」，为后续 Function Calling 做准备。

### 2. 为什么要标准化

小结四里，工具是代码**手动**调用的：`simple_qa.py` 自己决定要不要读文件、读哪个文件。

到了第二阶段，我们要让**大模型自己决定**调用哪个工具、传什么参数。如果模型连「有哪些工具」都不知道，它就没法做决策。

所以第一步是：用统一的格式，把工具的「名字、作用、参数」描述清楚，再把这个描述发给大模型。

### 3. 工具注册表 `tool_registry.py`

在 `src/devagent/tools/` 新建 `tool_registry.py`：

```python
from .file_tools import read_file

# 所有工具的描述清单，格式严格遵循大模型 Function Calling 规范（OpenAI Tools 格式）
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地指定路径的文本文件内容，用于查看代码文件、配置文件等文本内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件的路径，可以是相对路径或绝对路径"
                    }
                },
                "required": ["file_path"]  # 必填参数
            }
        }
    }
]

# 工具名字 → 实际执行函数的映射表
# 大模型返回要调用的工具名，我们靠这个表找到真正要执行的函数
TOOL_FUNCTIONS = {
    "read_file": read_file
}
```

### 4. `TOOLS_DEFINITION` vs `TOOL_FUNCTIONS`

这两个概念是第二阶段最容易混淆的点，务必要分清：

| 名称 | 类型 | 用途 | 使用方 |
| --- | --- | --- | --- |
| `TOOLS_DEFINITION` | `list` | 工具的「说明书」（JSON Schema），描述工具名、描述、参数结构、必填项等 | 发给大模型（API 请求的 `tools` 字段） |
| `TOOL_FUNCTIONS` | `dict` | 工具名 → Python 实际函数的映射 | 我们自己的代码（解析到 `tool_calls` 后，用它找到真正要执行的函数） |

简单来说：**`TOOLS_DEFINITION` 是「告诉模型有啥」，`TOOL_FUNCTIONS` 是「代码怎么调」**。

### 5. `properties` 里的键名很关键

`parameters.properties` 里的每一个键名，就是**模型调用工具时实际传进来的参数名**。

大模型会严格按照这个 schema 生成 `arguments`：

```json
{"file_path": "/Users/mac/Documents/DevAgent/src/devagent/config.py"}
```

如果我们用 `TOOL_FUNCTIONS["read_file"](**tool_args)` 去调用，而 `read_file` 的函数形参是 `path`，就会报：

```text
TypeError: read_file() got an unexpected keyword argument 'file_path'
```

**结论：Schema 里的参数键名必须和函数的形参名完全一致。**

- **键名（如 `file_path`）**：决定能不能传进去（直接影响能否调用成功）
- **`description`（描述文字）**：只影响模型「要不要选这个工具」「用什么值」，不会影响 Python 传参

统一方式有三种：

1. **改 schema**：把 `file_path` 改成 `path`，和函数保持一致（最省事）
2. **改函数**：把 `read_file(path)` 改成 `read_file(file_path)`，和 schema 保持一致
3. **加参数映射**：在执行工具前，把 `{"file_path": ...}` 转成 `{"path": ...}` 再传入（最通用）

### 6. 小结

小结五只做一件事：**工具标准化**。把「普通 Python 函数」变成「带元数据的工具」，让模型有了「可用工具清单」。

---

## 小结六：Function Calling 核心逻辑

### 1. 本小结目标

搭建 `ToolAgent`，实现「模型自动决定是否调用工具 → 执行工具 → 把结果发回大模型 → 再次思考 → 给出最终答案」的最小闭环。

### 2. 为什么做这一步

小结四是「我问要不要读文件，我来决定」。小结六要变成「我问问题，模型自己决定要不要调工具、调哪个工具」。

这才是 Agent 的雏形：**从「命令式调用」走向「自主决策」**。

### 3. Agent 框架 `tool_agent.py`

在 `src/devagent/agent/` 下新建 `tool_agent.py`：

```python
import json
from devagent.llm_client import llm_client
from devagent.tools.tool_registry import TOOLS_DEFINITION, TOOL_FUNCTIONS

class ToolAgent:
    def __init__(self):
        self.system_prompt = """
        你是一个代码仓库助手，可以调用工具来读取本地文件，然后基于文件内容回答用户的问题。
规则：
1. 如果问题可以直接回答，就直接回答，不要调用工具
2. 如果需要读取文件才能回答，请调用 read_file 工具
3. 调用工具时，参数必须准确，文件路径要正确
4. 最终回答要基于工具返回的内容，不要编造信息
        """.strip()

    def run(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query},
        ]

        max_try = 5
        for _ in range(max_try):
            response = llm_client.chat(messages)
            assistant_msg = response["choices"][0]["message"]
            messages.append(assistant_msg)

            if "tool_calls" in assistant_msg and assistant_msg["tool_calls"] is not None:
                tool_calls = assistant_msg["tool_calls"]

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]
                    tool_call_id = tool_call["id"]

                    tool_args = json.loads(tool_args_str)
                    tool_result = TOOL_FUNCTIONS[tool_name](**tool_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_result
                    })
                continue
            else:
                return assistant_msg["content"]

        return "已达到最大思考轮次，未能完成回答。"


tool_agent = ToolAgent()
```

### 4. 外层循环流程

整个 `run` 方法用 `for` 循环模拟「多轮思考」：

```text
轮次 1
├── 把 [system, user] 发给大模型
├── 拿到 assistant_msg，追加到 messages
└── 如果有 tool_calls → 执行工具 → 追加 role:"tool" 消息 → continue（不返回，进入下一轮）

轮次 2
├── 把 [system, user, assistant(tool_calls), tool(结果)] 全量发给大模型
├── 拿到 assistant_msg，追加到 messages
└── 如果无 tool_calls → return assistant_msg["content"]（最终回答）
```

关键点：

- **每一轮都发全量 `messages`**：大模型需要看到「之前想干啥」「刚才调用了什么工具」「工具返回了什么」，才能接着思考并给出答案。
- **`continue` 的作用**：跳过本轮剩余代码，直接进入下一次循环。意思是「工具已处理完，再开一回合让大模型思考」。
- **`max_try = 5`**：限制最大轮次，防止模型一直调用工具导致死循环。
- **正常场景大多是 1～2 轮**：要用工具就至少 2 轮（决定调用 + 基于结果回答），不需要工具就 1 轮直接返回。

### 5. `json.loads` 和 `**` 解包

大模型返回的 `tool_calls[].function.arguments` 是 **JSON 字符串**，而不是 Python 字典：

```python
tool_args_str = tool_call["function"]["arguments"]  # '{"file_path": "..."}'
tool_args = json.loads(tool_args_str)               # {"file_path": "..."}
tool_result = TOOL_FUNCTIONS[tool_name](**tool_args) # 解包成关键字参数
```

- `json.loads()`：**解析**，把 JSON 字符串还原成 Python 数据结构
- `**tool_args`：**字典解包**，把字典的键值对拆成 `key=value` 形式传给函数

### 6. 测试与当前 Bug

用 `test/test_tool_agent.py` 测试时，模型返回了 XML 而不是标准的 `tool_calls`：

```xml
<tool_call>
<function=read_file>
<parameter=path>
src/devagent/config.py
</parameter>
</function>
</tool_call>
```

这说明 **Function Calling 协议没生效**。

原因：

| Bug | 分析 | 修复思路 |
| --- | --- | --- |
| **1. `llm_client.chat` 没支持 `tools`** | 现在只拼 `messages`、`model`，请求里完全没有 `tools` 字段。 | 给 `chat` 加 `tools=None, tool_choice="auto", temperature=0.1` 参数，传入时加入 `payload["tools"]`、`payload["tool_choice"]` |
| **2. `ToolAgent` 没传 `tools`** | `llm_client.chat(messages)` 没传工具定义，大模型根本不知道有这个工具。 | 改成 `llm_client.chat(messages, tools=TOOLS_DEFINITION, tool_choice="auto")` |
| **3. 用错映射表** | 现在代码里有 `TOOLS_DEFINITION[tool_name](**tool_args_str)` 的写法，`TOOLS_DEFINITION` 是列表不是函数映射表。 | 改用 `TOOL_FUNCTIONS[tool_name](**tool_args)`，且要先 `json.loads` 再解包 |
| **4. 参数名不一致** | `tool_registry` 用 `file_path`，`read_file` 用 `path`，会导致 `TypeError`。 | 两边统一（要么都用 `path`，要么都用 `file_path`，或加参数映射） |
| **5. 未处理工具异常** | 工具抛异常会直接中断整个循环。 | 用 `try/except` 捕获，转成字符串（如 `"工具执行出错：..."`）放进 `role: "tool"` 的 `content`，让模型根据错误信息决定下一步 |

**核心结论：只有在请求里带上 `tools=[...]`，OpenAI 兼容接口才会走 Function Calling，才会返回 `message.tool_calls`（JSON 格式）。不传的话，大模型只会用它自己习惯的方式“模拟”工具调用（比如 XML）。**

### 7. 本小结验收清单

- [x] `tool_registry.py` 创建完成，`TOOLS_DEFINITION` 和 `TOOL_FUNCTIONS` 都有定义
- [x] `ToolAgent` 框架搭建完成（消息历史、循环、工具调用、结果回传）
- [x] 理解 `json.loads` + `**`、循环 + `continue`、全量消息历史的逻辑
- [ ] `llm_client.chat` 支持 `tools` 并传入请求
- [ ] `ToolAgent` 正确用 `TOOL_FUNCTIONS` 调用工具、解析 `tool_calls`
- [ ] 参数名统一，能成功跑通「问文件 → 调用工具 → 回答」闭环
- [ ] 工具异常有兜底处理

### 8. 小结

小结六标志着从「手动调用工具」到「自动工具调用」的思路转变：

```text
小结四：代码说「要读文件」→ 调用 read_file → 拼 prompt → 回答（命令式）
小结六：大模型说「要读文件」→ 解析 tool_calls → 调用 read_file → 把结果发回去 → 大模型回答（决策式）
```

现在的最大差距就是**没把 `tools` 真正发出去**。等把 `llm_client` 和 `ToolAgent` 修好，模型就能按 OpenAI Function Calling 的规范返回 `tool_calls`，整个 Agent 才能真正跑起来。

当前状态：**理论走通，代码闭环待修复**。
