const { app, BrowserWindow } = require("electron")
const robot = require("robotjs")

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  win.loadFile("index.html")
  win.setFullScreen(true)
}

app.whenReady().then(() => {
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Periodically check mouse position
setInterval(() => {
  const mouse = robot.getMousePos()
  console.log("Mouse position:", mouse)
}, 100) // Adjust interval as needed

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit()
})
