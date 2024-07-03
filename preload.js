const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("electron", {
  onBase64Image: (callback) =>
    ipcRenderer.on("base64-image", (event, base64Image) =>
      callback(base64Image)
    ),
  sendMouseClick: () => ipcRenderer.send("mouse-click"),
})
