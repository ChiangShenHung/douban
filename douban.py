# 导入所需的Python模块
# selenium相关模块用于自动化操作浏览器
from selenium import webdriver  # 浏览器自动化的核心模块
from selenium.webdriver.common.by import By  # 定位元素的方法
from selenium.webdriver.support.ui import WebDriverWait  # 显式等待
from selenium.webdriver.support import expected_conditions as EC  # 预期条件
from selenium.webdriver.chrome.service import Service  # Chrome浏览器服务
from selenium.webdriver.chrome.options import Options  # Chrome浏览器配置选项
from bs4 import BeautifulSoup  # 用于解析HTML页面
import time  # 处理时间相关操作
import csv  # 处理CSV文件
import random  # 生成随机数
import os  # 操作系统相关功能

# 全局配置参数
CHROME_DRIVER_PATH = r"D:\Program Files (x86)\chromedriver-win64\chromedriver.exe"  # Chrome驱动程序路径
OUTPUT_FILE = "douban_watched_2025.csv"  # 输出文件名
LOGIN_TIMEOUT = 300  # 手动登录超时时间（秒）

class DoubanWatchedSpider:
    """
    豆瓣观影记录爬虫类
    用于自动获取用户的豆瓣观影记录，并将数据保存到CSV文件中
    包含反爬虫策略、登录验证、数据抓取等功能
    """
    def __init__(self):
        """
        初始化爬虫实例
        设置浏览器选项、创建浏览器实例、配置等待时间、设置浏览器指纹
        """
        options = self._init_browser_options()
        service = Service(executable_path=CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)  # 设置显式等待时间为15秒
        self._setup_browser_fingerprint()
        
    def _init_browser_options(self):
        """
        初始化Chrome浏览器的配置选项
        包括禁用自动化控制特征、设置窗口大小和用户代理等
        返回：配置好的Chrome选项对象
        """
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制特征
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 排除自动化开关
        options.add_experimental_option("useAutomationExtension", False)  # 禁用自动化扩展
        options.add_argument("--window-size=1280,720")  # 设置窗口大小
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # 设置用户代理
        return options

    def _setup_browser_fingerprint(self):
        """
        设置浏览器指纹，进一步增强反爬虫能力
        通过修改navigator和window对象来伪装浏览器特征
        """
        # 覆盖用户代理
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        # 注入JavaScript代码以修改浏览器特征
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            delete navigator.__proto__.webdriver;  // 删除webdriver标记
            window.chrome = { runtime: {} };  // 添加chrome对象
            navigator.plugins = [1,2,3];  // 设置插件
            """
        })

    def _close_new_ads(self):
        """
        关闭页面上的广告弹窗
        查找并点击所有带有close或mask类名的元素
        包含随机延迟以模拟人工操作
        """
        try:
            self.driver.execute_script("""
                document.querySelectorAll('[class*="close"], [class*="mask"]').forEach(btn => {
                    if(btn.offsetParent !== null) btn.click()
                });
            """)
            time.sleep(random.uniform(0.5,1.2))  # 添加随机延迟
        except Exception as e:
            pass

    def manual_login(self):
        """
        处理豆瓣登录流程
        等待用户手动完成登录操作，并验证登录状态
        返回：登录是否成功的布尔值
        """
        print("请手动完成以下操作：\n1. 访问豆瓣登录页\n2. 完成登录（含可能验证码）\n3. 确保最终进入个人主页")
        
        # 导航到个人主页
        self.driver.get("https://www.douban.com/mine/")
        self._close_new_ads()
        
        try:
            # 使用三重验证机制确认登录状态
            self.wait.until(lambda d: 
                "douban.com/people/" in d.current_url and  # 验证URL是否为个人主页
                d.find_elements(By.CSS_SELECTOR, ".user-info") and  # 验证个人信息区块是否存在
                d.find_elements(By.XPATH, "//a[contains(@href,'/mine?')]")  # 验证影音入口是否存在
            )
            # 从URL中提取用户ID
            current_url = self.driver.current_url
            if "douban.com/people/" in current_url:
                self.user_id = current_url.split("/people/")[1].split("/")[0]
                print(f"✅ 个人主页验证成功，用户ID：{self.user_id}")
            return True
        except Exception as e:
            # 登录失败时保存截图和页面源码以便调试
            self.driver.save_screenshot("login_fail.png")
            with open("login_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"❌ 登录失败，错误：{str(e)}")
            return False

    def get_watched_list(self):
        """
        获取用户的观影记录
        遍历所有页面，提取电影标题
        返回：包含所有电影标题的列表
        """
        print("正在获取观影记录...")
        base_url = f"https://movie.douban.com/people/{self.user_id}/collect"
        movie_list = []
        
        # 遍历所有页面（每页30条记录）
        for page in range(17):
            start = page * 30
            url = f"{base_url}?start={start}&sort=time&rating=all&mode=list&type=all&filter=all"
            print(f"解析第 {page + 1} 页...")
            
            self.driver.get(url)
            self._close_new_ads()
            
            # 等待页面加载完成
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".list-view .item")
            ))
            
            # 使用BeautifulSoup解析页面，提取电影标题
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            items = soup.select(".list-view .item")
            
            for item in items:
                title = item.select_one(".title a").get_text(strip=True)
                movie_list.append(title)
                print(f"获取：{title[:10]}...")
            
            # 添加随机延迟避免请求过快
            time.sleep(random.uniform(1, 3))
        
        return movie_list

    def _handle_pagination(self):
        """
        处理分页逻辑
        模拟人工点击下一页按钮
        返回：是否成功跳转到下一页的布尔值
        """
        try:
            next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.next:not(.disabled)")
            # 平滑滚动到下一页按钮位置
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", next_btn)
            time.sleep(random.uniform(0.8,1.5))  # 随机延迟
            next_btn.click()
            return True
        except:
            return False

    def save_to_csv(self, data):
        """
        将电影数据保存到CSV文件
        参数：
            data: 包含电影标题的列表
        """
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "电影名称", "采集时间"])  # 写入表头
            writer.writerows([[i+1, item, time.strftime("%Y-%m-%d %H:%M")] 
                            for i, item in enumerate(data)])  # 写入数据行
        print(f"数据已保存至 {OUTPUT_FILE}，共 {len(data)} 条记录")

    def run(self):
        """
        爬虫主运行方法
        处理整个流程：登录、获取数据、保存数据
        包含异常处理和资源清理
        """
        try:
            if self.manual_login():  # 如果登录成功
                movies = self.get_watched_list()  # 获取观影记录
                self.save_to_csv(movies)  # 保存数据
        except Exception as e:
            print(f"❗ 运行异常：{str(e)}")
        finally:
            input("按任意键关闭浏览器...")  # 等待用户确认
            self.driver.quit()  # 关闭浏览器释放资源

if __name__ == "__main__":
    spider = DoubanWatchedSpider()  # 创建爬虫实例
    spider.run()  # 运行爬虫