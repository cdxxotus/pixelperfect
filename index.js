const { app, BrowserWindow, ipcMain } = require("electron")
const robot = require("robotjs")
const { createCanvas, Image } = require("canvas")
const path = require("path")
const axios = require("axios")

let win
const NUM_PIXELS_TO_CHANGE = 1000
const INITIAL_COLOR = "#FFFFFF"
let pixelMap = []
let previousChanges = []
let currentBase64Img = null
const REGION_SIZE = 300

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
  context.fillStyle = INITIAL_COLOR
  context.fillRect(0, 0, width, height)

  // Initialize the pixel map
  for (let y = 0; y < height; y++) {
    pixelMap[y] = []
    for (let x = 0; x < width; x++) {
      pixelMap[y][x] = {
        color: INITIAL_COLOR,
        changeColor: (color) => {
          context.fillStyle = color
          context.fillRect(x, y, 1, 1)
          pixelMap[y][x].color = color
        },
      }
    }
  }

  // Function to update and stream the canvas
  const updateAndStreamCanvas = () => {
    console.log("Updating and streaming canvas...")

    // Generate a random color for this frame
    const color = getRandomColor()
    console.log("Generated color:", color)

    // If no previous changes, initialize with random starting point
    if (previousChanges.length === 0) {
      const startX = Math.floor(Math.random() * width)
      const startY = Math.floor(Math.random() * height)
      console.log("Initial start coordinates:", { startX, startY })
      for (let i = 0; i < NUM_PIXELS_TO_CHANGE; i++) {
        const x = (startX + i) % width
        const y = startY + Math.floor((startX + i) / width)
        if (y < height) {
          pixelMap[y][x].changeColor(color)
          previousChanges.push({ x, y })
        }
      }
    } else {
      // Change colors based on previous changes
      let newChanges = []
      for (
        let i = 0;
        i < previousChanges.length && newChanges.length < NUM_PIXELS_TO_CHANGE;
        i++
      ) {
        const { x, y } = previousChanges[i]
        const directions = [
          { dx: 1, dy: 0 },
          { dx: -1, dy: 0 },
          { dx: 0, dy: 1 },
          { dx: 0, dy: -1 },
        ]
        for (const { dx, dy } of directions) {
          const newX = (x + dx + width) % width
          const newY = (y + dy + height) % height
          if (
            pixelMap[newY][newX].color === INITIAL_COLOR &&
            newChanges.length < NUM_PIXELS_TO_CHANGE
          ) {
            pixelMap[newY][newX].changeColor(color)
            newChanges.push({ x: newX, y: newY })
          }
        }
      }
      previousChanges = newChanges
    }

    // Stream the updated canvas to the renderer process
    currentBase64Img = canvas.toDataURL("image/png").split(",")[1]
    console.log("Streaming updated canvas image...")
    win.webContents.send("base64-image", currentBase64Img)
  }

  // Function to capture a 300px x 300px region around the cursor from the canvas
  const captureRegionAroundCursor = (mouse) => {
    const x = Math.max(0, mouse.x - REGION_SIZE / 2)
    const y = Math.max(0, mouse.y - REGION_SIZE / 2)

    const regionCanvas = createCanvas(REGION_SIZE, REGION_SIZE)
    const regionContext = regionCanvas.getContext("2d")

    // Draw the region from the main canvas to the region canvas
    regionContext.drawImage(
      canvas,
      x,
      y,
      REGION_SIZE,
      REGION_SIZE,
      0,
      0,
      REGION_SIZE,
      REGION_SIZE
    )

    const base64Data = regionCanvas.toDataURL("image/png").split(",")[1]
    console.log("Captured region base64:", base64Data)
    return base64Data
  }

  // Event listeners for mouse movement
  let prevMouse = robot.getMousePos()
  setInterval(() => {
    const mouse = robot.getMousePos()
    if (mouse.x !== prevMouse.x || mouse.y !== prevMouse.y) {
      console.log("Mouse moved to:", mouse)
      updateAndStreamCanvas()
      prevMouse = mouse
    }
  }, 1000 / 70)

  setTimeout(() => {}, 3 * 1000)

  // Event listener for mouse clicks
  ipcMain.on("mouse-click", () => {
    console.log("Mouse click detected")
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

async function getInventedTextFromImage() {
  const image = captureRegionAroundCursor(robot.getMousePos())
  try {
    const response = await axios.post(
      "http://localhost:5000/get_invented_text_from_image",
      {
        image_data: image,
      }
    )
    console.log("Invented text response:", response.data)
    return response.data
  } catch (error) {
    console.error("Error getting invented text from image:", error)
  }
}

async function getHomeScreenDescription() {
  try {
    const response = await axios.post(
      "http://localhost:5000/get_home_screen_description"
    )
    console.log("Home screen description response:", response.data)
    return response.data.os_home_screen_description
  } catch (error) {
    console.error("Error getting home screen description:", error)
  }
}

async function getColorPalet(osDescription) {
  try {
    const response = await axios.post(
      "http://localhost:5000/get_colors_from_text",
      {
        text: osDescription,
      }
    )
    console.log("Color palette response:", response.data)
    return response.data
  } catch (error) {
    console.error("Error getting color palette:", error)
  }
}

const init = async () => {
  const osHomeScreenDescription = await getHomeScreenDescription()
  if (osHomeScreenDescription) {
    const colorPalette = await getColorPalet(osHomeScreenDescription)
    console.log("Final color palette:", colorPalette)
    const inv = await getInventedTextFromImage()
    console.log("Invented text:", inv)
  }
}

init()
