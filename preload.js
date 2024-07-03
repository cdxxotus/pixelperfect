const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("electron", {
  getWindowSize: () => ipcRenderer.invoke("get-window-size"),
  onBase64Image: (callback) =>
    ipcRenderer.on("base64-image", (event, data) => callback(data)),
})
