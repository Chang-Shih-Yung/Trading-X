// 測試前端顯示邏輯
console.log('🧪 測試前端顯示邏輯');

// 模擬信號數據
const testSignals = [
  { id: 1, symbol: 'BTCUSDT', profit_loss_pct: 2.5, trade_result: 'success' },
  { id: 2, symbol: 'ETHUSDT', profit_loss_pct: -1.2, trade_result: 'failure' },
  { id: 3, symbol: 'ADAUSDT', profit_loss_pct: null, trade_result: null },
  { id: 4, symbol: 'XRPUSDT', profit_loss_pct: 0.3, trade_result: 'breakeven' }
];

// 模擬 calculateProfitPercent 函數
const calculateProfitPercent = (signal) => {
  if (signal.profit_loss_pct !== undefined && signal.profit_loss_pct !== null) {
    console.log(`✅ 使用真實盈虧數據: ${signal.symbol} -> ${signal.profit_loss_pct.toFixed(2)}%`);
    return signal.profit_loss_pct;
  }
  console.log(`❌ ${signal.symbol} 缺少真實盈虧數據，返回 LOSE PRICE`);
  return "LOSE PRICE";
};

// 模擬 calculateTradeResult 函數
const calculateTradeResult = (signal) => {
  if (signal.trade_result && ['success', 'failure', 'breakeven'].includes(signal.trade_result)) {
    console.log(`✅ 使用真實交易結果: ${signal.symbol} -> ${signal.trade_result}`);
    return signal.trade_result;
  }
  console.log(`❌ ${signal.symbol} 缺少真實交易結果，返回 LOSE PRICE`);
  return "LOSE PRICE";
};

// 測試數據處理
console.log('\n📊 測試數據處理:');
testSignals.forEach(signal => {
  const profitPercent = calculateProfitPercent(signal);
  const tradeResult = calculateTradeResult(signal);
  
  console.log(`${signal.symbol}: profitPercent=${profitPercent}, tradeResult=${tradeResult}`);
  
  // 測試 toFixed 安全性
  if (typeof profitPercent === 'number') {
    console.log(`  ✅ 數字類型，可以使用 toFixed: ${profitPercent.toFixed(2)}%`);
  } else {
    console.log(`  ⚠️ 字符串類型，不能使用 toFixed: ${profitPercent}`);
  }
});

// 測試排序邏輯
console.log('\n🔍 測試排序邏輯:');
const processedSignals = testSignals.map(signal => ({
  ...signal,
  profitPercent: calculateProfitPercent(signal),
  tradeResult: calculateTradeResult(signal)
}));

// 分離有效信號和 LOSE PRICE 信號
const validSignals = processedSignals.filter(signal => 
  signal.profitPercent !== "LOSE PRICE" && typeof signal.profitPercent === 'number'
);

const losePriceSignals = processedSignals.filter(signal => 
  signal.profitPercent === "LOSE PRICE" || typeof signal.profitPercent !== 'number'
);

console.log(`有效信號: ${validSignals.length} 筆`);
console.log(`LOSE PRICE 信號: ${losePriceSignals.length} 筆`);

// 排序有效信號
validSignals.sort((a, b) => b.profitPercent - a.profitPercent);

console.log('\n📈 按盈利排序的有效信號:');
validSignals.forEach((signal, index) => {
  console.log(`${index + 1}. ${signal.symbol}: ${signal.profitPercent.toFixed(2)}%`);
});

console.log('\n📉 LOSE PRICE 信號:');
losePriceSignals.forEach((signal, index) => {
  console.log(`${validSignals.length + index + 1}. ${signal.symbol}: ${signal.profitPercent}`);
});

console.log('\n✅ 測試完成！');
