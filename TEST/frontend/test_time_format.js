// 測試時間格式化修復
const testTimeString = '2025-07-27T15:28:09.917693';

console.log('測試時間字串:', testTimeString);
console.log('');

// 原始的有問題的格式化
const formatDateTime1 = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

console.log('原始格式化結果（有問題）:', formatDateTime1(testTimeString));

// 修復後的格式化
const formatDateTime2 = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn(`無效的日期格式: ${dateString}`);
      return dateString;
    }
    
    const formatted = date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Taipei',
      hour12: false
    });
    
    return formatted;
  } catch (error) {
    console.error(`時間格式化錯誤: ${dateString}`, error);
    return dateString;
  }
};

console.log('修復後格式化結果:', formatDateTime2(testTimeString));
console.log('');

// 測試其他時間
const otherTimes = [
  '2025-07-27T14:28:32.695931', // ETHUSDT 信號
  '2025-07-27T02:02:58.995670', // 凌晨2點信號
];

console.log('其他時間測試:');
otherTimes.forEach(time => {
  console.log(`原始: ${time}`);
  console.log(`有問題: ${formatDateTime1(time)}`);
  console.log(`修復後: ${formatDateTime2(time)}`);
  console.log('---');
});
