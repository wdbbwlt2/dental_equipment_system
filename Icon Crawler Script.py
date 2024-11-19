import os
import requests
from bs4 import BeautifulSoup
import time


class IconCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.icons_dir = os.path.join('resources', 'images')
        self.create_directory()

    def create_directory(self):
        """创建图标存储目录"""
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)

    def download_icon(self, keyword, filename):
        """从Flaticon下载图标"""
        # 搜索URL
        search_url = f'https://www.flaticon.com/search?word={keyword}'

        try:
            # 获取搜索页面
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到第一个图标的下载链接
            icon_link = soup.find('img', {'class': 'lzy'})
            if icon_link and 'data-src' in icon_link.attrs:
                icon_url = icon_link['data-src']

                # 下载图标
                icon_response = requests.get(icon_url, headers=self.headers, timeout=10)
                icon_response.raise_for_status()

                # 保存图标
                icon_path = os.path.join(self.icons_dir, filename)
                with open(icon_path, 'wb') as f:
                    f.write(icon_response.content)

                print(f"Successfully downloaded {filename}")
                return True

            else:
                print(f"No icon found for keyword: {keyword}")
                return False

        except Exception as e:
            print(f"Error downloading {filename}: {str(e)}")
            return False

    def download_all_icons(self):
        """下载所有需要的图标"""
        icons = {
            'product': 'product management',
            'exhibition': 'exhibition',
            'record': 'record management',
            'visualization': 'data visualization',
            'search': 'search',
            'reset': 'reset'
        }

        for filename, keyword in icons.items():
            print(f"\nDownloading {filename}.png...")
            success = self.download_icon(keyword, f"{filename}.png")
            if success:
                time.sleep(2)  # 避免请求过快
            else:
                print(f"Failed to download {filename}.png")


if __name__ == '__main__':
    crawler = IconCrawler()
    crawler.download_all_icons()