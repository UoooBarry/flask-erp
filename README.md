# Flask 进销存管理系统 (ERP)

一个基于 Flask 的现代化企业资源规划(ERP)演示系统，展示完整的企业级应用开发能力。

## 项目简介

本项目是一个功能完善的进销存管理系统，采用现代化的技术栈和最佳实践构建。项目展示了从数据库设计、API开发、用户认证、权限控制到自动化测试的完整开发流程，适合作为技术面试和求职展示的演示项目。

## 技术亮点

### 🎯 核心技术栈
- **后端框架**: Flask (Python)
- **ORM**: SQLAlchemy 2.0+ (数据类风格模型)
- **数据库**: SQLite (可轻松切换到 PostgreSQL/MySQL)
- **认证**: JWT (JSON Web Token) 无状态认证
- **API 设计**: RESTful API 设计
- **测试框架**: pytest 完整测试覆盖

### ✨ 架构设计

#### 1. 现代化 ORM 模型设计
```python
# 使用 SQLAlchemy 2.0+ 的数据类风格
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
```
- 类型安全的字段定义
- 自动时间戳管理 (`created_at`, `updated_at`)
- 清晰的关系映射
- 数据类风格的初始化

#### 2. 统一的 API 响应和错误处理系统
```python
# 成功响应
return render_success({"id": 1}, meta_data={"total": 100})

# 异常处理
raise ValidationError("输入数据无效")
raise NotFoundError("用户不存在")
```
- 统一的响应格式
- 自定义异常类体系
- 自动捕获数据库验证错误 (IntegrityError → 422)
- 全局错误处理器中间件
- 自动化错误日志记录

#### 3. 基于角色的权限控制系统 (RBAC)
- 多对多用户-角色关系
- 细粒度权限管理 (蓝图表、端点、方法级别)
- JWT Token 携带角色信息
- 装饰器式权限验证
- 自动权限发现机制

#### 4. 安全最佳实践
- 密码哈希存储 (Werkzeug Security)
- JWT Token 过期控制
- 环境变量管理 (python-dotenv)
- SQL 注入防护 (ORM 参数化查询)
- CORS 支持 (可选配置)

### 🗄️ 数据库设计

#### 核心表结构
- **users** - 用户表 (用户名、密码哈希)
- **roles** - 角色表 (角色名称)
- **user_roles** - 用户-角色关联表
- **role_permissions** - 角色权限表 (角色、蓝图表、端点、方法)

#### 关系设计
- 用户 ↔ 角色: 多对多关系
- 自动级联删除
- 索引优化 (username 唯一索引、角色权限复合索引)
- 外键约束保证数据完整性

### 🔐 认证与授权

#### JWT 认证流程
1. 用户登录验证
2. 生成包含用户 ID 和角色的 JWT Token
3. 客户端请求携带 Token
4. 服务端验证 Token 并提取用户信息

#### 权限验证
```python
@permission_required()
def protected_view():
    # 自动验证用户权限
    return render_success({"data": "敏感数据"})
```
- 声明式权限验证
- 自动权限检查
- 无权限自动返回 403

### 🧪 测试体系

#### 测试覆盖
- **单元测试**: 模型层测试 (用户创建、密码哈希、约束验证)
- **集成测试**: API 端点测试、装饰器测试
- **错误处理测试**: 异常捕获和响应格式测试
- **数据库测试**: IntegrityError、StatementError 处理

#### 测试特性
- pytest 框架
- 数据库回滚机制
- Application Context 管理
- 35+ 个测试用例，100% 通过率

### 📦 API 设计

#### RESTful API 示例
```
POST   /auth/login           # 用户登录
GET    /users               # 获取用户列表
POST   /users               # 创建用户
GET    /users/:id           # 获取单个用户
PUT    /users/:id           # 更新用户
DELETE /users/:id           # 删除用户
```

#### 统一响应格式

**成功响应**
```json
{
  "success": true,
  "data": { "id": 1, "username": "admin" },
  "meta": { "total": 100, "page": 1 }
}
```

**错误响应**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": { "username": "Username is required" }
}
```

### 🚀 开发工具链

#### 项目结构
```
flask-erp/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # API 路由
│   ├── utils/           # 工具类 (异常处理、响应、装饰器)
│   └── extensions.py   # 数据库和扩展初始化
├── tests/              # 测试套件
├── migrations/         # 数据库迁移
└── config.py          # 环境配置
```

#### 开发命令
```bash
# 运行应用
flask run

# 数据库迁移
flask db migrate
flask db upgrade

# 运行测试
pytest                          # 所有测试
pytest tests/test_user_model.py   # 单个测试文件
pytest tests/test_user_model.py::TestUserModel::test_user_creation  # 单个测试

# 数据库初始化
python seeds.py
```

### 🎨 代码质量

#### 代码风格
- **PEP 8** 规范
- 类型提示
- 文档字符串
- 清晰的命名约定
- 模块化设计

#### 设计模式
- **Blueprint** - 路由模块化
- **Repository Pattern** - 数据访问抽象
- **Decorator Pattern** - 权限验证
- **Middleware Pattern** - 错误处理

## 快速开始

### 环境要求
- Python 3.14+
- pip / poetry

### 安装步骤
```bash
# 克隆项目
git clone https://github.com/yourusername/flask-erp.git
cd flask-erp

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件设置 SECRET_KEY

# 初始化数据库
flask db upgrade
python seeds.py

# 运行应用
flask run
```

### 测试项目
```bash
# 运行所有测试
pytest

# 查看测试覆盖率
pytest --cov=app
```

## 未来规划

- [ ] 实现 REST API 文档 (Swagger/OpenAPI)
- [ ] 添加用户个人资料管理
- [ ] 实现权限管理后台界面
- [ ] 添加数据导入导出功能
- [ ] 集成 Celery 异步任务
- [ ] 添加 Redis 缓存层
- [ ] 实现实时通知系统
- [ ] 部署到云服务 (AWS/Azure)
- [ ] 添加 Docker 容器化
- [ ] 集成 CI/CD 流程
