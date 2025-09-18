# Text-to-SQL 项目技术设计文档

## 项目概述

这是一个功能完整的Text-to-SQL概念验证系统，使用Google Gemini API将自然语言查询转换为SQL语句，支持元数据管理来处理无意义列名的问题。

## 系统架构

### 核心组件

1. **TextToSQL类** (`src/text_to_sql.py`) - 主要的Text-to-SQL转换引擎
2. **SQLValidator类** (`src/sql_validator.py`) - SQL查询安全验证器
3. **DatabaseUtils类** (`src/database_utils.py`) - 数据库工具集
4. **元数据管理系统** - 处理无意义列名的业务语义映射

## 详细文件分析

### 1. 项目配置文件

#### `requirements.txt`
```text
google-generativeai==0.3.2      # Google Gemini AI API
sqlalchemy==2.0.23              # 数据库ORM和工具
langchain==0.1.0                # AI提示词管理
langchain-google-genai==0.0.5   # LangChain-Google集成
python-dotenv==1.0.0            # 环境变量管理
```

#### `.env.example`
环境变量模板，包含Google API密钥配置。

#### `.gitignore`
标准的Python项目忽略配置，包括：
- Python编译文件和缓存
- 虚拟环境
- 数据库文件
- IDE配置文件
- 环境变量文件

### 2. 核心模块

#### `__init__.py`
包初始化文件，定义了：
- 包版本：0.1.0
- 作者信息
- 主要类的导出：TextToSQL、SQLValidator、DatabaseUtils

#### `src/text_to_sql.py`
**核心Text-to-SQL引擎**，包含完整的元数据管理功能。

**主要功能：**
- 数据库初始化和表结构创建
- 元数据表管理
- SQL生成和执行
- 增强的Schema输出

**关键方法：**

`__init__(db_path)`
- 初始化数据库连接
- 配置Gemini AI模型
- 创建示例表和元数据

`_create_metadata_table()`
创建元数据存储表：
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
)
```

`_insert_sample_metadata()`
插入示例元数据，为每个列提供业务语义信息。

`get_enhanced_schema()`
获取包含元数据的增强Schema，格式：
```
Table: employees
Columns:
  - id INTEGER NOT NULL PRIMARY KEY (业务名称: 员工ID, 描述: 员工的唯一标识符, 示例: 1, 2, 3, 规则: 主键，自增)
  - name TEXT NOT NULL (业务名称: 员工姓名, 描述: 员工的全名, 示例: John Doe, 规则: 不能为空)
