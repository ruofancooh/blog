function toggleIframe(songType, songId, contianerId, aId) {
  let container = document.getElementById(contianerId);
  let a = document.getElementById(aId);
  if (container === null) {
    console.log("未获取到contianer");
  } else if (container.childNodes.length !== 1) {
    container.removeChild(container.lastChild);
    a.innerText = "点此收听";
  } else {
    let iframe = document.createElement("iframe");
    iframe.frameBorder = "no";
    iframe.width = "100%";
    iframe.height = 86;
    iframe.src = `//music.163.com/outchain/player?type=${songType}&id=${songId}&auto=0&height=66`;
    container.appendChild(iframe);
    a.innerText = "点此收起";
  }
}