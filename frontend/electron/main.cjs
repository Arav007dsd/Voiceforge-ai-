const { app, BrowserWindow, shell } = require('electron')
const createWindow = () => {
  const win = new BrowserWindow({ width: 1440, height: 940, minWidth: 900, minHeight: 650, backgroundColor: '#09090f', autoHideMenuBar: true, webPreferences: { contextIsolation: true, nodeIntegration: false } })
  win.loadURL('https://voiceforge-ai-lemon.vercel.app')
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' } })
}
app.whenReady().then(() => { createWindow(); app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow() }) })
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
