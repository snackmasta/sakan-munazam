const express = require('express');
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const app = express();
const PORT = 5000;

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

const devicesFile = path.join(dataDir, 'devices.json');

// Function to save device data
function saveDeviceData() {
  try {
    fs.writeFileSync(devicesFile, JSON.stringify(deviceFirmware, null, 2));
  } catch (error) {
    console.error('Error saving device data:', error);
  }
}

// Load device firmware data
let deviceFirmware;
try {
  if (fs.existsSync(devicesFile)) {
    const data = fs.readFileSync(devicesFile, 'utf8');
    try {
      deviceFirmware = JSON.parse(data);
    } catch (parseError) {
      console.error('Error parsing device data, starting with empty list:', parseError);
      deviceFirmware = {};
    }
  } else {
    deviceFirmware = {
      'esp1': { version: '1.0.3', file: 'firmware_esp1.bin' },
      'esp2': { version: '1.0.3', file: 'firmware_esp2.bin' }
    };
    saveDeviceData();
  }
} catch (error) {
  console.error('Error accessing device data file:', error);
  deviceFirmware = {};
}

// Configure multer for firmware file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, __dirname);
  },
  filename: (req, file, cb) => {
    const deviceId = req.body.deviceId;
    if (deviceFirmware[deviceId]) {
      const oldPath = path.join(__dirname, deviceFirmware[deviceId].file);
      if (fs.existsSync(oldPath)) {
        fs.unlinkSync(oldPath); // Remove old firmware file
      }
      const newFileName = `firmware_${deviceId}.bin`;
      deviceFirmware[deviceId].file = newFileName;
      saveDeviceData(); // Save changes to file
      cb(null, newFileName);
    } else {
      cb(new Error('Invalid device ID'));
    }
  }
});
const upload = multer({ storage });

// Add JSON body parser
app.use(express.json());

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Endpoint to get all devices
app.get('/devices', (req, res) => {
  const devices = Object.entries(deviceFirmware).map(([id, data]) => ({
    id,
    version: data.version,
    file: data.file
  }));
  res.json(devices);
});

// Endpoint to add new device
app.post('/device', (req, res) => {
  const { deviceId } = req.body;
  if (!deviceId) {
    return res.status(400).json({ error: 'Device ID is required' });
  }
  if (deviceFirmware[deviceId]) {
    return res.status(400).json({ error: 'Device ID already exists' });
  }
  
  deviceFirmware[deviceId] = {
    version: '1.0.0',
    file: `firmware_${deviceId}.bin`
  };
  
  saveDeviceData(); // Save changes to file
  res.json({ success: true, device: { id: deviceId, ...deviceFirmware[deviceId] } });
});

// Endpoint to rename device
app.post('/rename-device', (req, res) => {
  const { oldId, newId } = req.body;
  if (!oldId || !newId || !deviceFirmware[oldId]) {
    return res.status(400).json({ error: 'Invalid device IDs' });
  }
  if (deviceFirmware[newId]) {
    return res.status(400).json({ error: 'New device ID already exists' });
  }

  const oldFirmware = deviceFirmware[oldId];
  const oldPath = path.join(__dirname, oldFirmware.file);
  const newFileName = `firmware_${newId}.bin`;
  const newPath = path.join(__dirname, newFileName);

  deviceFirmware[newId] = {
    version: oldFirmware.version,
    file: newFileName
  };

  if (fs.existsSync(oldPath)) {
    fs.renameSync(oldPath, newPath);
  }
  
  delete deviceFirmware[oldId];
  saveDeviceData(); // Save changes to file
  res.json({ success: true, device: { id: newId, ...deviceFirmware[newId] } });
});

// Endpoint to update firmware version
app.post('/update-version', (req, res) => {
  const { deviceId, version } = req.body;
  if (!deviceId || !version || !deviceFirmware[deviceId]) {
    return res.status(400).json({ error: 'Invalid device ID or version' });
  }
  deviceFirmware[deviceId].version = version;
  saveDeviceData(); // Save changes to file
  res.json({ success: true, version });
});

// Endpoint to upload firmware
app.post('/upload-firmware', upload.single('firmware'), (req, res) => {
  const { deviceId } = req.body;
  if (!deviceId || !deviceFirmware[deviceId]) {
    return res.status(400).json({ error: 'Invalid device ID' });
  }
  res.json({ success: true });
});

// Endpoint to get the latest firmware version for a device
app.get('/version', (req, res) => {
  const deviceId = req.query.deviceId;
  if (!deviceId || !deviceFirmware[deviceId]) {
    return res.status(404).json({ error: 'Device not found' });
  }
  res.json({ version: deviceFirmware[deviceId].version });
});

// Endpoint to download the firmware binary for a device
app.get('/firmware', (req, res) => {
  const deviceId = req.query.deviceId;
  if (!deviceId || !deviceFirmware[deviceId]) {
    return res.status(404).json({ error: 'Device not found' });
  }
  const firmwarePath = path.join(__dirname, deviceFirmware[deviceId].file);
  res.download(firmwarePath, deviceFirmware[deviceId].file);
});

const udpRelay = require('./server/udpRelay');
app.use('/api/udp', udpRelay);

const calibPairs = require('./server/calibPairs');
app.use('/api/calib-pairs', calibPairs);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`OTA server running on http://0.0.0.0:${PORT}`);
});
