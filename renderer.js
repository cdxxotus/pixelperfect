document.addEventListener("DOMContentLoaded", () => {
  window.electron.onBase64Image((base64Image) => {
    const img = new Image()
    img.src = `data:image/png;base64,${base64Image}`
    document.body.appendChild(img)
  })
})
