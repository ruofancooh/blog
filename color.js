const hsvToRgb = (h, s, v) => {
  let r,
    g,
    b,
    i = Math.floor(h * 6),
    f = h * 6 - i,
    p = v * (1 - s),
    q = v * (1 - f * s),
    t = v * (1 - (1 - f) * s);
  switch (i % 6) {
    case 0:
      (r = v), (g = t), (b = p);
      break;
    case 1:
      (r = q), (g = v), (b = p);
      break;
    case 2:
      (r = p), (g = v), (b = t);
      break;
    case 3:
      (r = p), (g = q), (b = v);
      break;
    case 4:
      (r = t), (g = p), (b = v);
      break;
    case 5:
      (r = v), (g = p), (b = q);
      break;
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
};
const rgbToHsv = (r, g, b) => {
  (r /= 255), (g /= 255), (b /= 255);
  let h,
    s,
    v = Math.max(r, g, b),
    d = v - Math.min(r, g, b);
  s = v === 0 ? 0 : d / v;
  if (v === d) h = 0;
  else
    switch (v) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / d + 2;
        break;
      case b:
        h = (r - g) / d + 4;
        break;
    }
  h /= 6;
  return [h, s, v];
};
const rgbToHex = (r, g, b) =>
  `#${((1 << 24) + (r << 16) + (g << 8) + b)
    .toString(16)
    .slice(1)
    .toUpperCase()}`;
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16),
      ]
    : null;
};
const update = (from) => {
  let r, g, b, h, s, v;
  if (from === "hsv") {
    h = +document.getElementById("hue").value;
    s = +document.getElementById("saturation").value;
    v = +document.getElementById("value").value;
    [r, g, b] = hsvToRgb(h, s, v);
    updateValues({ red: r, green: g, blue: b });
  } else if (from === "rgb") {
    r = +document.getElementById("red").value;
    g = +document.getElementById("green").value;
    b = +document.getElementById("blue").value;
    [h, s, v] = rgbToHsv(r, g, b);
    updateValues({ hue: h, saturation: s, value: v });
  } else if (from === "hex") {
    const hex = document.getElementById("hex").value;
    if (hex.length === 7 && hexToRgb(hex)) {
      [r, g, b] = hexToRgb(hex);
      [h, s, v] = rgbToHsv(r, g, b);
      updateValues({
        hue: h,
        saturation: s,
        value: v,
        red: r,
        green: g,
        blue: b,
      });
    }
  }
  updateDisplayValues({
    hue: h,
    saturation: s,
    value: v,
    red: r,
    green: g,
    blue: b,
  });
  const hex = rgbToHex(r, g, b);
  document.getElementById("hex").value = hex;
  document.getElementById("hexError").textContent = hexToRgb(hex)
    ? ""
    : "Invalid Hex Color";
  document.getElementById("colorBox").style.backgroundColor = hex;
};
const updateValues = (values) => {
  for (const [key, value] of Object.entries(values)) {
    document.getElementById(key).value = value;
  }
};
const updateDisplayValues = (values) => {
  for (const [key, value] of Object.entries(values)) {
    const displayElement = document.getElementById(`${key}Value`);
    if (displayElement) {
      displayElement.textContent =
        typeof value === "number" ? value.toFixed(2) : value;
    }
  }
};
["hue", "saturation", "value", "red", "green", "blue"].forEach((id) => {
  document
    .getElementById(id)
    .addEventListener("input", () =>
      update(
        id === "hue" || id === "saturation" || id === "value" ? "hsv" : "rgb"
      )
    );
});
document.getElementById("hex").addEventListener("input", (e) => {
  const hex = e.target.value;
  if (hex.length === 7) {
    update("hex");
  } else {
    document.getElementById("hexError").textContent = "Invalid Hex Color";
  }
});
update("hsv");
