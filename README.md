# 🏍️ 3D Motocross Game

An immersive 3D motocross racing simulator with realistic bike physics, multiple bike models, and dynamic track types.

## 🎮 Features

### Multiple Bikes
- **KTM 450** (Orange) - Lightweight, high RPM performer
  - Max RPM: 13,000
  - Mass: 180 kg
  - Power: +10% boost
  
- **Yamaha YZ** (Blue) - Balanced all-around bike
  - Max RPM: 12,500
  - Mass: 190 kg
  - Power: Standard
  
- **Honda CRF** (Red) - Stable and reliable
  - Max RPM: 12,000
  - Mass: 200 kg
  - Power: -5% reduction

### Track Types
- **Street Track** - Smooth asphalt with long straights
- **Motocross Track** - Rough terrain with jumps and obstacles

### Camera Modes
- **First-Person View** - Immersive rider's perspective
- **Third-Person View** - Follow camera behind the bike
- Toggle between modes with **P key**

### Realistic Physics
- Clutch-based start mechanics
- 6-speed transmission with manual gear shifts
- RPM-based power delivery
- Suspension dynamics
- Aerodynamic drag
- Bike lean based on speed

## 🚀 Installation & Running Locally

### Prerequisites
- Python 3.8+
- OpenGL-compatible graphics card

### Setup
```bash
# Clone the repository
git clone https://github.com/xhbshefj-rando/random.git
cd random

# Install dependencies
pip install -r requirements.txt

# Run the game
python motocross_game.py
```

## 🎮 Controls

| Control | Action |
|---------|--------|
| **UP / W** | Throttle |
| **CTRL / C** | Clutch (hold for smooth starts) |
| **SPACE** | Brake |
| **Q / E** | Downshift / Upshift |
| **P** | Toggle 1st/3rd Person View |
| **ESC** | Quit Game |

## 💡 Gameplay Tips

1. **Starting the Bike**
   - Hold CTRL/C to engage the clutch
   - Gradually release while applying throttle
   - Prevents stalling at low RPM

2. **Gear Management**
   - Shift up when RPM exceeds 8,000
   - Shift down for better acceleration in lower gears
   - Use 6th gear for top speed on straights

3. **Track Strategy**
   - Street Track: Maintain high speed on smooth sections
   - Motocross Track: Time your acceleration over jumps
   - Use the suspension effectively on rough terrain

## 🌐 Vercel Deployment

This game is optimized for local play. However, an API endpoint is provided for deployment:

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### API Endpoint
Once deployed, access the API at:
```
https://your-deployment.vercel.app/api/game
```

The API provides game information and bike/track data in JSON format.

**Note:** The full 3D game requires OpenGL and Pygame, which work best locally. The Vercel deployment serves an informational API only.

## 📁 Project Structure

```
.
├── motocross_game.py      # Main game executable
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── api/
│   ├── game.py           # Serverless API endpoint
│   └── requirements.txt   # API-specific dependencies
└── README.md              # This file
```

## 🛠️ Development

### Adding New Bikes
Edit the `_setup_bike_properties()` method in the `BikePhysics` class:

```python
BikeType.CUSTOM: {
    'name': 'Custom Bike',
    'max_rpm': 12000,
    'idle_rpm': 800,
    'mass': 195,
    'power_multiplier': 1.0,
    'color': (1.0, 1.0, 0.0)  # Yellow
}
```

### Modifying Track Layout
Adjust the `_generate_street_track()` or `_generate_motocross_track()` methods:

```python
# Change segment count
for i in range(100):  # Track length

# Modify track width
width = 4  # Street track

# Adjust jump height in motocross
height = 3  # Jump height
```

## 📋 System Requirements

- **OS:** Windows, macOS, or Linux
- **Python:** 3.8 or higher
- **RAM:** 2GB minimum
- **GPU:** Any OpenGL 2.0+ compatible GPU
- **Resolution:** 1200x800 minimum

## 🐛 Troubleshooting

### "No OpenGL context" error
- Update graphics drivers
- Ensure monitor is connected
- Try running in windowed mode

### Low FPS
- Close other applications
- Update graphics drivers
- Reduce track segments (modify range in `_generate_track()`)

### Pygame not installing
- Update pip: `pip install --upgrade pip`
- Try: `pip install pygame==2.5.2`

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to fork, modify, and submit improvements!

---

**Enjoy the ride! 🏁**
