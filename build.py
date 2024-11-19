# build.py
import os
import shutil
import PyInstaller.__main__
import json


def create_config_template():
    """创建配置文件模板"""
    config = {
        "database": {
            "host": "YOUR_SERVER_IP",  # 将被替换为实际的服务器IP
            "port": 3306,
            "database": "dental_equipment_db",
            "user": "dental_user",
            "password": "your_password",
            "charset": "utf8mb4",
            "pool_size": 5,
            "pool_timeout": 30
        },
        "ui": {
            "window_title": "牙科设备展会管理系统",
            "window_size": [1280, 800],
            "theme": "light",
            "font_family": "Microsoft YaHei",
            "font_size": 10,
            "table_row_height": 30,
            "date_format": "YYYY-MM-DD",
            "language": "zh_CN"
        },
        "export": {
            "excel_template_path": "resources/templates/excel",
            "pdf_template_path": "resources/templates/pdf",
            "csv_encoding": "utf-8-sig",
            "excel_default_sheet": "Sheet1",
            "pdf_page_size": "A4",
            "export_path": "exports"
        }
    }

    with open('dist/config/settings_template.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def copy_resources():
    """复制必要的资源文件"""
    resource_dirs = ['resources', 'exports', 'logs']
    for dir_name in resource_dirs:
        target_dir = os.path.join('dist', dir_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    # 复制资源文件
    if os.path.exists('resources'):
        shutil.copytree('resources', 'dist/resources', dirs_exist_ok=True)


def build_application():
    """打包应用程序"""
    PyInstaller.__main__.run([
        'main.py',
        '--name=DentalEquipmentSystem',
        '--windowed',
        '--icon=resources/images/icon.ico',
        '--add-data=resources;resources',
        '--hidden-import=mysql.connector',
        '--hidden-import=PyQt5',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=matplotlib',
        '--clean',
        '--noconfirm'
    ])


def create_setup_script():
    """创建安装脚本"""
    setup_script = '''@echo off
echo 正在安装牙科设备展会管理系统...

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "exports" mkdir exports
if not exist "config" mkdir config

REM 复制配置文件模板
copy /y "config\\settings_template.json" "config\\settings.json"

echo 请修改 config\\settings.json 中的数据库连接信息
echo 安装完成！
pause
'''

    with open('dist/setup.bat', 'w', encoding='utf-8') as f:
        f.write(setup_script)


def create_readme():
    """创建说明文档"""
    readme_content = '''# 牙科设备展会管理系统安装说明

## 安装步骤

1. 运行 setup.bat 进行初始安装
2. 修改 config/settings.json 中的数据库连接信息：
   - host: 数据库服务器IP地址
   - user: 数据库用户名
   - password: 数据库密码
   - database: 数据库名称

3. 运行 DentalEquipmentSystem.exe 启动系统

## 注意事项

- 确保MySQL服务器已开启远程访问
- 确保防火墙已允许MySQL端口(3306)的访问
- 首次运行可能需要以管理员身份运行
'''

    with open('dist/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)


def main():
    """主函数"""
    print("开始打包应用...")

    # 1. 打包应用
    build_application()

    # 2. 创建配置目录和模板
    os.makedirs('dist/config', exist_ok=True)
    create_config_template()

    # 3. 复制资源文件
    copy_resources()

    # 4. 创建安装脚本和说明文档
    create_setup_script()
    create_readme()

    print("打包完成！")


if __name__ == '__main__':
    main()