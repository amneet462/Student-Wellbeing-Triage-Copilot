import sys
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(50, 752, "Student Wellbeing & Triage Copilot — 4-Day Implementation Plan")
            self.drawRightString(562, 752, "Day-by-Day Work Division (Person 1 · Person 2 · Person 3)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(50, 746, 562, 746)
        
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(50, 42, 562, 42)
        
        footer_text = "CONFIDENTIAL — Sprint Plan for Person 1, Person 2, and Person 3"
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(50, 30, footer_text)
        self.drawRightString(562, 30, page_str)
        self.restoreState()

def create_implementation_plan_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Palette
    c_primary = colors.HexColor("#1E3A8A")    # Deep Navy
    c_secondary = colors.HexColor("#0D9488")  # Calming Teal
    c_dark = colors.HexColor("#0F172A")       # Slate 900
    c_body = colors.HexColor("#334155")       # Slate 700
    c_light = colors.HexColor("#F8FAFC")      # Slate 50
    c_border = colors.HexColor("#CBD5E1")     # Slate 300
    c_done = colors.HexColor("#15803D")       # Green 700
    c_todo = colors.HexColor("#B91C1C")       # Red 700

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_dark,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_body,
        spaceAfter=5
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_body
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Student Wellbeing & Triage Copilot", title_style))
    story.append(Paragraph("4-Day Master Implementation Plan · Day-by-Day Work Division (3 People)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=8))

    meta_data = [
        [
            Paragraph("<b>Total Sprint:</b> 4 Working Days", body_style),
            Paragraph("<b>Team:</b> Person 1 · Person 2 · Person 3", body_style),
            Paragraph("<b>Stack:</b> FastAPI · ChromaDB · React · Gemini", body_style),
        ],
        [
            Paragraph("<b>Current Progress:</b> ~40% Done", body_style),
            Paragraph("<b>Completed Work:</b> 102/102 Tests Passing", body_style),
            Paragraph("<b>Core Goal:</b> Relieve Counseling Backlogs", body_style),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[165, 175, 172])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # High-level Role Summary
    story.append(Paragraph("Team Role Overview", h1_style))
    role_summary_data = [
        [Paragraph("Developer", table_header), Paragraph("Core Responsibilities", table_header), Paragraph("Current Status", table_header)],
        [
            Paragraph("<b>Person 1</b>", table_cell_bold),
            Paragraph("<b>AI Safety, Triage & APIs:</b> Distress & self-harm detection, zero-LLM emergency bypass, issue categorization, and backend integration routes.", table_cell),
            Paragraph("<font color='#15803D'><b>~85% COMPLETED</b><br/>(102/102 Tests Passing)</font>", table_cell)
        ],
        [
            Paragraph("<b>Person 2</b>", table_cell_bold),
            Paragraph("<b>RAG & AI Assistant:</b> Collecting university policies & CBT exercises, ChromaDB vector database setup, and citation-backed chatbot.", table_cell),
            Paragraph("<font color='#B91C1C'><b>TO DO (Day 1 - 4)</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 3</b>", table_cell_bold),
            Paragraph("<b>Portal, Agents & Integration:</b> React frontend dashboard, emergency button, syllabus task scheduler, and professor extension email drafter.", table_cell),
            Paragraph("<font color='#B91C1C'><b>TO DO (Day 1 - 4)</b></font>", table_cell)
        ],
    ]
    t_roles = Table(role_summary_data, colWidths=[80, 312, 120])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_roles)
    story.append(Spacer(1, 10))

    # DAY 1
    story.append(Paragraph("DAY 1: Setup, Data Gathering & Basic Frontend Layout", h1_style))
    d1_data = [
        [Paragraph("Person", table_header), Paragraph("Tasks to Complete (Day 1)", table_header), Paragraph("Status", table_header)],
        [
            Paragraph("<b>Person 1</b><br/>Safety & Triage", table_cell_bold),
            Paragraph(
                "• [DONE] Build regex acute distress & self-harm detection engine<br/>"
                "• [DONE] Build rule-based safety state machine with session locks<br/>"
                "• [DONE] Implement emergency bypass: 0 LLM calls for crisis text<br/>"
                "• [DONE] Build emergency contacts loader (999, 988, Samaritans)<br/>"
                "• [DONE] Build query classifier (academic, emotional, financial, admin)<br/>"
                "• [DONE] Build backend API endpoints (102 tests passing)<br/>"
                "• Add real campus clinic phone numbers to emergency JSON config<br/>"
                "• Add mock endpoints so Person 2 and Person 3 can test without blockers",
                table_cell
            ),
            Paragraph("<font color='#15803D'><b>Core Done</b></font><br/>Minor config left", table_cell)
        ],
        [
            Paragraph("<b>Person 2</b><br/>RAG Assistant", table_cell_bold),
            Paragraph(
                "• Collect 5 university policy documents (extensions, mitigating circumstances, drop deadlines, hardship funds, accommodations)<br/>"
                "• Collect 5 mental wellness & CBT resources (5-4-3-2-1 grounding, box breathing, sleep hygiene, exam anxiety)<br/>"
                "• Install ChromaDB (or FAISS)<br/>"
                "• Initialize two separate vector stores: (1) Policies and (2) Wellness",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 1 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 3</b><br/>Portal & UI", table_cell_bold),
            Paragraph(
                "• Create the React + Vite frontend project with Tailwind CSS<br/>"
                "• Build the main page layout with tabs: (1) Chat, (2) Workload Planner, (3) Campus Resources<br/>"
                "• Add top emergency button: 'In Crisis? Get 24/7 Immediate Help'<br/>"
                "• Build a popup modal that displays emergency phone numbers when clicked",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 1 Work</b></font>", table_cell)
        ],
    ]
    t_d1 = Table(d1_data, colWidths=[90, 332, 90])
    t_d1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_d1)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # DAY 2
    story.append(Paragraph("DAY 2: Core AI, Chatbot & Syllabus Upload", h1_style))
    d2_data = [
        [Paragraph("Person", table_header), Paragraph("Tasks to Complete (Day 2)", table_header), Paragraph("Status", table_header)],
        [
            Paragraph("<b>Person 1</b><br/>Safety & Triage", table_cell_bold),
            Paragraph(
                "• Build a safety gatekeeper: screen all incoming chat messages with the safety engine before passing them to Person 2's AI<br/>"
                "• Ensure high-risk messages immediately stop the AI and return crisis contacts<br/>"
                "• Add an audit log to record timestamps whenever crisis bypass is triggered (with personal text redacted)",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 2 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 2</b><br/>RAG Assistant", table_cell_bold),
            Paragraph(
                "• Split policy and wellness documents into small text chunks<br/>"
                "• Generate embeddings and save them into the two ChromaDB databases<br/>"
                "• Connect ChromaDB to Google Gemini (or OpenAI) to build the RAG chatbot<br/>"
                "• Instruct the AI via prompt to <b>always cite exact document names and section numbers</b><br/>"
                "• Create the backend chat endpoint (<code>/api/assistant/chat</code>)",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 2 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 3</b><br/>Portal & UI", table_cell_bold),
            Paragraph(
                "• Build the chat screen in React with user/assistant message bubbles<br/>"
                "• Add source citation badges (e.g., <code>[Source: Policy §4.2]</code>) under assistant replies<br/>"
                "• Add emergency lock: if a message is a crisis, lock chat and display emergency phone cards<br/>"
                "• Build a syllabus upload box supporting PDF drag-and-drop and text paste<br/>"
                "• Create the backend endpoint (<code>/api/agent/parse-syllabus</code>) to extract assignments and dates",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 2 Work</b></font>", table_cell)
        ],
    ]
    t_d2 = Table(d2_data, colWidths=[90, 332, 90])
    t_d2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_d2)
    story.append(Spacer(1, 10))

    # DAY 3
    story.append(Paragraph("DAY 3: Tasks, Email Drafter & Campus Directory", h1_style))
    d3_data = [
        [Paragraph("Person", table_header), Paragraph("Tasks to Complete (Day 3)", table_header), Paragraph("Status", table_header)],
        [
            Paragraph("<b>Person 1</b><br/>Safety & Triage", table_cell_bold),
            Paragraph(
                "• Create the campus directory backend endpoint (<code>/api/resources/campus</code>)<br/>"
                "• Add contact details for Financial Aid, Housing, and Disability Support<br/>"
                "• Add rate limiting and basic error handling so the server never crashes on bad input",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 3 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 2</b><br/>RAG Assistant", table_cell_bold),
            Paragraph(
                "• Build interactive CBT exercise endpoints (4-7-8 breathing timer, 5-4-3-2-1 grounding guide)<br/>"
                "• Add fallback check: if document similarity score is too low, tell student to contact a human advisor<br/>"
                "• Test chatbot against 15 real university questions to make sure citations are accurate",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 3 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 3</b><br/>Portal & UI", table_cell_bold),
            Paragraph(
                "• Build the task scheduler: break big syllabus deadlines into daily 30-minute checklist items (Today / This Week / Next Week)<br/>"
                "• Add interactive checkboxes so students can tick off completed study tasks<br/>"
                "• Build the 'Draft Extension Email' button: generates a polite, formal email to the professor citing university policy with 1-click copy<br/>"
                "• Build the Campus Resource Directory page showing cards for Financial Aid, Housing, and Disability Support",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 3 Work</b></font>", table_cell)
        ],
    ]
    t_d3 = Table(d3_data, colWidths=[90, 332, 90])
    t_d3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_d3)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # DAY 4
    story.append(Paragraph("DAY 4: Testing, Hardening & Live Demo Preparation", h1_style))
    d4_data = [
        [Paragraph("Person", table_header), Paragraph("Tasks to Complete (Day 4)", table_header), Paragraph("Status", table_header)],
        [
            Paragraph("<b>Person 1</b><br/>Safety & Triage", table_cell_bold),
            Paragraph(
                "• Test the safety engine against tricky messages, slang, and jailbreak attempts to ensure the AI never leaks during a crisis<br/>"
                "• Run the full test suite (<code>pytest</code>) and verify everything passes with 0 errors<br/>"
                "• Document safety verification results for the presentation",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 4 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 2</b><br/>RAG Assistant", table_cell_bold),
            Paragraph(
                "• Check response speed: ensure chatbot replies in under 2.5 seconds<br/>"
                "• Pick and prepare 3 best demo questions with clear, verified citations (e.g. extenuating circumstances rule, exam panic grounding)<br/>"
                "• Prepare a simple diagram showing how the two knowledge bases work for the presentation",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 4 Work</b></font>", table_cell)
        ],
        [
            Paragraph("<b>Person 3</b><br/>Portal & UI", table_cell_bold),
            Paragraph(
                "• Polish frontend styling, animations, loading spinners, and error alerts<br/>"
                "• Connect all frontend buttons and forms to live backend APIs<br/>"
                "• Record a 2-minute backup demo video (as safety against live Wi-Fi/projector issues)<br/>"
                "• Rehearse the live walkthrough with Person 1 and Person 2:<br/>"
                "  1. Triggering an emergency bypass (showing safety works)<br/>"
                "  2. Asking a policy question (showing citation works)<br/>"
                "  3. Uploading a syllabus (showing task breakdown and extension email drafter work)",
                table_cell
            ),
            Paragraph("<font color='#B91C1C'><b>Day 4 Work</b></font>", table_cell)
        ],
    ]
    t_d4 = Table(d4_data, colWidths=[90, 332, 90])
    t_d4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_d4)
    story.append(Spacer(1, 10))

    # Golden Rules
    story.append(Paragraph("Golden Team Rules", h1_style))
    rules_text = """
1. <b>Zero-AI in Crisis:</b> If Person 1's safety check flags a crisis, Person 2's AI <b>must never run</b>. Only static verified emergency phone numbers are returned.<br/>
2. <b>Citations Required:</b> Person 2's chatbot must always cite real policy documents (e.g. <i>[Source: Policy Handbook §3.1]</i>). It must never invent rules.<br/>
3. <b>Clear Daily Sync:</b> At the start of each day, spend 5 minutes reviewing this checklist so no one is blocked.
    """
    story.append(Paragraph(rules_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Implementation Plan PDF successfully created at: {output_path}")

if __name__ == "__main__":
    out_file = r"D:\Student-Wellbeing-Triage-Copilot\Student_Wellbeing_Triage_Copilot_Implementation_Plan.pdf"
    create_implementation_plan_pdf(out_file)
