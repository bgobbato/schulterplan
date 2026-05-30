# GPS Web Planner

Web application for visualizing and modifying surgical planning of reverse
shoulder arthroplasty (Exactech GPS) online, with scenario management,
colleague sharing, and export back to the desktop software.

**Live URL**: http://195.35.18.141/gps/
**Local dev**: http://localhost:8765/

---

## Current status: DEPLOYED (VPS) — iteration 4 (2026-05-09) — mobile responsive

Fully functional web app deployed on a VPS behind Nginx reverse proxy.
Features: GPS case folder import, in-browser .mesh.bin parsing, 7 baseplate
types with laterality, 3D viewer with position controls, scenarios, comments,
sharing via view/edit links, .ini export, auto-placement from landmarks,
fully responsive mobile layout (works on phone and tablet).

---

## File layout (local development)

```
/Users/brunogobbato/Dropbox/3D/Exactech/gps-web-planner/
├── PROJECT.md              (this file)
├── index.html              (entire frontend: HTML + CSS + JS, ~1725 lines)
├── server.py               (Flask + SQLite backend, ~534 lines)
├── data/                   (read-only implant catalog + test data)
│   ├── planning.json           (default test case: Miria)
│   ├── scapula.obj             (Miria's scapula mesh)
│   ├── baseplate_standard.obj  (320-115-01_D — bilateral)
│   ├── baseplate_10sup.obj     (320-115-02_A — bilateral)
│   ├── baseplate_8post_left.obj    (320-115-03_- — LEFT only)
│   ├── baseplate_8post_right.obj   (320-115-04_- — RIGHT only)
│   ├── baseplate_extended.obj      (320-115-06_A — bilateral)
│   ├── baseplate_postsup_left.obj  (320-115-07_A — LEFT only)
│   └── baseplate_postsup_right.obj (320-115-08_A — RIGHT only)
├── storage/                (user-generated data — grows over time)
│   ├── gps.db                  (SQLite database)
│   └── cases/
│       └── <case_id>/
│           ├── scapula.bin         (uploaded mesh)
│           └── scapula_osteo.bin   (optional)
├── scenarios/              (sample GPS case folders for testing)
└── deploy/
    ├── PLAN.md                 (architecture planning document)
    ├── gps-web-planner.service (systemd unit file)
    └── nginx-snippet.conf      (Nginx proxy configuration)
```

## File layout (VPS)

```
/var/www/gps-web-planner/
├── server.py
├── index.html
├── data/                   (same as local)
├── storage/                (owned by www-data)
│   ├── gps.db
│   └── cases/
└── deploy/
```

---

## How to run

### Local development

```bash
cd /Users/brunogobbato/Dropbox/3D/Exactech/gps-web-planner
python3 server.py 8765
# open http://localhost:8765/
```

### Deploy to VPS

```bash
# Sync code (excludes storage to preserve uploaded cases)
rsync -avz --exclude='storage' --exclude='.claude' --exclude='__pycache__' \
  /Users/brunogobbato/Dropbox/3D/Exactech/gps-web-planner/ \
  root@195.35.18.141:/var/www/gps-web-planner/

# Restart the service
ssh root@195.35.18.141 "systemctl restart gps-web-planner"
```

---

## Architecture

### Frontend (index.html)

**No build step, no framework.** Everything in a single HTML file.

- **3D rendering**: Three.js v0.160.0 (loaded via CDN with importmap)
- **Loaders**: `OBJLoader` and `OrbitControls` from `three/addons/`
- **UI**: vanilla HTML/CSS with CSS Grid layout
- **State**: single in-memory `state` JavaScript object
- **Color palette**: Advita Ortho brand identity
  - Primary green: `#38B048` (buttons, active states)
  - Dark petrol: `#004858` (headings, title, hover states, toasts)
  - Teal accent: `#10A898`
  - Light green: `#88C038`
  - Background: `#f4f7f6` (subtle green tint)
  - 3D viewport: `#ecf3f2`

### Backend (server.py)

- **Framework**: Flask (single dependency beyond stdlib)
- **Database**: SQLite with WAL mode
- **Storage**: filesystem for binary mesh files
- **Auth**: token-based (edit_token per case, no user accounts)

### Deployment

