const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

const PAIRS_FILE = path.join(__dirname, '../data/calib_pairs.json');

// Save pairs (POST)
router.post('/', (req, res) => {
  const pairs = req.body;
  if (!Array.isArray(pairs)) return res.status(400).json({error: 'Invalid data'});
  fs.writeFile(PAIRS_FILE, JSON.stringify(pairs, null, 2), err => {
    if (err) return res.status(500).json({error: 'Failed to save'});
    res.json({success: true});
  });
});

// Load pairs (GET)
router.get('/', (req, res) => {
  fs.readFile(PAIRS_FILE, 'utf8', (err, data) => {
    if (err) return res.json([]);
    try {
      const pairs = JSON.parse(data);
      res.json(pairs);
    } catch {
      res.json([]);
    }
  });
});

module.exports = router;
