(function() {
    function getMoonPhaseEmoji() {
      // 基准新月日期（UTC时间）
      const baseDate = new Date('2023-01-21T00:00:00Z');
      const currentDate = new Date();
      
      // 计算天数差
      const timeDiff = currentDate - baseDate;
      const dayDiff = timeDiff / (1000 * 3600 * 24);
      
      // 计算月相阶段（0-8）
      const phase = (dayDiff % 29.53) / 29.53 * 8;
      
      // 月相emoji映射
      const phases = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘', '🌑'];
      const index = Math.floor(phase);
      
      return phases[index];
    }
  
    // 替换标题中的​ ZERO WIDTH SPACE
    const placeholder = '​';
    const emoji = getMoonPhaseEmoji();
    document.title = document.title.replace(placeholder, emoji+" ");
  })();