#!/usr/bin/env python3
"""Generate a 2-page PDF guide for GPS Web Planner."""
from fpdf import FPDF

# Advita brand colors
DARK_PETROL = (0, 72, 88)       # #004858
GREEN = (56, 176, 72)           # #38B048
TEAL = (16, 168, 152)           # #10A898
LIGHT_BG = (244, 247, 246)      # #f4f7f6
WHITE = (255, 255, 255)
TEXT = (26, 46, 46)             # #1a2e2e
MUTED = (86, 112, 112)         # #567070

class GuidePDF(FPDF):
    def header(self):
        # Thin top accent bar
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 3, 'F')

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*MUTED)
        self.cell(0, 10, f'GPS Web Planner Guide  |  Page {self.page_no()}/2  |  Created by Dr. Bruno Gobbato', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*DARK_PETROL)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        # Underline
        self.set_draw_color(*GREEN)
        self.set_line_width(0.5)
        y = self.get_y()
        self.line(self.l_margin, y, self.l_margin + 60, y)
        self.ln(3)

    def body_text(self, text):
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*TEXT)
        self.multi_cell(0, 4.2, text)
        self.ln(1)

    def bullet(self, text, bold_prefix=None):
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*TEXT)
        if bold_prefix:
            full = '  -  ' + bold_prefix + text
        else:
            full = '  -  ' + text
        self.multi_cell(0, 4.2, full)
        self.ln(0.3)

    def path_box(self, label, path):
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*DARK_PETROL)
        self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_fill_color(235, 240, 238)
        self.set_font('Courier', '', 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f'  {path}', fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def feature_item(self, icon, title, desc):
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*DARK_PETROL)
        self.cell(5, 4.5, icon)
        self.cell(0, 4.5, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(self.l_margin + 5)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*TEXT)
        self.multi_cell(0, 3.8, desc)
        self.ln(1)

pdf = GuidePDF('P', 'mm', 'A4')
pdf.set_auto_page_break(auto=False)
pdf.set_margins(15, 10, 15)

# ============ PAGE 1 ============
pdf.add_page()

