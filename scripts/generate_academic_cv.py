#!/usr/bin/env python3

from pathlib import Path
import shutil

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "adam-swietek-academic-cv.pdf"
WEBSITE_COPY = ROOT / "static" / "cv.pdf"

BASKERVILLE_COLLECTION = Path("/System/Library/Fonts/Supplemental/Baskerville.ttc")
BASKERVILLE_REGULAR = "Baskerville"
BASKERVILLE_SEMIBOLD = "Baskerville-Semibold"

if not BASKERVILLE_COLLECTION.exists():
    raise FileNotFoundError(
        "Baskerville is required to generate the CV but was not found at "
        f"{BASKERVILLE_COLLECTION}"
    )

pdfmetrics.registerFont(TTFont(BASKERVILLE_REGULAR, BASKERVILLE_COLLECTION, subfontIndex=0))
pdfmetrics.registerFont(TTFont(BASKERVILLE_SEMIBOLD, BASKERVILLE_COLLECTION, subfontIndex=4))
pdfmetrics.registerFont(TTFont("Baskerville-Italic", BASKERVILLE_COLLECTION, subfontIndex=2))
pdfmetrics.registerFont(TTFont("Baskerville-SemiboldItalic", BASKERVILLE_COLLECTION, subfontIndex=5))
pdfmetrics.registerFontFamily(
    BASKERVILLE_REGULAR,
    normal=BASKERVILLE_REGULAR,
    bold=BASKERVILLE_SEMIBOLD,
    italic="Baskerville-Italic",
    boldItalic="Baskerville-SemiboldItalic",
)

NAVY = colors.HexColor("#17324D")
MID = colors.HexColor("#566575")
LIGHT = colors.HexColor("#D9E1E8")
TEXT = colors.HexColor("#17212B")


class CVDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="cv", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.49 * inch, letter[0] - doc.rightMargin, 0.49 * inch)
        canvas.setFont(BASKERVILLE_REGULAR, 8)
        canvas.setFillColor(MID)
        canvas.drawString(doc.leftMargin, 0.32 * inch, "Adam R. Swietek")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.32 * inch, str(doc.page))
        canvas.restoreState()


styles = getSampleStyleSheet()

name_style = ParagraphStyle(
    "Name",
    parent=styles["Normal"],
    fontName=BASKERVILLE_SEMIBOLD,
    fontSize=22,
    leading=25,
    textColor=NAVY,
    spaceAfter=2,
)

role_style = ParagraphStyle(
    "Role",
    parent=styles["Normal"],
    fontName=BASKERVILLE_REGULAR,
    fontSize=10.5,
    leading=14,
    textColor=TEXT,
    spaceAfter=3,
)

contact_style = ParagraphStyle(
    "Contact",
    parent=styles["Normal"],
    fontName=BASKERVILLE_REGULAR,
    fontSize=8.7,
    leading=12,
    textColor=MID,
    spaceAfter=12,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName=BASKERVILLE_SEMIBOLD,
    fontSize=10.2,
    leading=12,
    textColor=NAVY,
    spaceBefore=9,
    spaceAfter=4,
    borderWidth=0,
    borderPadding=0,
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName=BASKERVILLE_REGULAR,
    fontSize=8.7,
    leading=11.3,
    textColor=TEXT,
    spaceAfter=2.5,
)

small_style = ParagraphStyle(
    "Small",
    parent=body_style,
    fontSize=8.1,
    leading=10.5,
    textColor=MID,
)

date_style = ParagraphStyle(
    "Date",
    parent=body_style,
    fontName=BASKERVILLE_SEMIBOLD,
    fontSize=8.2,
    leading=11,
    textColor=NAVY,
    alignment=TA_RIGHT,
)

entry_style = ParagraphStyle(
    "Entry",
    parent=body_style,
    leftIndent=0,
    firstLineIndent=0,
)

publication_style = ParagraphStyle(
    "Publication",
    parent=body_style,
    leftIndent=11,
    firstLineIndent=-11,
    spaceAfter=5,
)


def link(label, url):
    return f'<link href="{url}" color="#17324D"><u>{label}</u></link>'


def section(title):
    return KeepTogether([
        Spacer(1, 2),
        Paragraph(title.upper(), section_style),
        Table([[""]], colWidths=[7.02 * inch], rowHeights=[0.6], style=[
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]),
        Spacer(1, 3),
    ])


