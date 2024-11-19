# utils/statistics.py
"""
统计分析模块

提供数据统计和分析功能。
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import pandas as pd
from database.database import Database
from .logger import get_logger

# 1. 添加错误类型定义
class StatisticsError(Exception):
    """统计分析异常类"""
    pass


class Statistics:
    """统计分析类"""

    def __init__(self):
        try:
            self.db = Database()
        except Exception as e:
            raise StatisticsError(f"数据库初始化失败: {str(e)}")
        self.logger = get_logger(__name__)

    def get_product_statistics(self) -> Dict[str, Any]:
        """获取产品统计信息"""
        try:
            stats = {
                'total_products': 0,
                'model_distribution': {},
                'color_distribution': {},
                'most_popular_model': None,
                'most_used_color': None
            }

            # 查询总产品数
            query = "SELECT COUNT(*) as count FROM products"
            result = self.db.execute_query(query)
            stats['total_products'] = result[0]['count']

            # 型号分布
            query = """
                SELECT model, COUNT(*) as count 
                FROM products 
                GROUP BY model
            """
            results = self.db.execute_query(query)
            stats['model_distribution'] = {r['model']: r['count'] for r in results}
            if results:
                stats['most_popular_model'] = max(results, key=lambda x: x['count'])['model']

            # 颜色分布
            query = """
                SELECT color, COUNT(*) as count 
                FROM products 
                GROUP BY color
            """
            results = self.db.execute_query(query)
            stats['color_distribution'] = {r['color']: r['count'] for r in results}
            if results:
                stats['most_used_color'] = max(results, key=lambda x: x['count'])['color']

            return stats
        except Exception as e:
            self.logger.error(f"获取产品统计信息失败: {str(e)}")
            raise

    def get_exhibition_statistics(self) -> Dict[str, Any]:
        """获取展会统计信息"""
        try:
            stats = {
                'total_exhibitions': 0,
                'upcoming_exhibitions': 0,
                'ongoing_exhibitions': 0,
                'completed_exhibitions': 0,
                'monthly_distribution': {},
                'regional_distribution': {}
            }

            # 基本统计
            query = "SELECT COUNT(*) as count FROM exhibitions"
            result = self.db.execute_query(query)
            stats['total_exhibitions'] = result[0]['count']

            # 状态统计
            today = date.today()
            query = """
                SELECT 
                    COUNT(CASE WHEN start_date > %s THEN 1 END) as upcoming,
                    COUNT(CASE WHEN start_date <= %s AND end_date >= %s THEN 1 END) as ongoing,
                    COUNT(CASE WHEN end_date < %s THEN 1 END) as completed
                FROM exhibitions
            """
            result = self.db.execute_query(query, [today, today, today, today])
            stats.update({
                'upcoming_exhibitions': result[0]['upcoming'],
                'ongoing_exhibitions': result[0]['ongoing'],
                'completed_exhibitions': result[0]['completed']
            })

            # 月度分布
            query = """
                SELECT strftime('%Y-%m', start_date) as month, COUNT(*) as count
                FROM exhibitions
                GROUP BY month
                ORDER BY month
            """
            results = self.db.execute_query(query)
            stats['monthly_distribution'] = {r['month']: r['count'] for r in results}

            # 地区分布
            query = """
                SELECT 
                    SUBSTRING_INDEX(address, '省', 1) as region,
                    COUNT(*) as count
                FROM exhibitions
                GROUP BY region
            """
            results = self.db.execute_query(query)
            stats['regional_distribution'] = {r['region']: r['count'] for r in results}

            return stats
        except Exception as e:
            self.logger.error(f"获取展会统计信息失败: {str(e)}")
            raise

    def get_record_statistics(self) -> Dict[str, Any]:
        """获取参展记录统计信息"""
        try:
            stats = {
                'total_records': 0,
                'status_distribution': {},
                'product_participation': {},
                'exhibition_popularity': {},
                'monthly_trends': {}
            }

            # 总记录数
            query = "SELECT COUNT(*) as count FROM product_exhibition_records"
            result = self.db.execute_query(query)
            stats['total_records'] = result[0]['count']

            # 状态分布
            query = """
                SELECT status, COUNT(*) as count
                FROM product_exhibition_records
                GROUP BY status
            """
            results = self.db.execute_query(query)
            stats['status_distribution'] = {r['status']: r['count'] for r in results}

            # 产品参展次数
            query = """
                SELECT p.model, COUNT(*) as count
                FROM product_exhibition_records r
                JOIN products p ON r.product_id = p.product_id
                GROUP BY p.model
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            stats['product_participation'] = {r['model']: r['count'] for r in results}

            # 展会参展产品数量
            query = """
                SELECT e.name, COUNT(*) as count
                FROM product_exhibition_records r
                JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
                GROUP BY e.exhibition_id
                ORDER BY count DESC
            """
            results = self.db.execute_query(query)
            stats['exhibition_popularity'] = {r['name']: r['count'] for r in results}

            # 月度趋势
            query = """
                SELECT 
                    strftime('%Y-%m', e.start_date) as month,
                    COUNT(*) as count
                FROM product_exhibition_records r
                JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
                GROUP BY month
                ORDER BY month
            """
            results = self.db.execute_query(query)
            stats['monthly_trends'] = {r['month']: r['count'] for r in results}

            return stats
        except Exception as e:
            self.logger.error(f"获取参展记录统计信息失败: {str(e)}")
            raise

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合统计报告"""
        try:
            report = {
                'timestamp': datetime.now(),
                'product_stats': None,
                'exhibition_stats': None,
                'record_stats': None,
                'summary': {}
            }

            # 获取各项统计并验证数据
            try:
                report['product_stats'] = self.get_product_statistics()
            except Exception as e:
                self.logger.error(f"产品统计获取失败: {str(e)}")
                report['product_stats'] = {}

            try:
                report['exhibition_stats'] = self.get_exhibition_statistics()
            except Exception as e:
                self.logger.error(f"展会统计获取失败: {str(e)}")
                report['exhibition_stats'] = {}

            try:
                report['record_stats'] = self.get_record_statistics()
            except Exception as e:
                self.logger.error(f"记录统计获取失败: {str(e)}")
                report['record_stats'] = {}

            # 计算关键绩效指标
            report['summary'] = {
                'total_products': report['product_stats'].get('total_products', 0),
                'total_exhibitions': report['exhibition_stats'].get('total_exhibitions', 0),
                'total_records': report['record_stats'].get('total_records', 0),
                'avg_products_per_exhibition': (
                    report['record_stats'].get('total_records', 0) /
                    report['exhibition_stats'].get('total_exhibitions', 1)  # 避免除以0
                    if report['exhibition_stats'].get('total_exhibitions', 0) > 0 else 0
                ),
                'participation_rate': (
                    report['record_stats'].get('total_records', 0) /
                    (report['product_stats'].get('total_products', 1) *
                     report['exhibition_stats'].get('total_exhibitions', 1)) * 100
                    if (report['product_stats'].get('total_products', 0) *
                        report['exhibition_stats'].get('total_exhibitions', 0)) > 0 else 0
                )
            }

            return report

        except Exception as e:
            self.logger.error(f"生成综合统计报告失败: {str(e)}")
            raise