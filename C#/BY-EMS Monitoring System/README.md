# BY-EMS 监控系统

## 项目结构

- **Models**: 存放数据模型类
- **Views**: 存放视图文件（XAML）
- **ViewModels**: 存放视图模型类
- **Services**: 存放服务类，处理数据获取逻辑

## 依赖管理

- 使用 NuGet 安装必要的库，例如 MVVM Light 或 Prism。

## 数据获取逻辑

- 参考之前的 Python 代码，设计一个服务类来处理数据获取逻辑。
- 使用 `HttpClient` 或 WebSocket 客户端与后端建立连接。

## UI 设计

- 使用 XAML 设计窗口，确保 UI 友好且响应迅速。
- 使用 `DataBinding` 将数据与 UI 组件连接。

## 日志记录

- 实现日志记录功能，方便调试和监控系统运行状态。