```
Internet ──► VPS port 443 (Nginx, TLS)
                │
                ├─► location /gps/  → proxy_pass to 127.0.0.1:8765 (Flask)
                └─► location /      → existing PHP app (coe-fila)
```

- **systemd** keeps Flask alive (`gps-web-planner.service`)
- **Nginx** terminates TLS and routes `/gps/` to Flask
- VPS IP: `195.35.18.141`

---

## Database schema (SQLite)

```sql
CREATE TABLE cases (
  id                       TEXT PRIMARY KEY,        -- 8-char urlsafe random
  case_short_id            TEXT,                    -- from case.ini
  side                     TEXT NOT NULL,           -- 'LEFT' | 'RIGHT'
  surgeon                  TEXT,
  creator_name             TEXT,
  edit_token               TEXT NOT NULL,           -- secret for edit access

  preop_retroversion       REAL,
  preop_inclination        REAL,
  preop_subluxation        REAL,

  glenoid_plate            TEXT,
  orig_version             REAL,
  orig_inclination         REAL,
  orig_rotation            REAL,
  orig_implant_to_glenoid  TEXT,                    -- JSON array of 16 floats
  patient_to_glenoid       TEXT,                    -- JSON array of 16 floats

  scapula_path             TEXT NOT NULL,
  scapula_osteo_path       TEXT,

  created_at               INTEGER NOT NULL,
  updated_at               INTEGER NOT NULL
);

CREATE TABLE scenarios (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id           TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  slot              INTEGER,
  name              TEXT,
  author            TEXT,
  implant_type      TEXT,
  adj_retroversion  REAL DEFAULT 0,
  adj_inclination   REAL DEFAULT 0,
  adj_depth         REAL DEFAULT 0,
  adj_tx            REAL DEFAULT 0,
  adj_ty            REAL DEFAULT 0,
  adj_rotz          REAL DEFAULT 0,
  created_at        INTEGER NOT NULL,
  updated_at        INTEGER NOT NULL
);

CREATE TABLE comments (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id      TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  scenario_id  INTEGER REFERENCES scenarios(id) ON DELETE SET NULL,
  author       TEXT,
  text         TEXT NOT NULL,
  created_at   INTEGER NOT NULL
);

CREATE TABLE revisions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id      TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  author       TEXT,
  action       TEXT NOT NULL,
  payload_json TEXT,
  created_at   INTEGER NOT NULL
);
```

---

## API surface

```
POST   /api/cases                        Upload + create case (multipart)
GET    /api/cases                        List all cases
GET    /api/cases/:id                    Full case JSON (with scenarios + comments)
PATCH  /api/cases/:id                    Update metadata
DELETE /api/cases/:id                    Delete (edit-token required)

GET    /api/cases/:id/mesh/scapula       Binary mesh download
GET    /api/cases/:id/mesh/scapula_osteo Binary mesh download

GET    /api/cases/:id/scenarios          List scenarios
POST   /api/cases/:id/scenarios          Create scenario
PUT    /api/cases/:id/scenarios/:sid     Update scenario
DELETE /api/cases/:id/scenarios/:sid     Delete scenario

GET    /api/cases/:id/comments           List comments
POST   /api/cases/:id/comments           Add comment (no token needed)

GET    /api/cases/:id/revisions          Audit log
```

### Authentication model

- **View**: anyone with the case URL (`?case=<id>`) can view
- **Edit**: requires edit token (`?case=<id>&edit=<token>`)
- Edit token is returned at case creation and stored in `localStorage`
- API mutations check `X-Edit-Token` header or session

### Author identification

- "Your name" input shown on first edit attempt
- Stored in `localStorage`, sent as `X-Author` header
- Falls back to "Anonymous"

---

## Sharing model

Two URLs per case:

- **View-only**: `http://195.35.18.141/gps/?case=abc12345`
- **Edit**: `http://195.35.18.141/gps/?case=abc12345&edit=<token>`

The **Share** button opens a modal with two buttons:
- **EDIT** — copies the edit URL to clipboard
- **VIEW-ONLY** — copies the view URL to clipboard

Clipboard uses a fallback method (`execCommand('copy')` with hidden textarea)
because `navigator.clipboard.writeText()` requires HTTPS and the VPS serves
over plain HTTP.

---

## Implemented features (complete list)

### Case import