# Title block
pdf.set_fill_color(*DARK_PETROL)
pdf.rect(0, 3, 210, 28, 'F')
pdf.set_y(8)
pdf.set_font('Helvetica', 'B', 22)
pdf.set_text_color(*WHITE)
pdf.cell(0, 10, 'GPS Web Planner', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(*GREEN)
pdf.cell(0, 6, 'Quick Start Guide', align='C', new_x="LMARGIN", new_y="NEXT")

pdf.ln(8)

# Intro
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(*TEXT)
pdf.multi_cell(0, 4.5,
    'The GPS Web Planner is an experimental web application that allows surgeons to review, '
    'modify, and share reverse shoulder arthroplasty planning created with the Equinoxe Planning '
    'App (EPA) - directly in a web browser, without needing the desktop software installed.')
pdf.ln(1)
pdf.set_font('Helvetica', 'BI', 8)
pdf.set_text_color(*MUTED)
pdf.multi_cell(0, 4,
    'Note: This is a test/prototype project. It is not an official Advita Ortho product. '
    'Always verify your final plan in the official Equinoxe Planning App before surgery.')
pdf.ln(4)

# --- IMPORTING A CASE ---
pdf.section_title('1. Importing a case')

pdf.body_text(
    'The Equinoxe Planning App stores case data locally on your computer. '
    'To import a case into the GPS Web Planner, you need to locate the case folder:')

pdf.path_box('macOS:', '/Users/<username>/Library/Application Support/Blue-Ortho/Blue-Ortho-Shoulder')
pdf.path_box('Windows:', r'C:\Users\<username>\AppData\Local\Blue-Ortho\Blue-Ortho-Shoulder\Data')

pdf.body_text(
    'Inside this folder you will find one subfolder per patient case, named with the case ID '
    'and a timestamp (e.g. PatientName_2026-03-21-141720/).')

pdf.set_font('Helvetica', 'B', 8.5)
pdf.set_text_color(*DARK_PETROL)
pdf.cell(0, 5, 'How to import:', new_x="LMARGIN", new_y="NEXT")
pdf.bullet('Click the "Import Case Folder" button in the top bar.')
pdf.bullet('Navigate to the Blue-Ortho folder and select the patient case folder.')
pdf.bullet('The app reads the scapula mesh, anatomical landmarks, and planning data automatically.')
pdf.ln(2)

# --- TWO PLANNING WORKFLOWS ---
pdf.section_title('2. Supported planning workflows')

pdf.body_text(
    'The Equinoxe Planning App offers two different workflows, and the GPS Web Planner supports both:')

pdf.set_font('Helvetica', 'B', 8.5)
pdf.set_text_color(*DARK_PETROL)
pdf.cell(0, 5, 'Standard Planning (EPA only)', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 8.5)
pdf.set_text_color(*TEXT)
pdf.multi_cell(0, 4, 'The surgeon uses the desktop app to segment the scapula and place the implant. '
    'The case folder contains 01-segmentation/ and 02-planning/ subfolders. '
    'The baseplate loads at the exact position from the desktop plan.')
pdf.ln(2)

pdf.set_font('Helvetica', 'B', 8.5)
pdf.set_text_color(*DARK_PETROL)
pdf.cell(0, 5, 'GPS-Guided Planning (with intraoperative navigation)', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 8.5)
pdf.set_text_color(*TEXT)
pdf.multi_cell(0, 4, 'The case is planned with GPS guidance. The folder may only contain '
    '05-autoSegmentation/ with auto-detected landmarks but no implant placement yet. '
    'The app will automatically place a Standard baseplate centered on the glenoid face, '
    'giving you a starting point to begin planning.')
pdf.ln(2)

# --- 3D VIEWER ---
pdf.section_title('3. 3D Viewer')
pdf.body_text(
    'Once imported, the scapula and baseplate are displayed in 3D. '
    'Drag to rotate, scroll to zoom, right-click to pan. '
    'Three preset views are available: Anterior, Glenoid (face-on), and Lateral.')
pdf.ln(0.5)

pdf.bullet('Toggle baseplate visibility to inspect the glenoid surface.', 'Show/Hide Implant: ')
pdf.bullet('Make the scapula semi-transparent to see the baseplate through the bone.', 'Transparent Bone: ')
pdf.bullet('If available, toggle between the original scapula (with osteophytes) and the cleaned version.', 'Remove Osteophytes: ')


# ============ PAGE 2 ============
pdf.add_page()
pdf.set_y(12)

# --- IMPLANT SELECTION ---
pdf.section_title('4. Implant selection')
pdf.body_text(
    'Five baseplate types are available in the left sidebar: Standard, 8deg Post Aug, '
    '10deg Sup Aug, Extended, and Post Sup. Click any card to switch the implant type. '
    'The correct LEFT or RIGHT variant is selected automatically based on the patient side.')
pdf.ln(1)

# --- POSITION CONTROLS ---
pdf.section_title('5. Implant position controls')
pdf.body_text(
    'Fine-tune the baseplate position using the controls in the right sidebar:')

pdf.bullet('Retroversion (Left Right): +/- 1deg per click', 'Retroversion: ')
pdf.bullet('Inferior Inclination (Down Up): +/- 1deg per click', 'Inclination: ')
pdf.bullet('Depth (- / +): move deeper or shallower by 1mm', 'Depth: ')
pdf.bullet('SI Translation (Up Down): shift superior/inferior by 1mm', 'SI Translation: ')
pdf.bullet('AP Translation (Left Right): shift anterior/posterior by 1mm', 'AP Translation: ')
pdf.bullet('Axial Rotation (Rot): rotate around the central axis by 1deg', 'Axial Rotation: ')
pdf.bullet('Reset: return to the original imported position.', 'Reset: ')
pdf.ln(2)

# --- SCENARIOS ---
pdf.section_title('6. Saving scenarios')
pdf.body_text(
    'You can save up to three different planning scenarios for each case, '
    'allowing you to compare different implant positions, types, or strategies.')

pdf.set_font('Helvetica', 'B', 8.5)
pdf.set_text_color(*DARK_PETROL)
pdf.cell(0, 5, 'How to save:', new_x="LMARGIN", new_y="NEXT")
pdf.bullet('Adjust the implant position and/or type as desired.')
pdf.bullet('Click "Save Current Scenario" in the left sidebar.')
pdf.bullet('The scenario is saved to the first available slot (1, 2, or 3).')
pdf.bullet('Click any filled slot to reload that scenario.')
pdf.ln(1)
pdf.set_font('Helvetica', '', 8.5)
pdf.set_text_color(*TEXT)
pdf.multi_cell(0, 4, 'Each scenario stores the implant type and all position adjustments. '
    'Scenarios are saved on the server and persist across sessions.')
pdf.ln(2)

# --- SHARING ---
pdf.section_title('7. Sharing with colleagues')
pdf.body_text(
    'Click the "Share (link)" button in the top bar to open the sharing dialog. '
    'Two options are available:')

pdf.bullet('Copies a link allowing the recipient to view, modify, save scenarios, and comment.', 'EDIT - ')
pdf.bullet('Copies a link for viewing only - no modifications allowed.', 'VIEW-ONLY - ')

pdf.ln(1)
pdf.body_text(
    'The link is automatically copied to your clipboard. Paste it in an email or message to share.')
pdf.ln(1)

# --- COMMENTS ---
pdf.section_title('8. Comments')
pdf.body_text(
    'A comments section is available in the right sidebar. Any user who opens the case '
    '- whether in edit or view-only mode - can leave comments. Each comment is attributed '
    'to the author\'s name. This enables asynchronous collaboration: a colleague can review '
    'your planning, leave feedback, and you can review it later.')
pdf.ln(2)

# --- EXPORT ---
pdf.section_title('9. Exporting the modified plan')
pdf.body_text(
    'After adjusting the implant, click "Export .ini" to download a modified reverse.ini file '
    'compatible with the Equinoxe Planning App. This file contains the updated implant '
    'transformation matrix and can be re-imported into the desktop software.')
pdf.ln(2)

# --- WORKFLOW BOX ---
pdf.set_fill_color(235, 243, 241)
pdf.set_draw_color(*TEAL)
pdf.set_line_width(0.4)
y = pdf.get_y()
pdf.rect(pdf.l_margin, y, 180, 32, 'DF')
pdf.set_xy(pdf.l_margin + 4, y + 2)
pdf.set_font('Helvetica', 'B', 9)
pdf.set_text_color(*DARK_PETROL)
pdf.cell(0, 5, 'Typical workflow', new_x="LMARGIN", new_y="NEXT")
pdf.set_x(pdf.l_margin + 4)
pdf.set_font('Courier', '', 8)
pdf.set_text_color(*TEXT)
workflow = (
    '1. Plan the case in Equinoxe Planning App (desktop)\n'
    '2. Locate the case folder on your computer\n'
    '3. Import the folder into GPS Web Planner (browser)\n'
    '4. Review and adjust the implant position\n'
    '5. Save up to 3 scenarios for comparison\n'
    '6. Share the link with colleagues (EDIT or VIEW-ONLY)\n'
    '7. Colleagues view, comment, and optionally modify\n'
    '8. Export the final .ini and re-import into desktop app'
)
pdf.multi_cell(172, 3.2, workflow)

# Bottom credits
pdf.set_y(-20)
pdf.set_font('Helvetica', 'I', 7.5)
pdf.set_text_color(*MUTED)
pdf.cell(0, 4, 'Inspired by Advita Ortho / Blueortho Equinoxe Planning App', align='C', new_x="LMARGIN", new_y="NEXT")

# Save
out = '/Users/brunogobbato/Dropbox/3D/Exactech/gps-web-planner/GPS_Web_Planner_Guide.pdf'
pdf.output(out)
print(f'PDF saved: {out}')
