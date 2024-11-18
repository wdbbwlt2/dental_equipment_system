import os
import requests
import logging
from pathlib import Path


def setup_logger():
    """设置日志记录器"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def download_simhei_font():
    """
    下载并保存SimHei字体文件
    """
    logger = setup_logger()

    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 创建字体目录
        font_dir = os.path.join(project_root, 'resources', 'fonts')
        os.makedirs(font_dir, exist_ok=True)

        font_path = os.path.join(font_dir, 'simhei.ttf')

        # 检查文件是否已存在
        if os.path.exists(font_path):
            logger.info("SimHei字体文件已存在")
            return

        # SimHei字体下载URL
        url = "http://font.py4js.com/fonts/SimHei.ttf"

        logger.info("开始下载SimHei字体...")

        # 发送请求并下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查是否下载成功

        # 保存文件
        with open(font_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"SimHei字体已成功下载到: {font_path}")

    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败: {str(e)}")
        # 尝试备用链接
        backup_urls = [
            "https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf",
            "https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-Regular.otf"
        ]

        for backup_url in backup_urls:
            try:
                logger.info(f"尝试使用备用链接: {backup_url}")
                response = requests.get(backup_url, stream=True)
                response.raise_for_status()

                with open(font_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                logger.info(f"使用备用链接成功下载字体到: {font_path}")
                return
            except requests.exceptions.RequestException as e:
                logger.error(f"备用链接下载失败: {str(e)}")
                continue

        raise Exception("所有下载尝试均失败")

    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        download_simhei_font()
    except Exception as e:
        print(f"程序执行失败: {str(e)}")