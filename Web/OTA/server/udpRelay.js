const dgram = require('dgram');
const express = require('express');
const router = express.Router();

// UDP relay endpoint: /api/udp?ip=...&msg=...
router.get('/', async (req, res) => {
  const { ip, msg } = req.query;
  if (!ip || !msg) return res.status(400).send('Missing ip or msg');
  const udpPort = 4210; // Default port for your devices
  const client = dgram.createSocket('udp4');
  const message = Buffer.from(msg);
  client.send(message, 0, message.length, udpPort, ip, (err) => {
    client.close();
    if (err) return res.status(500).send('UDP send error: ' + err);
    res.send('Sent');
  });
});

module.exports = router;