- **Import Case Folder** button accepts a GPS case directory (`webkitdirectory`)
- In-browser parser for `.mesh.bin` files (DataView → Three.js BufferGeometry)
- INI parser for `case.ini`, `landmarks.ini`, `reverse.ini`
- Auto-detects baseplate type from `GlenoidPlate` in `reverse.ini`
- Folder priority: `01-segmentation/` > `05-autoSegmentation/`
- Scapula priority: `03-osteophyte/scapula.mesh.bin` > `01-segmentation/` > `05-autoSegmentation/`
- **Auto-placement from landmarks** (NEW): when no `02-planning/reverse.ini`
  exists, computes the glenoid frame from Glenoid/Trigonum/InferiorPt points
  and places a STANDARD baseplate centered on the glenoid face

### Auto-placement algorithm (PatientRefToGlenoidRef from landmarks)

When `PatientRefToGlenoidRef` is not present in `landmarks.ini` (e.g.
`05-autoSegmentation/` cases without planning), it is computed from three
landmark points:

```
Z = normalize(Glenoid - Trigonum)
X = -normalize(cross(InferiorPt - Trigonum, Glenoid - Trigonum))
    orthogonalized against Z
Y = Z x X
Origin = Glenoid center
```

This produces a 4x4 matrix identical to what the GPS desktop software
computes. Verified against two real cases (FRANK and YONARA) with zero error.

The default `transfoFromImplantToLocalGlenoidRef` is the identity matrix,
placing the baseplate centered on the glenoid face with no offset.

### 3D viewer

- Bone-colored scapula (`#e6dbc7`)
- Blue baseplate (`#1e88e5`, Phong material with shininess 80)
- OrbitControls (drag to rotate, scroll to zoom, right-click to pan)
- Ambient + 2 directional lights
- 3D scene background: `#ecf3f2` (subtle teal tint)

### View presets

- **Anterior** — camera looking from the front
- **Glenoid** — camera looking straight at the glenoid face (default)
- **Lateral** — camera from the side

All views use the glenoid local frame vectors derived from `PatientRefToGlenoidRef`:
- `glenoidNormal` (Z column) — glenoid face direction
- `glenoidUp` (Y column) — superior direction
- `glenoidRight` (X column) — anterior/posterior direction

### Implant controls

- **Retroversion** (← →): +/- 1° rotation around Y axis
- **Inferior Inclination** (↓ ↑): +/- 1° rotation around X axis
- **Depth** (- +): +/- 1mm translation along Z axis
- **SI Translation** (↑ ↓): +/- 1mm along Y
- **AP Translation** (← →): +/- 1mm along X
- **Axial Rotation** (↻): +1° around Z
- **Reset**: restores the original planning (or identity for auto-placed)

### Math: implant positioning

```
implant_to_patient = PatientRefToGlenoidRef @ adjust @ transfoFromImplantToLocalGlenoidRef
```

The `adjust` matrix is built from `state.adjust` values in the GLENOID LOCAL
frame (Euler XYZ rotations + translations). This is independent of patient pose.

> **CRITICAL**: Despite the name, `PatientRefToGlenoidRef` goes
> **Glenoid → Patient** (NOT Patient → Glenoid). Do NOT invert it.

### Toggle buttons

- **Show/Hide Implant** — toggles baseplate visibility
- **Transparent Bone** — sets scapula opacity to 50%
- **Remove Osteophytes** — swaps scapula to `03-osteophyte/` version (appears
  only when the file exists)

### Scenarios

- 3 slots for saved scenarios
- Each scenario stores: implant type + 6 adjustment values (retroversion,
  inclination, depth, tx, ty, rotz)
- Click to load, "Save Current Scenario" to save to first empty slot
- Scenarios sync to server when online (with edit token)

### Comments

- Anyone can add comments (no edit token required)
- Shown in the right sidebar below implant controls
- Comments are attributed to the author name from `localStorage`

### Export

- **Export .ini** — generates a `reverse.ini` file with the modified
  `transfoFromImplantToLocalGlenoidRef` matrix, compatible with the desktop
  GPS software for re-import

### Sharing

- **Share** button opens a modal with EDIT / VIEW-ONLY buttons
- Copies the appropriate URL to clipboard
- Uses fallback clipboard method for HTTP (non-HTTPS) environments
- View-only mode disables all edit controls

### Server persistence

