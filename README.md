# SchulterPlan — 3D Shoulder Surgical Planning

Real-time 3D surgical planning tool for shoulder arthroplasty with Implantcast Agilon implants. Built with Three.js, deployed on Vercel.

## Features

### Main Planner (`/`)
- **3D Viewer**: Interactive Three.js visualization of scapula + implant
- **Multiple Views**: Anterior, Glenoid (face-on), Lateral, Inferior perspectives
- **Position Controls**: Adjust retroversion, inclination, depth, translation, axial rotation
- **Measurement Tools**: 
  - Manual 3D measurement with point-to-point distance
  - Auto-measure: Automatic distance to glenoid rim (inferior & anterior)
  - Center line visualization
- **Bone Contact Analysis**: Heatmap showing implant-bone contact area
- **Case Import**: Load patient cases from `planning.json`
- **Implant Selection**: 6 Implantcast Agilon variants + TechImport

### Surgery Dashboard (`/surgery-dashboard.html`)
- **Landscape Layout**: Optimized for large displays/TVs in operating room
- **6 Specialized Viewports**:
  1. Scapula only (no implant) — Glenoid view
  2. Scapula + Implant — Glenoid view
  3. Auto-measure visualization (Inferior + Anterior distances)
  4. Center line — Inferior view
  5. Center line — Lateral view
  6. Center line — All-around reference
- **Real-time Sync**: Reflects planned implant position with proper matrix transformations
- **AI Assistant Panel**: Right sidebar for surgical notes & voice recording

## Technical Stack

- **Frontend**: Vanilla JavaScript (ES modules), Three.js r160
- **3D Models**: 
  - STL format: Implants (Agilon Nº2, Nº3 Short/Long, Round 3, TechImport)
  - OBJ format: Scapula, Baseplates (Exactech catalog)
  - Back-surface models for bone contact analysis
- **Matrix Format**: Row-major 4×4 transformations (GPS standard)
- **Lighting**: Ambient + directional lights for clinical visualization

## Data Structure

```
data/
├── planning.json                    # Case: patient ref → glenoid → implant transforms
├── scapula.obj                      # Patient's scapula anatomy
├── glenoid_anat_2_back.stl         # Implant back surface (for contact analysis)
├── glenoid_anat_[2|3]_[short|long].stl  # Agilon Nº2/3 variants
├── glenoid_round_3.stl             # Agilon Round 3
├── techimport.stl                  # TechImport implant
└── baseplate_*.obj                 # Baseplate options (Exactech)
```

## Deployment

### Vercel (Recommended)

```bash
# Clone and navigate to project
cd schulterplan-vercel

# Deploy
vercel deploy
```

Vercel will:
- Serve static files (HTML, JS, models)
- Cache 3D models with long-term cache headers
- Auto-scale for concurrent users

### Local Development

```bash
npm start
# or
python3 -m http.server 8000
```

Visit `http://localhost:8000` (or `http://localhost:3000` for dev server)

## Browser Requirements

- WebGL-capable browser (Chrome, Firefox, Safari, Edge)
- Minimum 512MB RAM for 3D rendering
- Recommended: 1920×1080 or higher for full dashboard view

## Usage Notes

1. **Planning Page** (`/`)
   - Load case from `data/planning.json`
   - Adjust implant position with sliders
   - View bone contact in real-time
   - Measure distances manually or auto-measure

2. **Surgery Dashboard** (`/surgery-dashboard.html`)
   - Full-screen landscape layout
   - No scrolling needed (fits 1920×1080 displays)
   - Use arrow keys or mouse to rotate views
   - Right panel for surgical notes

## Matrix System

- **GPS Format**: Row-major 4×4 matrices (arrays of 16 floats)
- **Parsing**: `flatToMatrix4(arr)` converts flat arrays to Three.js Matrix4
- **Transform Chain**: `I2P = P2G × adjustM × I2G_orig`
  - `I2G`: Implant → Local Glenoid frame
  - `adjustM`: Adjustment matrix (retroversion, inclination, depth, translation)
  - `P2G`: Patient Reference → Glenoid frame
  - `I2P`: Final Implant → Patient transform

## Calibration

- **Contact Analysis**: Thresholds calibrated for clinical accuracy (embedded < -1mm, contact < 0mm, near < 0.5mm)
- **Auto-Measure**: Expects 12–26mm for glenoid rim distances (clinically validated range)
- **Measurement Colors**: 6 rotating colors for multi-point distance tracks

## Known Limitations

- Back-surface models required for accurate bone contact analysis
- Only one case at a time (planning.json)
- No real-time sync with surgical navigation systems (future feature)

## Author

Dr. Bruno Gobbato (bgobbato@gmail.com)

## License

Proprietary — Medical use only

---

**Last Updated**: May 24, 2026  
**Version**: 1.0 (SchulterPlan Implantcast Edition)
