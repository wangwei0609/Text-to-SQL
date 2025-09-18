# Text-to-SQL Proof of Concept

一个功能完整的Text-to-SQL系统，使用Google Gemini的API将自然语言查询转换为SQL语句，支持元数据管理来处理无意义列名。

## 功能特性

- 🤖 基于Google Gemini的自然语言到SQL转换
- 🗄️ 支持SQLite数据库
- 🔒 SQL查询安全验证
- 📊 自动数据库模式提取
- 🧪 完整的测试套件
- 🎯 简单易用的API
- 📋 **元数据管理系统** - 为无意义列名提供业务语义
- 🔄 **动态元数据更新** - 无需重启应用即可更新列含义
- 📊 **增强Schema输出** - 包含业务描述和示例值

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的Google API密钥
```

### 3. 运行示例

```bash
python example_usage.py
```

### 4. 运行测试

```bash
python test_text_to_sql.py
```

### 5. 演示元数据功能

```bash
# 演示元数据如何帮助处理无意义列名
python demo_meaningless_names_enhanced.py
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

## 元数据管理系统

### 什么是元数据？

元数据管理系统为数据库中的列提供业务语义信息，即使面对无意义的列名（如`c001`, `t01`），系统仍能准确理解用户意图。

### 元数据表结构

```sql
CREATE TABLE column_metadata (
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    business_name TEXT,        -- 业务名称
    description TEXT,          -- 详细描述
    data_type TEXT,           -- 数据格式说明
    example_value TEXT,       -- 示例值
    is_sensitive BOOLEAN,     -- 是否敏感字段
    business_rules TEXT,      -- 业务规则
    PRIMARY KEY (table_name, column_name)
);
```

### 使用示例

```python
# 添加列的元数据
text_to_sql.add_column_metadata(
    table_name="t01",
    column_name="c003",
    business_name="员工年龄",
    description="员工的年龄",
    example_value="30, 28, 35",
    business_rules="必须大于18"
)

# 获取增强的schema（包含元数据）
enhanced_schema = text_to_sql.get_enhanced_schema()
print(enhanced_schema)

# 即使是无意义的列名，系统仍能正确理解
result = text_to_sql.query("Find employees older than 30")
```

### 元数据功能特性

- **动态更新**: 无需重启应用即可添加/修改元数据
- **丰富上下文**: 提供业务名称、描述、示例值、业务规则
- **敏感字段标记**: 自动识别和处理敏感数据
- **向后兼容**: 完全兼容现有代码

## 安全特性

- SQL注入防护
- 危险操作检测
- 只读查询强制
- 语法验证

## 项目结构

```
Text-to-SQL/
├── src/
│   └── text_to_sql.py      # 主要的Text-to-SQL类（含元数据管理）
├── test_text_to_sql.py     # 测试文件
├── example_usage.py        # 使用示例
├── demo_meaningless_names_enhanced.py  # 元数据功能演示
├── requirements.txt        # 依赖包
├── .env.example           # 环境变量模板
└── README.md               # 文档
```

## API参考

### TextToSQL类

#### 核心方法

- `__init__(db_path)`: 初始化Text-to-SQL系统
- `query(question)`: 将自然语言转换为SQL并执行
- `generate_sql(question)`: 仅生成SQL查询
- `execute_query(sql)`: 执行SQL查询

#### 元数据管理方法

- `get_enhanced_schema()`: 获取包含元数据的增强schema
- `add_column_metadata(table_name, column_name, business_name, description, ...)`: 添加列元数据
- `remove_column_metadata(table_name, column_name)`: 删除列元数据
- `get_column_metadata()`: 获取所有元数据

### 元数据表结构

元数据存储在`column_metadata`表中，包含以下字段：

- `table_name`: 表名
- `column_name`: 列名
- `business_name`: 业务名称（如"员工年龄"）
- `description`: 详细描述
- `data_type`: 数据类型说明
- `example_value`: 示例值
- `is_sensitive`: 是否敏感字段
- `business_rules`: 业务规则

## 许可证

MIT License
