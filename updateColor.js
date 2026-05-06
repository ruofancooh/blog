(function () {
  function getDynamicColor() {
    const now = new Date();

    // ----- 1. 色相 H：周循环（周一 0 → 周日 360） -----
    const dayOfWeek = now.getDay(); // 0 周日, 1 周一 … 6 周六
    const diffToMonday = (dayOfWeek + 6) % 7; // 距离周一的天数（周一 0）
    const year = now.getFullYear();
    const month = now.getMonth();
    const date = now.getDate();
    const todayStart = new Date(year, month, date).getTime();
    const mondayStart = todayStart - diffToMonday * 86400000; // 本周一 00:00:00 毫秒值
    const elapsed = now.getTime() - mondayStart;
    const hue = (elapsed / (7 * 86400000)) * 360; // 0 ~ 360

    // ----- 2. 饱和度 S：距离 7 月 22 日越远越低 -----
    const target = new Date(year, 6, 22).getTime(); // 7 月 22 日 00:00:00
    const diffDays = Math.abs(todayStart - target) / 86400000;
    let saturation = 1 - diffDays / 182; // x 为相差天数
    if (saturation < 0) saturation = 0; // 最小为 0

    // ----- 3. 明度 V：中午 12 点最高，凌晨 0 点最低 -----
    const minutes = now.getHours() * 60 + now.getMinutes();
    const value = 1 - Math.abs(minutes - 720) / 720; // 720 = 12*60，三角波

    // ----- 4. HSV → HSL 转换（使颜色可用于 CSS） -----
    const h = hue % 360;
    const s = saturation;
    const v = value;

    // 计算 HSL 的 L 和 S
    const l = v * (1 - s / 2);
    let s_l = 0;
    if (l !== 0 && l !== 1) {
      s_l = (v - l) / Math.min(l, 1 - l);
    }

    // 钳位并取整
    const finalL = Math.round(Math.max(0, Math.min(1, l)) * 100);
    const finalS = Math.round(Math.max(0, Math.min(1, s_l)) * 100);
    const finalH = Math.round(h);

    return `hsl(${finalH}, ${finalS}%, ${finalL}%)`;
  }

  // 将函数计算出的颜色赋给根元素的 CSS 变量
  document.documentElement.style.setProperty(
    "--body-bg-color",
    getDynamicColor()
  );
})();
