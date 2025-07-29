#!/usr/bin/env python3
"""
創建符合市場配置的測試信號
用於驗證短線策略的智能判斷邏輯
"""

import sqlite3
import json
from datetime import datetime, timedelta
import pytz
import random

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ).replace(tzinfo=None)

def create_intelligent_test_signals():
    """創建智能化的測試信號，基於市場配置策略"""
    
    # 讀取市場配置
    with open('app/config/market_conditions_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 獲取牛市短線策略配置
    bull_strategies = config['market_conditions']['bull']['strategies']
    
    test_signals = []
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    now = get_taiwan_now()
    
    for i, symbol in enumerate(symbols):
        # 根據不同策略創建信號
        if i == 0:  # BTCUSDT - 極短線剝頭皮策略
            strategy = bull_strategies['ultra_short_scalping']
            timeframe = '5m'
            
            # 基於配置計算有效期（30分鐘內強制平倉）
            expires_at = now + timedelta(minutes=25)  # 略少於30分鐘
            
            # 智能信心度計算（基於配置的風險回報比）
            confidence = random.uniform(0.88, 0.96)  # 高信心度範圍
            
            # 基於策略的精準度評分
            precision_score = random.uniform(0.92, 0.98)
            
            # 策略特定的進場價格計算
            entry_price = 43250.50 + random.uniform(-100, 100)
            
            signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': 'BUY',
                'signal_strength': confidence * 100,
                'confidence': confidence,
                'precision_score': precision_score,
                'entry_price': entry_price,
                'stop_loss': entry_price * (1 - 0.01),  # 1% 止損（配置建議）
                'take_profit': entry_price * (1 + 0.015), # 1.5% 止盈
                'primary_timeframe': timeframe,
                'strategy_name': f"牛市極短線剝頭皮_{timeframe}",
                'status': 'active',
                'is_scalping': 1,
                'is_precision_selected': 1,
                'market_condition_score': random.uniform(0.90, 0.98),
                'indicator_consistency': random.uniform(0.85, 0.95),
                'timing_score': random.uniform(0.88, 0.96),
                'risk_adjustment': random.uniform(0.90, 0.98),
                'created_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'reasoning': f'牛市極短線剝頭皮策略 - RSI突破+MACD金叉+成交量放大 (評分: {precision_score:.3f})',
                'urgency_level': 'high',
                'risk_reward_ratio': 1.5  # 配置建議的風險回報比
            }
            
        elif i == 1:  # ETHUSDT - 短線動能追蹤策略
            strategy = bull_strategies['short_term_momentum']
            timeframe = '1h'
            
            # 基於配置計算有效期（48小時內）
            expires_at = now + timedelta(hours=36)  # 36小時
            
            confidence = random.uniform(0.78, 0.88)  # 中高信心度
            precision_score = random.uniform(0.85, 0.93)
            entry_price = 2380.75 + random.uniform(-50, 50)
            
            signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': 'BUY',
                'signal_strength': confidence * 100,
                'confidence': confidence,
                'precision_score': precision_score,
                'entry_price': entry_price,
                'stop_loss': entry_price * (1 - 0.03),  # 3% 止損
                'take_profit': entry_price * (1 + 0.075), # 7.5% 止盈（2.5倍風險回報）
                'primary_timeframe': timeframe,
                'strategy_name': f"牛市短線動能追蹤_{timeframe}",
                'status': 'active',
                'is_scalping': 1,
                'is_precision_selected': 1,
                'market_condition_score': random.uniform(0.82, 0.92),
                'indicator_consistency': random.uniform(0.78, 0.88),
                'timing_score': random.uniform(0.80, 0.90),
                'risk_adjustment': random.uniform(0.85, 0.93),
                'created_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'reasoning': f'牛市短線動能追蹤策略 - RSI 50-70區間+MACD金叉+日內強勢 (評分: {precision_score:.3f})',
                'urgency_level': 'medium',
                'risk_reward_ratio': 2.5
            }
            
        else:  # BNBUSDT - 短線波段策略
            strategy = bull_strategies['short_term_swing']
            timeframe = '4h'
            
            # 基於配置計算有效期（3天內）
            expires_at = now + timedelta(days=2, hours=12)  # 2.5天
            
            confidence = random.uniform(0.72, 0.82)  # 中等信心度
            precision_score = random.uniform(0.80, 0.90)
            entry_price = 285.45 + random.uniform(-10, 10)
            
            signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': 'BUY',
                'signal_strength': confidence * 100,
                'confidence': confidence,
                'precision_score': precision_score,
                'entry_price': entry_price,
                'stop_loss': entry_price * (1 - 0.04),  # 4% 止損
                'take_profit': entry_price * (1 + 0.12), # 12% 止盈（3倍風險回報）
                'primary_timeframe': timeframe,
                'strategy_name': f"牛市短線波段_{timeframe}",
                'status': 'active',
                'is_scalping': 1,
                'is_precision_selected': 1,
                'market_condition_score': random.uniform(0.75, 0.85),
                'indicator_consistency': random.uniform(0.72, 0.82),
                'timing_score': random.uniform(0.74, 0.84),
                'risk_adjustment': random.uniform(0.78, 0.88),
                'created_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'reasoning': f'牛市短線波段策略 - 日線回調至支撐+RSI<45+背離修復 (評分: {precision_score:.3f})',
                'urgency_level': 'medium',
                'risk_reward_ratio': 3.0
            }
        
        test_signals.append(signal)
    
    # 插入到數據庫
    conn = sqlite3.connect('tradingx.db')
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO trading_signals (
            symbol, timeframe, signal_type, signal_strength, confidence, precision_score,
            entry_price, stop_loss, take_profit, primary_timeframe, strategy_name,
            status, is_scalping, is_precision_selected,
            market_condition_score, indicator_consistency, timing_score, risk_adjustment,
            created_at, expires_at, reasoning, urgency_level, risk_reward_ratio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    created_signals = []
    
    for signal in test_signals:
        cursor.execute(insert_query, (
            signal['symbol'], signal['timeframe'], signal['signal_type'],
            signal['signal_strength'], signal['confidence'], signal['precision_score'],
            signal['entry_price'], signal['stop_loss'], signal['take_profit'],
            signal['primary_timeframe'], signal['strategy_name'], signal['status'], 
            signal['is_scalping'], signal['is_precision_selected'], 
            signal['market_condition_score'], signal['indicator_consistency'], 
            signal['timing_score'], signal['risk_adjustment'], signal['created_at'], 
            signal['expires_at'], signal['reasoning'], signal['urgency_level'], 
            signal['risk_reward_ratio']
        ))
        
        signal_id = cursor.lastrowid
        signal['id'] = signal_id
        created_signals.append(signal)
        
        print(f"✅ 創建 {signal['symbol']} 智能信號 (ID: {signal_id})")
        print(f"   策略: {signal['strategy_name']}")
        print(f"   時間框架: {signal['timeframe']}")
        print(f"   信心度: {signal['confidence']:.3f}")
        print(f"   精準度: {signal['precision_score']:.3f}")
        print(f"   有效期: {signal['expires_at']}")
        print(f"   推理: {signal['reasoning']}")
        print()
    
    conn.commit()
    conn.close()
    
    print(f"🎯 成功創建 {len(created_signals)} 個基於市場配置的智能測試信號")
    return created_signals

if __name__ == "__main__":
    create_intelligent_test_signals()