def dated_entry(date, title, details=None):
    content = f"<b>{title}</b>"
    if details:
        content += f"<br/>{details}"
    table = Table(
        [[Paragraph(date, date_style), Paragraph(content, entry_style)]],
        colWidths=[0.88 * inch, 6.08 * inch],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def bullet(text):
    return Paragraph(f"&#8226;&nbsp;&nbsp;{text}", body_style)


story = []

story.append(Paragraph("Adam Robert Swietek", name_style))
story.append(Paragraph(
    "Postdoctoral Scholar | Department of Urban Planning and Spatial Analysis<br/>"
    "USC Sol Price School of Public Policy | Urban Data Lab",
    role_style,
))
story.append(Paragraph(
    f'{link("swietek@usc.edu", "mailto:swietek@usc.edu")} &nbsp;&nbsp;|&nbsp;&nbsp; '
    f'{link("adamswietek.github.io", "https://adamswietek.github.io")} &nbsp;&nbsp;|&nbsp;&nbsp; '
    f'{link("Google Scholar", "https://scholar.google.com/citations?user=m64YRz0AAAAJ&hl=en")} &nbsp;&nbsp;|&nbsp;&nbsp; '
    f'{link("GitHub", "https://github.com/AdamSwietek")}',
    contact_style,
))

story.append(section("Academic appointment"))
story.append(dated_entry(
    "2025-present",
    "University of Southern California, Los Angeles",
    "Postdoctoral Scholar, Department of Urban Planning and Spatial Analysis, USC Price School; Urban Data Lab",
))

story.append(section("Education"))
story.append(dated_entry(
    "2024",
    "EPFL - PhD, Architecture and Sciences of the City",
    f'Thesis: {link("Spatial Modeling for Building Design Evaluation: From Visual Landscape Quality Assessment to Devaluation Risk Estimation", "https://infoscience.epfl.ch/entities/publication/4a3dffb6-a14f-4016-8f0f-352006c3660e")}<br/>'
    "Advisor: Philippe Thalmann. Committee: Marilyne Andersen, Alexandre Alahi, Lint Barrage, and Silvia Tobias. Nominated for EPFL Thesis Distinction.",
))
story.append(dated_entry(
    "2019",
    "Columbia University - MS, Real Estate Development and Finance",
))
story.append(dated_entry(
    "2013",
    "Georgia Institute of Technology - BS, Mechanical Engineering",
    "Minor in Energy Systems",
))

story.append(section("Research interests"))
story.append(Paragraph(
    "Environmental externalities in cities; urban, real estate, and environmental economics; spatial modeling and GeoAI; urban data science; building performance; computational design; climate adaptation and resilience.",
    body_style,
))

story.append(section("Publications and preprints"))
story.append(Paragraph(
    f'<b>Swietek, A. R.</b> (2026). "{link("Structure-to-Structure Connectivity and Urban Wildfire Destruction Risk in California", "https://doi.org/10.2139/ssrn.7590400")}." SSRN preprint.',
    publication_style,
))
story.append(Paragraph(
    f'<b>Swietek, A. R.</b> (2024). "{link("Automated Design Appraisal: Estimating Real Estate Price Growth and Value at Risk Due to Local Development", "https://doi.org/10.2139/ssrn.4670069")}." SSRN working paper.',
    publication_style,
))
story.append(Paragraph(
    f'<b>Swietek, A. R.</b>, &amp; Zumwald, M. (2023). "{link("Visual Capital: Evaluating Building-Level Visual Landscape Quality at Scale", "https://doi.org/10.1016/j.landurbplan.2023.104880")}." <i>Landscape and Urban Planning</i>, 240, 104880.',
    publication_style,
))
story.append(Paragraph(
    f'<b>Swietek, A. R.</b>, &amp; Schweizer, J. (2022). "{link("How View Determines Well-Being and Value", "https://www.wuestpartner.com/ch-en/2022/11/07/how-view-determines-well-being-andvalue/")}." Wuest Partner.',
    publication_style,
))

story.append(PageBreak())

story.append(section("Selected research in progress"))
story.append(bullet("<b>Urban Electrification:</b> AI-based analysis of electrical permits in Los Angeles."))
story.append(bullet("<b>Hidden Housing:</b> Detecting unpermitted dwelling units in Los Angeles."))
story.append(bullet("<b>Construction and Demolition Waste:</b> Analysis of Facebook Marketplace listings."))
story.append(bullet("<b>MeshCity:</b> A Python toolkit for loading and transforming USGS LiDAR point clouds."))
story.append(bullet("<b>Generative Design for Reducing Urban Fire Spread and Structure Loss.</b>"))
story.append(bullet("<b>Estimating Spatial Basis Risk to Hedge Extreme Temperatures with Prediction Markets.</b>"))
story.append(bullet("<b>Urban Geometry of Heat Island Intensity.</b>"))
story.append(bullet("<b>Openview:</b> Open-source visual-network and viewpoint-simulation tools for large-scale urban visibility analysis."))

story.append(section("Grants, fellowships, and innovation awards"))
story.append(dated_entry(
    "2023",
    link("AVIA - ENAC Innovation Seed Grant", "https://www.epfl.ch/schools/enac/avia/"),
    "Principal investigator; integrated data-driven impact assessment for early-stage architectural design optimization.",
))
story.append(dated_entry(
    "2022",
    link("EPFL Blaze Trailblazer - REON", "https://www.epfl.ch/innovation/startup/programs/blaze/2022-iii/"),
    "Co-founder; automated reuse assessment for building components and construction materials.",
))
story.append(dated_entry(
    "",
    link("Circular Economy Transition Incubator - REON", "https://www.cetransition.ch/de/kreislaufwirtschaft-inkubator"),
    "Selected for the nationwide incubator supporting circular-economy ventures.",
))
story.append(dated_entry(
    "2019-2024",
    link("Marie Sklodowska-Curie Fellowship - EU Horizon 2020", "https://www.epfl.ch/schools/enac/open-visual-capital-data/"),
    "European Union Horizon 2020 research and innovation programme, grant agreement No. 754354.",
))

story.append(section("Teaching"))
story.append(dated_entry(
    "",
    link("Economic Growth and Sustainability I (HUM-471)", "https://edu.epfl.ch/coursebook/en/economic-growth-and-sustainability-i-HUM-471"),
    "Teaching Assistant, EPFL Humanities and Social Sciences Program. Instructor: Philippe Thalmann.",
))
story.append(dated_entry(
    "",
    link("Economic Growth and Sustainability II (HUM-470)", "https://edu.epfl.ch/coursebook/en/economic-growth-and-sustainability-ii-HUM-470"),
    "Teaching Assistant, EPFL Humanities and Social Sciences Program. Instructor: Philippe Thalmann.",
))

story.append(section("Student supervision"))
story.append(dated_entry(
    "2024",
    "Esteban Requena - Master's thesis",
    '"Identifying Geographical Clusters of High or Low Sustainability Ratings and Their Implications."',
))
story.append(dated_entry(
    "2023",
    "Yannick Neypatraiky - Master's thesis, EPFL Civil Engineering",
    f'{link("Data-Driven Assessment of the Swiss Building Stock: Characterising Building Typologies for Energy Retrofit Prioritisation", "https://infoscience.epfl.ch/entities/publication/a51a82b4-fc7a-443a-a15e-d49177214c43")}.',
))
story.append(dated_entry(
    "2022",
    "Paul Habert, Yannick Neypatraiky, and Thomas Rimbot - Machine Learning course project",
    '"Best Place for You to Live."',
))

story.append(section("Selected presentations and talks"))
story.append(dated_entry(
    "2026",
    '"Openview: A Tool for Mesh-Based Urban Visibility Modeling and Analysis"',
    f'{link("2026 AAG Annual Meeting", "https://aag-meetings.secure-platform.com/aag2026")}, San Francisco, California, March 17-21.',
))
story.append(dated_entry(
    "2024",
    link("Spatial Modeling in Building Design Evaluation", "https://www.wsl.ch/en/events-and-courses/spatial-modeling-in-building-design-evaluation/"),
    "WSL Landscape Centre Seminar Series, July 2.",
))
story.append(dated_entry(
    "2023",
    link("Spatial Statistics 2023: Climate and the Environment", "https://www.statsoc.org.au/event-4837057"),
    "University of Colorado Boulder, July 18-21.",
))
story.append(dated_entry(
    "2023",
    '"Visual Capital: Large-Scale Assessment of Building-Level Visual Landscape Quality"',
    f'EPFL EDAR Doc.Days, April 17. {link("Program", "https://memento.epfl.ch/public/upload/files/DocdaysProgrammeDay1.pdf")} | {link("Video", "https://www.youtube.com/watch?v=o8qmGErEjCQ")}',
))
story.append(dated_entry(
    "2020",
    link("Forming Groups of Students Best Suited to Work Together on a Sustainability Issue", "https://infoscience.epfl.ch/entities/publication/c7672f12-141f-48ed-8151-c7e88020f95b"),
    "With Philippe Thalmann. EPFL Teaching Sustainability Think Tank, November 23.",
))


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = CVDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.74 * inch,
        rightMargin=0.74 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.62 * inch,
        title="Academic Curriculum Vitae - Adam Robert Swietek",
        author="Adam Robert Swietek",
        subject="Academic curriculum vitae",
    )
    doc.build(story)
    shutil.copyfile(OUTPUT, WEBSITE_COPY)
    print(OUTPUT)
    print(WEBSITE_COPY)


if __name__ == "__main__":
    build()