- Cases uploaded via multipart POST (metadata JSON + binary mesh files)
- SQLite database with WAL mode for concurrent reads
- Binary meshes stored as files on disk (`storage/cases/<id>/`)
- Audit log (revisions table) tracks all mutations

### Mobile responsive layout

Fully responsive via CSS media query (`max-width: 768px`). Viewport meta tag
included. Works on iPhone, Android, and tablets.

**Mobile layout order (top to bottom):**
1. Top bar — title + view buttons + action buttons (wraps to 2 rows)
2. 3D Viewer — full width, fixed height (55vw, min 240px, max 380px)
3. Implant Position controls — right sidebar content, touch-friendly (44px targets)
4. Comments
5. Pre-Op Measurements + Implant Selection + Saved Scenarios — left sidebar content

**Mobile-specific adaptations:**
- `ctrl-btn` height: 44px (minimum recommended touch target)
- Arrow cross grid: 44×44px cells
- Implant grid: 3 columns (2 on screens < 400px)
- Scenarios: horizontal row (3 side by side)
- Footer actions: 2-column grid
- Share modal: 90vw width
- `ResizeObserver` on the viewer div to update Three.js renderer when
  CSS-driven size changes (e.g. on orientation change)

---

## Implant catalog

### Full mapping table

| Source file (320-115-XX) | Clinical name | Laterality | Web app file | Planning key(s) |
|--------------------------|---------------|------------|--------------|-----------------|
| 01_D | STANDARD | bilateral | `baseplate_standard.obj` | `Standard/Standard` |
| 02_A | 10 SUP AUG | bilateral | `baseplate_10sup.obj` | `SupAugmentGP10/Standard` |
| 03_- | 8 POST AUG LEFT | LEFT only | `baseplate_8post_left.obj` | `PostAugmentGP8/Standard` |
| 04_- | 8 POST AUG RIGHT | RIGHT only | `baseplate_8post_right.obj` | `PostAugmentGP8/Standard` |
| 06_A | EXTENDED | bilateral | `baseplate_extended.obj` | `StandardLong/Standard` |
| 07_A | POST SUP LEFT | LEFT only | `baseplate_postsup_left.obj` | `PostSupAugmentGP/Standard` |
| 08_A | POST SUP RIGHT | RIGHT only | `baseplate_postsup_right.obj` | `PostSupAugmentGP/Standard` |

### Laterality rule

Augmented baseplates (8 Post Aug, Post Sup) have LEFT/RIGHT mirror variants
and require the correct file based on `case.ini` side. Standard, Extended, and
10 Sup Aug use the same file for both sides.

### IMPLANT_TYPES structure (in code)

```javascript
const IMPLANT_TYPES = {
  STANDARD:    { label:'STANDARD',     fileBySide:{LEFT:'...', RIGHT:'...'}, planningKeys:[...] },
  '8_POST_AUG':{ label:'8 POST AUG',  fileBySide:{LEFT:'...left.obj', RIGHT:'...right.obj'}, ... },
  '10_SUP_AUG':{ label:'10 SUP AUG',  fileBySide:{LEFT:'...', RIGHT:'...'}, ... },
  EXTENDED:    { label:'EXTENDED',     fileBySide:{LEFT:'...', RIGHT:'...'}, ... },
  POST_SUP:    { label:'POST SUP',     fileBySide:{LEFT:'...left.obj', RIGHT:'...right.obj'}, ... }
};
```

### Planning key resolution

`resolveImplantFromPlanning(planningGlenoidPlate, side)`:
1. Strips optional LEFT/RIGHT prefix from the planning string
2. Extracts `TYPE/SIZE` substring
3. Looks up in `PLANNING_KEY_TO_TYPE` map
4. Returns `{ typeKey, file }` with the correct side-specific file

---

## Binary format: .mesh.bin (Exactech GPS proprietary)

| Offset | Size | Type | Content |
|--------|------|------|---------|
| 0x00 | 44 bytes | ASCII | `"caseId" : "XXX", "area" = "YYY"` |
| 0x2C | 48 bytes | — | Zero padding |
| 0x5C | 4 bytes | uint32 BE | Vertex count (n_verts) |
| 0x60 | n_verts*24 | float64 LE | Vertices (x, y, z triplets) |
| — | 4 bytes | uint32 BE | Separator (= n_verts) |
| — | n_verts*24 | float64 LE | Normals (nx, ny, nz triplets) |
| — | 4 bytes | uint32 BE | Index count (= n_faces * 3) |
| — | n_faces*12 | uint32 LE | Face indices (0-indexed) |

