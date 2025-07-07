#!/usr/bin/env python3
"""
股票数据缓存管理器
支持本地缓存股票数据，减少API调用，提高响应速度
"""

import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Union
import hashlib


class StockDataCache:
    """股票数据缓存管理器 - 支持美股和A股数据缓存优化"""
    
    def __init__(self, cache_dir: str = None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径，默认为 tradingagents/dataflows/data_cache
        """
        if cache_dir is None:
            # 获取当前文件所在目录
            current_dir = Path(__file__).parent
            cache_dir = current_dir / "data_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        # self.stock_data_dir = self.cache_dir / "stock_data"
        # self.news_data_dir = self.cache_dir / "news_data"
        # self.fundamentals_dir = self.cache_dir / "fundamentals"
        # self.metadata_dir = self.cache_dir / "metadata"

        # 创建子目录 - 按市场分类
        self.us_stock_dir = self.cache_dir / "us_stocks"
        self.china_stock_dir = self.cache_dir / "china_stocks"
        self.us_news_dir = self.cache_dir / "us_news"
        self.china_news_dir = self.cache_dir / "china_news"
        self.us_fundamentals_dir = self.cache_dir / "us_fundamentals"
        self.china_fundamentals_dir = self.cache_dir / "china_fundamentals"
        self.metadata_dir = self.cache_dir / "metadata"

        
        # for dir_path in [self.stock_data_dir, self.news_data_dir, self.fundamentals_dir, self.metadata_dir]:
        #     dir_path.mkdir(exist_ok=True)

        for dir_path in [self.us_stock_dir, self.china_stock_dir, self.us_news_dir,
                        self.china_news_dir, self.us_fundamentals_dir,
                        self.china_fundamentals_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)

        # 缓存配置 - 针对不同市场设置不同的TTL
        self.cache_config = {
            'us_stock_data': {
                'ttl_hours': 2,  # 美股数据缓存2小时（考虑到API限制）
                'max_files': 1000,
                'description': '美股历史数据'
            },
            'china_stock_data': {
                'ttl_hours': 1,  # A股数据缓存1小时（实时性要求高）
                'max_files': 1000,
                'description': 'A股历史数据'
            },
            'us_news': {
                'ttl_hours': 6,  # 美股新闻缓存6小时
                'max_files': 500,
                'description': '美股新闻数据'
            },
            'china_news': {
                'ttl_hours': 4,  # A股新闻缓存4小时
                'max_files': 500,
                'description': 'A股新闻数据'
            },
            'us_fundamentals': {
                'ttl_hours': 24,  # 美股基本面数据缓存24小时
                'max_files': 200,
                'description': '美股基本面数据'
            },
            'china_fundamentals': {
                'ttl_hours': 12,  # A股基本面数据缓存12小时
                'max_files': 200,
                'description': 'A股基本面数据'
            }
        }

        
        print(f"📁 缓存管理器初始化完成，缓存目录: {self.cache_dir}")    
        print(f"🗄️ 数据库缓存管理器初始化完成")
        print(f"   美股数据: ✅ 已配置")
        print(f"   A股数据: ✅ 已配置")

    def _determine_market_type(self, symbol: str) -> str:
        """根据股票代码确定市场类型"""
        import re

        # 判断是否为中国A股（6位数字）
        if re.match(r'^\d{6}$', str(symbol)):
            return 'china'
        else:
            return 'us'


    def _generate_cache_key(self, data_type: str, symbol: str, **kwargs) -> str:
        """生成缓存键"""
        # 创建一个包含所有参数的字符串
        params_str = f"{data_type}_{symbol}"
        for key, value in sorted(kwargs.items()):
            params_str += f"_{key}_{value}"
        
        # 使用MD5生成短的唯一标识
        cache_key = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"{symbol}_{data_type}_{cache_key}"
    
    # def _get_cache_path(self, data_type: str, cache_key: str, file_format: str = "json") -> Path:
    #     """获取缓存文件路径"""
    #     if data_type == "stock_data":
    #         base_dir = self.stock_data_dir
    #     elif data_type == "news":
    #         base_dir = self.news_data_dir
    #     elif data_type == "fundamentals":
    #         base_dir = self.fundamentals_dir
    #     else:
    #         base_dir = self.cache_dir
        
    #     return base_dir / f"{cache_key}.{file_format}"

    def _get_cache_path(self, data_type: str, cache_key: str, file_format: str = "json", symbol: str = None) -> Path:
        """获取缓存文件路径 - 支持市场分类"""
        if symbol:
            market_type = self._determine_market_type(symbol)
        else:
            # 从缓存键中尝试提取市场类型
            market_type = 'us' if not cache_key.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')) else 'china'

        # 根据数据类型和市场类型选择目录
        if data_type == "stock_data":
            base_dir = self.china_stock_dir if market_type == 'china' else self.us_stock_dir
        elif data_type == "news":
            base_dir = self.china_news_dir if market_type == 'china' else self.us_news_dir
        elif data_type == "fundamentals":
            base_dir = self.china_fundamentals_dir if market_type == 'china' else self.us_fundamentals_dir
        else:
            base_dir = self.cache_dir

        return base_dir / f"{cache_key}.{file_format}"

    
    def _get_metadata_path(self, cache_key: str) -> Path:
        """获取元数据文件路径"""
        return self.metadata_dir / f"{cache_key}_meta.json"
    
    def _save_metadata(self, cache_key: str, metadata: Dict[str, Any]):
        """保存元数据"""
        metadata_path = self._get_metadata_path(cache_key)
        metadata['cached_at'] = datetime.now().isoformat()
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """加载元数据"""
        metadata_path = self._get_metadata_path(cache_key)
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载元数据失败: {e}")
            return None
    
    # def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
    #     """检查缓存是否有效"""
    #     metadata = self._load_metadata(cache_key)
    #     if not metadata:
    #         return False
        
    #     cached_at = datetime.fromisoformat(metadata['cached_at'])
    #     age = datetime.now() - cached_at
        
    #     return age.total_seconds() < max_age_hours * 3600

    def is_cache_valid(self, cache_key: str, max_age_hours: int = None, symbol: str = None, data_type: str = None) -> bool:
        """检查缓存是否有效 - 支持智能TTL配置"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return False

        # 如果没有指定TTL，根据数据类型和市场自动确定
        if max_age_hours is None:
            if symbol and data_type:
                market_type = self._determine_market_type(symbol)
                cache_type = f"{market_type}_{data_type}"
                max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)
            else:
                # 从元数据中获取信息
                symbol = metadata.get('symbol', '')
                data_type = metadata.get('data_type', 'stock_data')
                market_type = self._determine_market_type(symbol)
                cache_type = f"{market_type}_{data_type}"
                max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        cached_at = datetime.fromisoformat(metadata['cached_at'])
        age = datetime.now() - cached_at

        is_valid = age.total_seconds() < max_age_hours * 3600

        if is_valid:
            market_type = self._determine_market_type(metadata.get('symbol', ''))
            cache_type = f"{market_type}_{metadata.get('data_type', 'stock_data')}"
            desc = self.cache_config.get(cache_type, {}).get('description', '数据')
            print(f"✅ 缓存有效: {desc} - {metadata.get('symbol')} (剩余 {max_age_hours - age.total_seconds()/3600:.1f}h)")

        return is_valid
    
    # def save_stock_data(self, symbol: str, data: Union[pd.DataFrame, str], 
    #                    start_date: str = None, end_date: str = None, 
    #                    data_source: str = "unknown") -> str:
    #     """
    #     保存股票数据到缓存
        
    #     Args:
    #         symbol: 股票代码
    #         data: 股票数据（DataFrame或字符串）
    #         start_date: 开始日期
    #         end_date: 结束日期
    #         data_source: 数据源（如 "tdx", "yfinance", "finnhub"）
        
    #     Returns:
    #         cache_key: 缓存键
    #     """
    #     cache_key = self._generate_cache_key("stock_data", symbol, 
    #                                        start_date=start_date, 
    #                                        end_date=end_date,
    #                                        source=data_source)
        
    #     # 保存数据
    #     if isinstance(data, pd.DataFrame):
    #         cache_path = self._get_cache_path("stock_data", cache_key, "csv")
    #         data.to_csv(cache_path, index=True)
    #     else:
    #         cache_path = self._get_cache_path("stock_data", cache_key, "txt")
    #         with open(cache_path, 'w', encoding='utf-8') as f:
    #             f.write(str(data))
        
    #     # 保存元数据
    #     metadata = {
    #         'symbol': symbol,
    #         'data_type': 'stock_data',
    #         'start_date': start_date,
    #         'end_date': end_date,
    #         'data_source': data_source,
    #         'file_path': str(cache_path),
    #         'file_format': 'csv' if isinstance(data, pd.DataFrame) else 'txt'
    #     }
    #     self._save_metadata(cache_key, metadata)
        
    #     print(f"💾 股票数据已缓存: {symbol} ({data_source}) -> {cache_key}")
    #     return cache_key

    def save_stock_data(self, symbol: str, data: Union[pd.DataFrame, str],
                       start_date: str = None, end_date: str = None,
                       data_source: str = "unknown") -> str:
        """
        保存股票数据到缓存 - 支持美股和A股分类存储

        Args:
            symbol: 股票代码
            data: 股票数据（DataFrame或字符串）
            start_date: 开始日期
            end_date: 结束日期
            data_source: 数据源（如 "tdx", "yfinance", "finnhub"）

        Returns:
            cache_key: 缓存键
        """
        market_type = self._determine_market_type(symbol)
        cache_key = self._generate_cache_key("stock_data", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source,
                                           market=market_type)

        # 保存数据
        if isinstance(data, pd.DataFrame):
            cache_path = self._get_cache_path("stock_data", cache_key, "csv", symbol)
            data.to_csv(cache_path, index=True)
        else:
            cache_path = self._get_cache_path("stock_data", cache_key, "txt", symbol)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(str(data))

        # 保存元数据
        metadata = {
            'symbol': symbol,
            'data_type': 'stock_data',
            'market_type': market_type,
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'file_path': str(cache_path),
            'file_format': 'csv' if isinstance(data, pd.DataFrame) else 'txt'
        }
        self._save_metadata(cache_key, metadata)

        # 获取描述信息
        cache_type = f"{market_type}_stock_data"
        desc = self.cache_config.get(cache_type, {}).get('description', '股票数据')
        print(f"💾 {desc}已缓存: {symbol} ({data_source}) -> {cache_key}")
        return cache_key

    
    def load_stock_data(self, cache_key: str) -> Optional[Union[pd.DataFrame, str]]:
        """从缓存加载股票数据"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return None
        
        cache_path = Path(metadata['file_path'])
        if not cache_path.exists():
            return None
        
        try:
            if metadata['file_format'] == 'csv':
                return pd.read_csv(cache_path, index_col=0)
            else:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"⚠️ 加载缓存数据失败: {e}")
            return None
    
    # def find_cached_stock_data(self, symbol: str, start_date: str = None, 
    #                           end_date: str = None, data_source: str = None,
    #                           max_age_hours: int = 24) -> Optional[str]:
    #     """
    #     查找匹配的缓存数据
        
    #     Args:
    #         symbol: 股票代码
    #         start_date: 开始日期
    #         end_date: 结束日期
    #         data_source: 数据源
    #         max_age_hours: 最大缓存时间（小时）
        
    #     Returns:
    #         cache_key: 如果找到有效缓存则返回缓存键，否则返回None
    #     """
    #     # 生成查找键
    #     search_key = self._generate_cache_key("stock_data", symbol,
    #                                         start_date=start_date,
    #                                         end_date=end_date,
    #                                         source=data_source)
        
    #     # 检查精确匹配
    #     if self.is_cache_valid(search_key, max_age_hours):
    #         print(f"🎯 找到精确匹配的缓存: {symbol} -> {search_key}")
    #         return search_key
        
    #     # 如果没有精确匹配，查找部分匹配（相同股票代码的其他缓存）
    #     for metadata_file in self.metadata_dir.glob(f"*_meta.json"):
    #         try:
    #             with open(metadata_file, 'r', encoding='utf-8') as f:
    #                 metadata = json.load(f)
                
    #             if (metadata.get('symbol') == symbol and 
    #                 metadata.get('data_type') == 'stock_data' and
    #                 (data_source is None or metadata.get('data_source') == data_source)):
                    
    #                 cache_key = metadata_file.stem.replace('_meta', '')
    #                 if self.is_cache_valid(cache_key, max_age_hours):
    #                     print(f"📋 找到部分匹配的缓存: {symbol} -> {cache_key}")
    #                     return cache_key
    #         except Exception:
    #             continue
        
    #     print(f"❌ 未找到有效缓存: {symbol}")
    #     return None

    def find_cached_stock_data(self, symbol: str, start_date: str = None,
                              end_date: str = None, data_source: str = None,
                              max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的缓存数据 - 支持智能市场分类查找

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            data_source: 数据源
            max_age_hours: 最大缓存时间（小时），None时使用智能配置

        Returns:
            cache_key: 如果找到有效缓存则返回缓存键，否则返回None
        """
        market_type = self._determine_market_type(symbol)

        # 如果没有指定TTL，使用智能配置
        if max_age_hours is None:
            cache_type = f"{market_type}_stock_data"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        # 生成查找键
        search_key = self._generate_cache_key("stock_data", symbol,
                                            start_date=start_date,
                                            end_date=end_date,
                                            source=data_source,
                                            market=market_type)

        # 检查精确匹配
        if self.is_cache_valid(search_key, max_age_hours, symbol, 'stock_data'):
            desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '数据')
            print(f"🎯 找到精确匹配的{desc}: {symbol} -> {search_key}")
            return search_key

        # 如果没有精确匹配，查找部分匹配（相同股票代码的其他缓存）
        for metadata_file in self.metadata_dir.glob(f"*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                if (metadata.get('symbol') == symbol and
                    metadata.get('data_type') == 'stock_data' and
                    metadata.get('market_type') == market_type and
                    (data_source is None or metadata.get('data_source') == data_source)):

                    cache_key = metadata_file.stem.replace('_meta', '')
                    if self.is_cache_valid(cache_key, max_age_hours, symbol, 'stock_data'):
                        desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '数据')
                        print(f"📋 找到部分匹配的{desc}: {symbol} -> {cache_key}")
                        return cache_key
            except Exception:
                continue

        desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '数据')
        print(f"❌ 未找到有效的{desc}缓存: {symbol}")
        return None

    
    def save_news_data(self, symbol: str, news_data: str, 
                      start_date: str = None, end_date: str = None,
                      data_source: str = "unknown") -> str:
        """保存新闻数据到缓存"""
        cache_key = self._generate_cache_key("news", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source)
        
        cache_path = self._get_cache_path("news", cache_key, "txt")
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(news_data)
        
        metadata = {
            'symbol': symbol,
            'data_type': 'news',
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'file_path': str(cache_path),
            'file_format': 'txt'
        }
        self._save_metadata(cache_key, metadata)
        
        print(f"📰 新闻数据已缓存: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def save_fundamentals_data(self, symbol: str, fundamentals_data: str,
                              data_source: str = "unknown") -> str:
        """保存基本面数据到缓存"""
        market_type = self._determine_market_type(symbol)
        cache_key = self._generate_cache_key("fundamentals", symbol,
                                           source=data_source,
                                           market=market_type,
                                           date=datetime.now().strftime("%Y-%m-%d"))
        
        # cache_path = self._get_cache_path("fundamentals", cache_key, "txt")
        cache_path = self._get_cache_path("fundamentals", cache_key, "txt", symbol)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(fundamentals_data)
        
        metadata = {
            'symbol': symbol,
            'data_type': 'fundamentals',
            'data_source': data_source,
            'market_type': market_type,            
            'file_path': str(cache_path),
            'file_format': 'txt'
        }
        self._save_metadata(cache_key, metadata)
        
        # print(f"💼 基本面数据已缓存: {symbol} ({data_source}) -> {cache_key}")
        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面数据')
        print(f"💼 {desc}已缓存: {symbol} ({data_source}) -> {cache_key}")        
        return cache_key

    def load_fundamentals_data(self, cache_key: str) -> Optional[str]:
        """从缓存加载基本面数据"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return None
        
        cache_path = Path(metadata['file_path'])
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ 加载基本面缓存数据失败: {e}")
            return None
    
    def find_cached_fundamentals_data(self, symbol: str, data_source: str = None,
                                    max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的基本面缓存数据
        
        Args:
            symbol: 股票代码
            data_source: 数据源（如 "openai", "finnhub"）
            max_age_hours: 最大缓存时间（小时），None时使用智能配置
        
        Returns:
            cache_key: 如果找到有效缓存则返回缓存键，否则返回None
        """
        market_type = self._determine_market_type(symbol)
        
        # 如果没有指定TTL，使用智能配置
        if max_age_hours is None:
            cache_type = f"{market_type}_fundamentals"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)
        
        # 查找匹配的缓存
        for metadata_file in self.metadata_dir.glob(f"*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                if (metadata.get('symbol') == symbol and
                    metadata.get('data_type') == 'fundamentals' and
                    metadata.get('market_type') == market_type and
                    (data_source is None or metadata.get('data_source') == data_source)):
                    
                    cache_key = metadata_file.stem.replace('_meta', '')
                    if self.is_cache_valid(cache_key, max_age_hours, symbol, 'fundamentals'):
                        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面数据')
                        print(f"🎯 找到匹配的{desc}缓存: {symbol} ({data_source}) -> {cache_key}")
                        return cache_key
            except Exception:
                continue
        
        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面数据')
        print(f"❌ 未找到有效的{desc}缓存: {symbol} ({data_source})")
        return None    

    def clear_old_cache(self, max_age_days: int = 7):
        """清理过期缓存"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cleared_count = 0
        
        for metadata_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                cached_at = datetime.fromisoformat(metadata['cached_at'])
                if cached_at < cutoff_time:
                    # 删除数据文件
                    data_file = Path(metadata['file_path'])
                    if data_file.exists():
                        data_file.unlink()
                    
                    # 删除元数据文件
                    metadata_file.unlink()
                    cleared_count += 1
                    
            except Exception as e:
                print(f"⚠️ 清理缓存时出错: {e}")
        
        print(f"🧹 已清理 {cleared_count} 个过期缓存文件")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            'total_files': 0,
            'stock_data_count': 0,
            'news_count': 0,
            'fundamentals_count': 0,
            'total_size_mb': 0
        }
        
        for metadata_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                data_type = metadata.get('data_type', 'unknown')
                if data_type == 'stock_data':
                    stats['stock_data_count'] += 1
                elif data_type == 'news':
                    stats['news_count'] += 1
                elif data_type == 'fundamentals':
                    stats['fundamentals_count'] += 1
                
                # 计算文件大小
                data_file = Path(metadata['file_path'])
                if data_file.exists():
                    stats['total_size_mb'] += data_file.stat().st_size / (1024 * 1024)
                
                stats['total_files'] += 1
                
            except Exception:
                continue
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats


# 全局缓存实例
_cache_instance = None

def get_cache() -> StockDataCache:
    """获取全局缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = StockDataCache()
    return _cache_instance
