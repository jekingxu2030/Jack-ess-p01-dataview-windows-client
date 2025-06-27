import re
import requests
import json
from PyQt5.QtCore import QObject, pyqtSignal

class AuthManager(QObject):
    login_success = pyqtSignal(str)
    login_failed = pyqtSignal(str)
    token_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = requests.Session()
        self.base_url = "http://ems.hy-power.net:8114"
        self.token = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def login(self, username, password):
        print("开始登录流程")
        try:
            # class="ant-form ant-form-horizontal css-17yhhjv login-form"            # 获取登录页面，可能需要CSRF令牌
            print("正在请求登录页面...")
            login_page = self.session.get(f"{self.base_url}/ems/login", headers=self.headers, timeout=10)
            print(f"登录页面请求成功，状态码: {login_page.status_code}")
            login_page.raise_for_status()

            # 已禁用CSRF令牌提取（用户要求）
            csrf_token = None
            print("已关闭CSRF令牌提取功能")

            print("开始使用模拟登录窗口获取验证码...")
            # 使用Selenium获取动态渲染的验证码
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            import time

            verification_code = None
            try:
                # 配置无头浏览器
                chrome_options = Options()
                # 启用可视化浏览器窗口（用户要求）
                # chrome_options.add_argument("--headless=new")
                # chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=800,600")
                chrome_options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(f"{self.base_url}/ems/login")

                # 等待canvas元素加载完成
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
                time.sleep(1)  # 额外等待确保元素渲染完成
                print("请在打开的浏览器窗口中完成登录操作...")
                # 等待用户手动完成登录
                input("登录成功后请按Enter键继续...")

                # 将Selenium浏览器中的cookies添加到requests会话
                print("正在同步浏览器登录状态...")
                for cookie in driver.get_cookies():
                    self.session.cookies.set(cookie['name'], cookie['value'])
                print("浏览器登录状态已同步到请求会话")

                # 获取canvas元素的verificationcode属性
                # 手动登录模式下不需要自动提取验证码
                verification_code = None
                print("已切换至手动登录模式，无需自动提取验证码")
            except Exception as e:
                print(f"Selenium获取验证码失败: {str(e)}")
            finally:
                if 'driver' in locals():
                    driver.quit()

            if not verification_code:
                print("未找到canvas验证码元素")
                self.login_failed.emit("登录失败：无法获取验证码")
                return False

            # 手动登录后跳过自动登录请求
                print("已完成手动登录，跳过自动登录请求")

            print("登录请求发送完成，正在检查登录结果...")
            # 检查登录是否成功（根据实际情况调整判断条件）
            print(f"登录响应URL: {response.url}")
            print(f"登录响应内容: {response.text[:200]}...")  # 打印前200个字符
            
                # 提取satoken
                self.token = self.session.cookies.get('satoken')
                if not self.token:
                    print("登录成功但未找到satoken cookie")
                    self.login_failed.emit("未获取到认证令牌")
                    return False
                print(f"成功提取satoken: {self.token[:10]}...")
                self.login_success.emit(self.token)
                return True
        except Exception as e:
            print(f"登录过程发生异常: {str(e)}")
            self.login_failed.emit(f"登录异常：{str(e)}")
            return False

    def _extract_csrf_token(self, html_content):
        # 增加调试日志查看HTML内容片段
        print("登录页面HTML前500字符: ", html_content[:500])
        
        # 优化CSRF令牌提取正则表达式，支持不同格式
        patterns = [
            r'name="csrf_token" value="([^"]+)"',  # 标准表单字段
            r'name="csrfmiddlewaretoken" value="([^"]+)"',  # Django常见格式
            r'csrfToken\s*=\s*"([^"]+)"',  # JavaScript变量格式
            r'<meta name="csrf-token" content="([^"]+)"'  # Meta标签格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                print(f"使用模式'{pattern}'提取到CSRF令牌")
                return match.group(1)
        
        print("所有CSRF提取模式均匹配失败")
        return None


    def get_ws_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get_ws_url(self):
        return "ws://ems.hy-power.net:8888/E6F7D5412A20" if self.token else None

    def logout(self):
        try:
            self.session.post(f"{self.base_url}/logout", headers=self.headers)
            self.token = None
            self.session.close()
        except Exception as e:
            print(f"登出异常：{str(e)}")