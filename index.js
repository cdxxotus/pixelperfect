const { app, BrowserWindow } = require("electron")
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

  const { width, height } = win.getBounds()
  const base64Image = generateWhiteImage(width, height)

  // Send the base64 image to the renderer process
  win.webContents.on("did-finish-load", () => {
    win.webContents.send("base64-image", base64Image)
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

// Periodically check mouse position
setInterval(() => {
  const mouse = robot.getMousePos()
  console.log("Mouse position:", mouse)
}, 100) // Adjust interval as needed

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit()
})
