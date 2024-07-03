const { app, BrowserWindow, ipcMain } = require("electron")
const robot = require("robotjs")
const { createCanvas } = require("canvas")
const path = require("path")

let win

const createWindow = () => {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false, // Disable nodeIntegration for security
      contextIsolation: true, // Enable contextIsolation
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

  const { width, height } = win.getBounds()

  // Periodically generate and send the base64 image to the renderer process
  setInterval(() => {
    const base64Image = generateWhiteImage(width, height)
    win.webContents.send("base64-image", base64Image)
  }, 1000 / 25) // 25 images per second

  // Periodically check mouse position
  setInterval(() => {
    const mouse = robot.getMousePos()
    console.log("Mouse position:", mouse)
  }, 100)

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit()
  })
})

// Function to generate a white image
function generateWhiteImage(width, height) {
  const canvas = createCanvas(width, height)
  const context = canvas.getContext("2d")
  context.fillStyle = "#FFFFFF"
  context.fillRect(0, 0, width, height)
  return canvas.toDataURL("image/png").split(",")[1]
}
