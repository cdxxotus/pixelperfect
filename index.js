const { app, BrowserWindow, ipcMain } = require("electron")
const robot = require("robotjs")
const { createCanvas } = require("canvas")
const path = require("path")

let win
const NUM_PIXELS_TO_CHANGE = 1000

const createWindow = () => {
  win = new BrowserWindow({
    fullscreen: true, // Enable full-screen mode
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false, // Disable nodeIntegration for security
      contextIsolation: true, // Enable contextIsolation
    },
  })
  win.loadFile("index.html")
}

app.whenReady().then(() => {
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  const { width, height } = win.getBounds()
  let canvas = createCanvas(width, height)
  let context = canvas.getContext("2d")

  // Initialize the canvas with a white background
  context.fillStyle = "#FFFFFF"
  context.fillRect(0, 0, width, height)

  // Function to update and stream the canvas
  const updateAndStreamCanvas = () => {
    // Clear the canvas
    context.fillStyle = "#FFFFFF"
    context.fillRect(0, 0, width, height)

    // Generate a random color for this frame
    const color = getRandomColor()
    context.fillStyle = color

    // Randomly choose a starting point
    const startX = Math.floor(Math.random() * width)
    const startY = Math.floor(Math.random() * height)

    // Draw a block of pixels next to each other
    for (let i = 0; i < NUM_PIXELS_TO_CHANGE; i++) {
      const x = (startX + i) % width
      const y = startY + Math.floor((startX + i) / width)
      if (y < height) {
        context.fillRect(x, y, 1, 1)
      }
    }

    // Stream the updated canvas to the renderer process
    const base64Image = canvas.toDataURL("image/png").split(",")[1]
    win.webContents.send("base64-image", base64Image)
  }

  // Event listeners for mouse movement and clicks
  let prevMouse = robot.getMousePos()
  setInterval(() => {
    const mouse = robot.getMousePos()
    if (mouse.x !== prevMouse.x || mouse.y !== prevMouse.y) {
      updateAndStreamCanvas()
      prevMouse = mouse
    }
  }, 1000 / 70)

  ipcMain.on("mouse-click", () => {
    updateAndStreamCanvas()
  })

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit()
  })
})

// Function to generate a random color
function getRandomColor() {
  const r = Math.floor(Math.random() * 256)
  const g = Math.floor(Math.random() * 256)
  const b = Math.floor(Math.random() * 256)
  return `rgb(${r}, ${g}, ${b})`
}