The in-browser parser (`parseMeshBin()`) reads this format using DataView and
constructs a Three.js BufferGeometry with position, normal, and index attributes.

---

## GPS case folder structure

```
CaseId_YYYY-MM-DD-HHMMSS/
  case.ini                  # patient info, side, surgeon
  patient.private           # encrypted patient data (not used)
  00-dicom/                 # original CT DICOM files (not used)
  01-segmentation/          # full segmentation (after planning)
    scapula.mesh.bin
    humerus.mesh.bin         (not used)
    glenoid.mesh.bin         (not used)
    coracoid.mesh.bin        (not used)
    landmarks.ini            # PatientRefToGlenoidRef + anatomical points
    hlandmarks.ini           (not used)
  02-planning/              # planning results (may not exist)
    reverse.ini              # GlenoidPlate, matrix, angles
    reverse_hum.ini          (not used)
  03-osteophyte/            # optional
    scapula.mesh.bin         # scapula after osteophyte removal
  05-autoSegmentation/      # auto-segmentation (before planning)
    scapula.mesh.bin
    landmarks.ini            # anatomical landmarks (no PatientRefToGlenoidRef)
    autoSegVolume.ct.bin     (not used)
    initialVolume.ct.bin     (not used)
```

### Import priority

1. **Landmarks**: `01-segmentation/landmarks.ini` > `05-autoSegmentation/landmarks.ini`
2. **Scapula mesh**: `03-osteophyte/scapula.mesh.bin` (if exists) OR
   `01-segmentation/scapula.mesh.bin` > `05-autoSegmentation/scapula.mesh.bin`
3. **Planning**: `02-planning/reverse.ini` (optional — auto-places if missing)
4. **Side**: `landmarks.Infos.side` > `case.ini.Infos.side`

---

## Key landmarks in landmarks.ini

| Key | Description | Used for |
|-----|-------------|----------|
| `Glenoid` | Glenoid center point (x, y, z) | Frame origin |
| `GlAnt` | Anterior glenoid rim | Orientation reference |
| `GlPost` | Posterior glenoid rim | Orientation reference |
| `GlSup` | Superior glenoid rim | Orientation reference |
| `GlInf` | Inferior glenoid rim | Orientation reference |
| `Trigonum` | Medial scapular body (trigonum spinae) | Frame Z axis |
| `InferiorPt` | Inferior scapular angle | Frame X axis (scapular plane) |
| `PatientRefToGlenoidRef` | 4x4 matrix (Glenoid→Patient) | Implant positioning |
| `BasisRotation` | Manual correction angle (usually 0) | Not used |
| `WearPlane` | Glenoid wear pattern (plane equation) | Not used |
| `GlenoidHelp1-4` | Glenoid articular surface rim points | Not used |

---

## Transformation chain

### Standard import (with reverse.ini)

```
implant_to_patient = PatientRefToGlenoidRef @ transfoFromImplantToLocalGlenoidRef
```

Both matrices come directly from the GPS case files.

### Auto-placement (without reverse.ini)

```
PatientRefToGlenoidRef = computed from Glenoid, Trigonum, InferiorPt
transfoFromImplantToLocalGlenoidRef = identity (4x4)
```

Baseplate is centered on the glenoid face with no offset or rotation.

### User adjustments

```
implant_to_patient = PatientRefToGlenoidRef @ adjust_matrix @ transfoFromImplantToLocalGlenoidRef
```

Where `adjust_matrix` encodes the user's retroversion, inclination, depth,
translation, and rotation changes in the glenoid local frame.

---

## Visual identity: Advita Ortho

Brand colors extracted from the official Advita visual identity PDF
(`advita.pdf`):

