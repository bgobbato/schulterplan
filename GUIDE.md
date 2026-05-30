# GPS Web Planner — User Guide

## What is this?

The **GPS Web Planner** is an experimental web application that allows surgeons to review, modify, and share reverse shoulder arthroplasty planning created with the **Equinoxe Planning App (EPA)** — directly in a web browser, without needing the desktop software installed.

> **Note:** This is a test/prototype project. It is not an official Advita Ortho product. Use it for educational and collaborative purposes only — always verify your final planning in the official Equinoxe Planning App before surgery.

---

## Getting started

### Step 1: Locate your case folder

The Equinoxe Planning App stores all case data in a local folder on your computer. The location depends on your operating system:

**macOS:**
```
/Users/<your-username>/Library/Application Support/Blue-Ortho/Blue-Ortho-Shoulder
```

**Windows:**
```
C:\Users\<your-username>\AppData\Local\Blue-Ortho\Blue-Ortho-Shoulder\Data
```

Inside this folder you will find one subfolder for each patient case, named with the case ID and a timestamp. For example:

```
PatientName_2026-03-21-141720/
```

### Step 2: Import a case

1. Open the GPS Web Planner in your browser.
2. Click the **"Import Case Folder"** button in the top bar.
3. A file picker dialog will appear — navigate to the Blue-Ortho folder described above.
4. **Select the patient case folder** (e.g. `PatientName_2026-03-21-141720/`) and confirm.

The app will automatically read the scapula mesh, anatomical landmarks, and planning data from the folder.

### What kind of cases can I import?

The Equinoxe Planning App offers two different workflows for planning a case:

- **Standard Planning (EPA only):** The surgeon uses the desktop app to segment the scapula and place the implant manually. The case folder will contain `01-segmentation/` and `02-planning/` subfolders with the full planning data.

- **GPS-Guided Planning (with intraoperative navigation):** The case is planned with GPS guidance in mind. The folder may contain an `05-autoSegmentation/` subfolder with automatically detected landmarks, but may not yet have a `02-planning/` folder if the implant has not been positioned yet.

**The GPS Web Planner supports both workflows.** If the case includes a completed plan (`02-planning/reverse.ini`), the baseplate will be loaded at the exact position defined in the desktop software. If no plan exists yet (GPS-only cases with `05-autoSegmentation/`), the app will automatically place a Standard baseplate centered on the glenoid face based on the anatomical landmarks — giving you a starting point to begin planning.

---

## Features

### 3D Viewer

Once a case is imported, you will see the patient's scapula in 3D with the baseplate positioned on the glenoid. You can:

- **Rotate** the view by clicking and dragging.
- **Zoom** with the scroll wheel.
- **Pan** by right-clicking and dragging.

Three **preset views** are available in the top bar:
- **Anterior** — view from the front of the patient.
- **Glenoid** — view looking straight at the glenoid face (default).
- **Lateral** — view from the side.

### Show / Hide Implant

Toggle the baseplate visibility on and off to see the glenoid surface underneath.

### Transparent Bone

Make the scapula semi-transparent (50% opacity) so you can see how the baseplate sits relative to the bone from any angle.

### Osteophyte visualization

If the case includes a scapula model with osteophytes removed (from the `03-osteophyte/` folder), a **"Remove Osteophytes"** button will appear. This lets you toggle between:
- The **original scapula** (with osteophytes) — showing the real anatomy.
- The **cleaned scapula** (osteophytes removed) — showing the planned surgical surface.

This is the same toggle available in the desktop Equinoxe Planning App.

---

### Implant selection

Five baseplate types are available in the left sidebar:
- **Standard**
- **8° Post Aug** (posterior augmented)
- **10° Sup Aug** (superior augmented)
- **Extended**
- **Post Sup** (posterior-superior augmented)

Click on any card to switch the baseplate type. The correct LEFT or RIGHT variant is selected automatically based on the case side.

---

### Implant position controls

