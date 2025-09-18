# Text-to-SQL Proof of Concept

一个简单但功能完整的Text-to-SQL系统，使用OpenAI的API将自然语言查询转换为SQL语句。

## 功能特性

- 🤖 基于OpenAI GPT的自然语言到SQL转换
- 🗄️ 支持SQLite数据库
- 🔒 SQL查询安全验证
- 📊 自动数据库模式提取
- 🧪 完整的测试套件
- 🎯 简单易用的API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的OpenAI API密钥
```

### 3. 运行示例

```bash
python example_usage.py
```

### 4. 运行测试

```bash
python test_text_to_sql.py
```

## 使用示例

```python
from src.text_to_sql import TextToSQL

# 初始化
text_to_sql = TextToSQL()

# 查询
result = text_to_sql.query("Show me all employees older than 30")

print(f"SQL: {result['sql_query']}")
print(f"Results: {result['results']}")
```

## 支持的查询类型

- 基本的SELECT查询
- WHERE条件过滤
- JOIN操作
- 聚合函数 (COUNT, AVG, SUM, etc.)
- GROUP BY操作
- 排序 (ORDER BY)

## 安全特性

- SQL注入防护
- 危险操作检测
- 只读查询强制
- 语法验证

## 项目结构

```
Text-to-SQL/
├── src/
│   ├── text_to_sql.py      # 主要的Text-to-SQL类
│   ├── sql_validator.py    # SQL验证器
│   └── database_utils.py   # 数据库工具类
├── test_text_to_sql.py     # 测试文件
├── example_usage.py        # 使用示例
├── requirements.txt        # 依赖包
└── README.md               # 文档
```

## API参考

### TextToSQL类

- `__init__(db_path)`: 初始化Text-to-SQL系统
- `query(question)`: 将自然语言转换为SQL并执行
- `generate_sql(question)`: 仅生成SQL查询
- `execute_query(sql)`: 执行SQL查询

### SQLValidator类

- `validate_query(sql)`: 验证SQL查询的安全性
- `is_read_only_query(sql)`: 检查是否为只读查询

## 许可证

MIT License