| Color | Hex | CSS variable | Usage |
|-------|-----|-------------|-------|
| Primary green | `#38B048` | `--blue` | Buttons, active states, view buttons |
| Dark petrol | `#004858` | `--blue-dark` | Title, headings, hover states, toasts |
| Teal | `#10A898` | `--accent` | Accent elements |
| Lime green | `#88C038` | `--green` | Secondary accent |
| Light bg | `#f4f7f6` | `--bg` | Page background |
| Panel white | `#ffffff` | `--panel` | Sidebar/topbar backgrounds |
| Border | `#c0d4d0` | `--border` | Teal-tinted borders |
| Text | `#1a2e2e` | `--text` | Primary text color |
| Muted text | `#567070` | `--muted` | Secondary text, labels |

Brand color extraction method: pixel sampling from the Advita visual identity
PDF (page 2 — AI logo wheel) using Python PIL. Dominant colors identified via
histogram bucketing at 8-pixel resolution.

---

## Bugs fixed (complete history)

1. **Matrix inversion error**: Initially computed
   `implant_to_patient = inv(PatientRefToGlenoidRef) @ I2G` which placed the
   implant ~440mm away. Fixed: `PatientRefToGlenoidRef` goes Glenoid→Patient
   despite its name — use directly, do NOT invert.

2. **Upside-down glenoid view**: Camera up vector was negated
   (`.negate()`). Fixed: use `glenoidUp.clone()` directly.

3. **Implant catalog key mismatch**: `IMPLANT_CATALOG` was keyed by planning
   name but `setImplant()` looked up by short key. Fixed by creating proper
   `PLANNING_KEY_TO_TYPE` reverse lookup.

4. **Python 3.9 type hints**: Used `Path | None` (requires 3.10+). Fixed by
   removing type hints.

5. **Nginx backup conflict**: Backup file placed in `sites-enabled/` caused
   conflicting `server_name`. Fixed by moving to `/root/`.

6. **Clipboard on HTTP**: `navigator.clipboard.writeText()` requires HTTPS.
   Fixed by adding fallback using `document.execCommand('copy')` with a
   hidden textarea.

7. **Share popup UX**: Browser `confirm()` dialog replaced with a proper
   HTML modal with EDIT / VIEW-ONLY buttons and clipboard confirmation
   message.

8. **Auto-placement missing**: Cases with only `05-autoSegmentation/`
   (no planning) would throw an error. Fixed by computing
   `PatientRefToGlenoidRef` from landmark points and using identity transform
   for the baseplate.

---

## Known limitations

- **Rotation axis convention** may not exactly match the desktop GPS.
  Retroversion/inclination are mapped to local Y/X — verify visually.
- **No bone-implant contact detection** (green/grey indicator from desktop)
- **No CT visualization** — only 3D meshes
- **No glenosphere** — intentionally excluded (baseplate-only scope)
- **No humeral planning** — glenoid side only
- **HTTP only** (no HTTPS yet) — clipboard uses fallback, no encryption
- **Planning key validation** — some `planningKey` mappings are guessed and
  need validation with real case data (Standard, 10 Sup Aug, Extended, Post Sup)
- **Single-file frontend** — may need splitting if complexity grows

---

## Roadmap

### Short term
- [ ] Validate remaining planningKey mappings with real cases
- [ ] Add HTTPS via Let's Encrypt / certbot
- [ ] Implant selection cards with real product photos
- [ ] Improve scenarios evaluation system

### Medium term
- [ ] Pre-op measurement computation from landmarks (retroversion,
      inclination, subluxation)
- [ ] Bone-implant contact indicator
- [ ] PDF report export (plan summary with screenshots)
- [ ] Multiple case comparison view

### Long term
- [ ] User accounts (optional, for case management)
- [ ] Anatomic shoulder planning (not just reverse)
- [ ] CT slice visualization
- [x] Mobile-responsive layout (iteration 4)

---

## Connection with the gps-to-obj skill

The `gps-to-obj` skill at `/Users/brunogobbato/.codex/skills/gps-to-obj/`
is the **offline predecessor** of this web app. It:
- Decodes proprietary `.bin` → standard `.obj`
- Positions the baseplate via the matrix in `.ini`
- Generates combined OBJ files (scapula + blue baseplate with MTL)

The web app uses the SAME binary format knowledge and transformation math,
but runs entirely in the browser and adds editing/sharing/persistence.

```
Desktop GPS case  ──►  skill gps-to-obj  ──►  .obj + .ini (offline viewing)
       │
       └──────────►  GPS Web Planner  ──►  modified .ini (re-import to desktop)
                     (online editing + sharing)
```