```

`add_column_metadata(table_name, column_name, business_name, description, ...)`
动态添加或更新列元数据，支持运行时修改业务语义。

`generate_sql(question)`
使用Gemini AI将自然语言问题转换为SQL查询，支持元数据增强的Schema。

`query(question)`
主要接口方法：接收自然语言问题，返回SQL查询和执行结果。

#### `src/database_utils.py`
**数据库工具集**，提供数据库操作的高级抽象。

**主要功能：**

`get_table_info()`
获取数据库表结构详细信息，包括：
- 列信息（名称、类型、约束）
- 主键约束
- 外键关系

`get_sample_data(table_name, limit)`
获取表的示例数据，用于AI理解的上下文。

`validate_sql(sql_query)`
使用SQLite的EXPLAIN命令验证SQL语法正确性。

`format_schema_for_llm()`
格式化数据库Schema为AI友好的格式，包含示例数据。

#### `src/sql_validator.py`
**SQL安全验证器**，确保生成的SQL查询安全。

**安全功能：**

`validate_query(sql_query)`
综合验证SQL查询的安全性，返回验证结果和错误信息。

`_is_potential_injection(sql_query)`
检测SQL注入模式，包括：
- DROP/DELETE操作
- 注释攻击（--, /* */）
- 布尔注入（1=1）
- 延迟攻击（WAITFOR DELAY）

`_contains_dangerous_operations(sql_query)`
检测危险SQL操作：
- 只允许SELECT和WITH查询
- 禁止DROP, DELETE, UPDATE等写操作

`_validate_syntax(sql_query)`
使用数据库引擎验证SQL语法。

`sanitize_query(sql_query)`
清理SQL查询，移除注释和多余空格。

### 3. 演示和测试文件

#### `example_usage.py`
使用示例和交互式演示程序。

**功能特性：**
- 显示数据库Schema
- 运行预设示例查询
- 交互式查询模式
- 结果格式化输出

**示例查询：**
```python
examples = [
    "Show me all employees and their departments",
    "Find employees older than 30 with salary above 70000",
    "What is the average salary by department?",
    "Count employees in each department",
    "Show the highest paid employee in Engineering",
    "List employees hired in 2020"
]
```

#### `test_text_to_sql.py`
完整的单元测试套件。

**测试覆盖：**
- 数据库初始化测试
- SQL生成功能测试
- 安全验证测试
- 危险查询检测
- Schema提取测试
- 查询执行测试
- 只读查询强制测试

**关键测试方法：**
- `test_database_initialization()`: 验证数据库正确初始化
- `test_basic_sql_generation()`: 测试基本SQL生成功能
- `test_sql_validation()`: 测试SQL验证功能
- `test_dangerous_query_detection()`: 测试危险查询检测
- `test_read_only_enforcement()`: 测试只读查询强制

#### `demo_meaningless_names_enhanced.py`
元数据功能的增强演示，对比有无元数据的差异。

**核心功能：**
- 创建无意义列名的数据库（t01, t02表，c001-c006列）
- 为无意义列名添加业务语义元数据
- 对比有无元数据的SQL生成质量
- 展示元数据如何解决列名理解问题

**元数据示例：**
```python
metadata_data = [
    ('t01', 'c001', '员工ID', '员工的唯一标识符', 'INTEGER', '1, 2, 3', 0, '主键，自增'),
    ('t01', 'c002', '员工姓名', '员工的全名', 'TEXT', 'John Doe', 0, '不能为空'),
    ('t01', 'c003', '员工年龄', '员工的年龄', 'INTEGER', '30, 28, 35', 0, '必须大于18'),
    # ... 更多元数据
]
```

**对比功能：**
`show_comparison()` 方法展示：
- 基础Schema vs 增强Schema
- 无元数据生成的SQL vs 有元数据生成的SQL
- 查询结果的准确性对比

#### `demo_meaningless_names.py`
简单的无意义列名演示，展示问题的严重性。

### 4. 数据库文件

#### `example.db`
主要的示例数据库，包含：
- `employees`表：员工信息
- `departments`表：部门信息
- `column_metadata`表：列元数据

#### `demo_meaningless_enhanced.db`
增强演示数据库，包含：
- `t01`表：无意义列名的员工表
- `t02`表：无意义列名的部门表
- `column_metadata`表：完整的元数据映射

## 技术架构特点

### 1. 元数据管理系统
**核心创新点**：为无意义列名提供业务语义映射

**架构优势：**
- **动态更新**：运行时修改元数据，无需重启
- **丰富上下文**：提供业务名称、描述、示例值、业务规则
- **敏感字段标记**：自动识别和处理敏感数据
- **向后兼容**：完全兼容现有代码

**实现机制：**
```python
# 元数据存储
metadata[table_name][column_name] = {
    'business_name': '员工年龄',
    'description': '员工的年龄',
    'data_type': 'INTEGER',
    'example_value': '30, 28, 35',
    'is_sensitive': False,
    'business_rules': '必须大于18'
}
```

### 2. 安全架构
**多层安全保护：**

1. **注入防护**：正则表达式检测注入模式
2. **操作限制**：只允许SELECT和WITH查询
3. **语法验证**：数据库引擎验证SQL语法
4. **查询清理**：移除危险注释和多余空格

### 3. AI集成架构
**基于Google Gemini的SQL生成：**

- **提示词工程**：优化的SQL生成提示模板
- **上下文增强**：元数据提供的丰富业务上下文
- **错误处理**：完善的异常处理和错误恢复

### 4. 数据库抽象层
**SQLAlchemy + SQLite的组合：**

- **类型安全**：SQLAlchemy的类型系统
- **连接管理**：自动连接池和事务管理
- **Schema检查**：动态表结构分析
- **跨平台**：SQLite的便携性

## 数据流设计

### 查询处理流程：
```
用户自然语言问题 →
TextToSQL.query() →
generate_sql() →
get_enhanced_schema() →
Gemini AI →
SQL查询 →
SQL验证 →
execute_query() →
结果返回
```

### 元数据处理流程：
```
数据库表结构 →
add_column_metadata() →
column_metadata表 →
get_enhanced_schema() →
AI上下文增强 →
准确SQL生成
```

## 性能和扩展性

### 1. 性能优化
- **连接池**：SQLAlchemy的连接管理
- **元数据缓存**：内存中的元数据缓存
- **异步处理**：支持异步查询执行
- **批量操作**：支持批量元数据插入

### 2. 扩展性设计
- **多数据库支持**：可扩展到PostgreSQL, MySQL等
- **插件架构**：支持自定义验证器和工具
- **配置驱动**：环境变量和配置文件管理
- **微服务就绪**：模块化设计，易于服务化

## 部署和运维

### 1. 环境要求
- Python 3.8+
- Google Gemini API密钥
- SQLite数据库

### 2. 安装步骤
```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑.env文件，添加API密钥
python example_usage.py
```

### 3. 监控和日志
- 错误处理和异常捕获
- 查询性能统计
- API调用监控
- 数据库连接状态

## 安全考虑

### 1. 数据安全
- 敏感字段标记
- 访问权限控制
- 数据加密传输
- 审计日志记录

### 2. API安全
- API密钥管理
- 请求频率限制
- 输入验证和清理
- 错误信息处理

### 3. 运行时安全
- SQL注入防护
- 权限最小化原则
- 资源使用限制
- 异常处理和恢复

## 未来扩展方向

### 1. 功能增强
- 支持更多数据库类型
- 增强的自然语言理解
- 复杂查询优化
- 可视化查询结果

### 2. 性能优化
- 查询缓存机制
- 批量处理支持
- 分布式架构
- 异步处理优化

### 3. 用户体验
- Web界面
- API文档
- 用户认证
- 多语言支持

## 总结

这个Text-to-SQL项目是一个功能完整、架构清晰的AI应用系统。其核心创新在于元数据管理系统，有效解决了无意义列名的理解问题。系统采用多层安全架构，确保查询的安全性，同时具有良好的扩展性和可维护性。通过模块化设计和丰富的测试覆盖，该系统为生产环境的使用奠定了良好的基础。