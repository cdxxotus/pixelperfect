const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("electron", {
  onBase64Image: (callback) =>
    ipcRenderer.on("base64-image", (event, base64Image) =>
      callback(base64Image)
    ),
  onInitializeCanvas: (callback) =>
    ipcRenderer.on("initialize-canvas", (event, base64Image) =>
      callback(base64Image)
    ),
  sendMouseMove: (mousePos) => ipcRenderer.send("mouse-move", mousePos),
  sendMouseClick: () => ipcRenderer.send("mouse-click"),
})
