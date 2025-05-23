# 豆瓣观影记录爬虫

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
  - 采集电影详细信息（标题、链接、观看时间、简介、评价）
  - CSV格式保存数据
  - 详细的运行状态日志
- 断点续传功能：
  - 自动保存采集进度
  - 支持中断后继续采集
  - 临时文件自动清理
- 异常处理和调试：
  - 登录失败自动保存截图
  - 保存页面源码便于分析
  - 完整的错误提示

## 环境准备

1. 下载Chrome浏览器驱动
   - 访问 [ChromeDriver下载页面](https://chromedriver.chromium.org/downloads)
   - 下载与您的Chrome浏览器版本匹配的驱动程序
   - 将驱动程序放置在指定位置（如：D:\Program Files (x86)\chromedriver-win64\chromedriver.exe）

2. 配置驱动路径
   - 打开 `douban.py` 文件
   - 修改 `CHROME_DRIVER_PATH` 变量为您的实际驱动程序路径

## 使用方法

1. 运行程序
   ```bash
   python douban.py
   ```

2. 手动登录
   - 程序会自动打开浏览器
   - 在打开的页面中完成登录操作（最好使用扫码登录）
   - 登录成功后会自动跳转到个人主页

3. 数据采集
   - 程序会自动开始采集观影记录
   - 采集过程中会显示实时进度
   - 如果程序中断，重新运行时会从上次进度继续

## 输出文件

- 观影数据：`douban_watched_2025.csv`
  - 包含字段：序号、电影名称、豆瓣链接、观看时间、电影简介、评价内容
  - 使用UTF-8编码，支持中文显示
- 临时文件（采集过程中）：
  - `douban_progress.txt`：当前采集进度 里面的数字是第几页
  - `douban_watched_temp.csv`：临时数据文件
- 调试文件（仅在登录失败时生成）：
  - `login_fail.png`：登录失败时的页面截图
  - `login_page.html`：登录页面的源代码

## 注意事项

1. 确保Chrome浏览器已安装并且版本与驱动程序匹配
2. 首次运行时需要手动完成登录操作
3. 采集过程中请勿关闭浏览器窗口
4. 如果程序中断，可以直接重新运行，会自动继续上次的采集进度
5. 采集完成后，临时文件会自动清理