The right sidebar provides fine controls to adjust the baseplate position:

**Rotation:**
- **Retroversion** (← →): adjust by 1° per click.
- **Inferior Inclination** (↓ ↑): adjust by 1° per click.

**Depth:**
- **Depth** (− / +): move the baseplate deeper into or further out of the bone by 1mm per click.

**Translation:**
- **SI** (↑ ↓): shift the baseplate superior or inferior by 1mm.
- **AP** (← →): shift anterior or posterior by 1mm.
- **Axial Rotation** (↻): rotate around the baseplate central axis by 1°.

**Reset:** Click the **Reset** button to return to the original imported position.

---

### Saving scenarios

You can save up to **three different planning scenarios** for each case. This allows you to compare different implant positions, types, or strategies side by side.

**To save a scenario:**
1. Adjust the implant position and/or type as desired.
2. Click the **"Save Current Scenario"** button in the left sidebar.
3. The scenario will be saved to the first available slot (Scenario 1, 2, or 3).

**To load a saved scenario:**
- Click on any filled scenario slot to restore that configuration.

Each scenario stores the implant type and all position adjustments. Scenarios are synchronized with the server, so they persist across sessions and are visible to anyone with the case link.

---

### Sharing with colleagues

You can share your planning with colleagues by sending them a link. Click the **"Share (link)"** button in the top bar to open the sharing dialog.

Two options are available:

- **EDIT** — Copies a link that allows the recipient to view the case, modify the implant position, save new scenarios, and add comments. Use this when you want a colleague to actively collaborate on the planning.

- **VIEW-ONLY** — Copies a link that allows the recipient to view the 3D model and all saved scenarios, but without the ability to make changes. Use this when you want to show your planning without allowing modifications.

The link is automatically copied to your clipboard. Simply paste it in an email, message, or chat to share it.

---

### Comments

A **comments section** is available in the right sidebar below the implant controls. Any user who opens the case — whether in edit or view-only mode — can leave comments.

- Type your comment in the text box and press **Post**.
- Each comment is attributed to the author's name (you will be prompted to enter your name the first time you interact with the app).
- Comments are visible to everyone who has the case link.

This is useful for asynchronous collaboration: a colleague can review your planning, leave feedback in the comments, and you can review it later.

---

### Exporting the modified plan

After adjusting the implant position, you can export the modified planning as a `.ini` file compatible with the Equinoxe Planning App:

1. Click the **"Export .ini"** button in the left sidebar.
2. A file named `<caseId>_modified.ini` will be downloaded.
3. This file contains the updated implant transformation matrix and can be imported back into the desktop software.

---

## Workflow summary

```
1. Open a case in the Equinoxe Planning App (desktop)
         ↓
2. Locate the case folder on your computer
         ↓
3. Import the folder into GPS Web Planner (browser)
         ↓
4. Review and adjust the implant position
         ↓
5. Save up to 3 scenarios for comparison
         ↓
6. Share the link with colleagues (EDIT or VIEW-ONLY)
         ↓
7. Colleagues view, comment, and optionally modify
         ↓
8. Export the final .ini and re-import into the desktop app
```

---

## Important notes

- **This is a test project** and is not intended to replace the official Equinoxe Planning App. Always verify your final surgical plan in the official software.
- The app works entirely in the browser — no installation is required.
- Case data is stored on the server only when you click **"Save to Server"**. Local imports stay in your browser session until saved.
- The 3D models shown are the same meshes generated by the Equinoxe Planning App — they are not modified or simplified.
- Only the **scapula** and **baseplate** are displayed. The humerus, glenosphere, and other components are not included in this version.

---

## System requirements

- A modern web browser (Chrome, Firefox, Safari, or Edge).
- An internet connection (to access the web app and share cases).
- Access to the Equinoxe Planning App case folders on your computer.

---

*GPS Web Planner — Created by Dr. Bruno Gobbato*
*Inspired by Advita Ortho / Blueortho Equinoxe Planning App*
