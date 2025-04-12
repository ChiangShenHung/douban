# 豆瓣观影记录爬虫

这是一个基于Python的豆瓣电影爬虫程序，用于获取用户的观影记录数据。程序使用Selenium进行页面操作，支持手动登录和验证码处理，采用多重反爬虫策略确保数据采集的稳定性。本代码采用元宝Deepseek R1 + Trae AI辅助开发，个人在项目中承担指出具体问题（如：提出使用手动登录之后再自动采集）以及分析影片列表在页面中的格式、翻页功能方法的实现指导以及后续功能调试测试。

## 功能特点

- 支持手动登录和验证码处理，避免自动登录失败问题
- 多重反爬虫策略：
  - 修改浏览器指纹
  - 禁用自动化特征
  - 自定义用户代理
  - 随机延迟请求
- 智能处理页面元素：
  - 自动关闭广告弹窗
  - 平滑滚动页面
  - 等待页面加载完成
- 数据采集和导出：
  - 支持批量获取观影记录
  - CSV格式保存数据
  - 详细的运行状态日志
- 异常处理和调试：
  - 登录失败自动保存截图
  - 保存页面源码便于分析
  - 完整的错误提示

## 安装依赖

```bash
pip install selenium beautifulsoup4
```

## 环境准备

1. 下载Chrome浏览器驱动
   - 访问 [ChromeDriver下载页面](https://chromedriver.chromium.org/downloads)
   - 下载与您的Chrome浏览器版本匹配的驱动程序
   - 将驱动程序放置在指定位置（如：D:\Program Files (x86)\chromedriver-win64\chromedriver.exe）

2. 配置驱动路径
   - 打开 `douban.py` 文件
   - 修改 `CHROME_DRIVER_PATH` 变量为您的实际驱动程序路径

## 使用方法

1. 运行爬虫程序
   ```bash
   python douban.py
   ```

2. 登录流程
   - 程序会自动打开浏览器并导航到豆瓣登录页面
   - 手动完成登录操作（包括可能出现的验证码）
   - 系统会自动验证登录状态，成功后开始数据采集
   - 采集过程中会显示实时进度

## 输出文件

- 观影数据：`douban_watched_2025.csv`
  - 包含字段：序号、电影名称、采集时间
  - 使用UTF-8编码，支持中文显示
- 调试文件（仅在登录失败时生成）：
  - `login_fail.png`：登录失败时的页面截图
  - `login_page.html`：登录页面的源代码

## 注意事项

1. 确保Chrome浏览器版本与驱动程序版本匹配
2. 首次运行需要手动登录并处理验证码
3. 程序会自动处理页面弹窗和广告，无需手动干预
4. 采集过程中请勿关闭浏览器窗口
5. 数据采集包含随机延迟，请耐心等待完成
6. 程序运行完成后，按任意键关闭浏览器