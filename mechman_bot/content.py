"""Website-grounded, hard-coded conversation copy.

Company and offering claims in this file are taken only from mechmansolution.com.
The implementation deliberately does not call an LLM or improvise product facts.
"""

from __future__ import annotations

COMPANY = {
    "name": "Mechman Solutions",
    "phone": "+91 99137 89065",
    "phone_digits": "919913789065",
    "secondary_phone": "+91 70437 13080",
    "email": "mechmansolution@gmail.com",
    "alternate_email": "info@mechmansolution.com",
    "address": "256/50, Makarpura GIDC, Vadodara, Gujarat - 390010",
    "hours": "Monday to Saturday, 9:00 AM-6:30 PM IST",
    "website": "https://mechmansolution.com/",
}


def main_menu(name: str = "") -> str:
    greeting = f"Hi {name.strip().split()[0]}" if name.strip() else "Hi"
    return (
        f"{greeting} 👋 Welcome to Mechman Solutions.\n\n"
        "We help manufacturers choose, implement, and get real results from Autodesk CAD/CAM "
        "software. What would you like to explore?\n\n"
        "A - Products\n"
        "B - Services\n"
        "C - Solutions for your shop\n"
        "D - About Mechman\n"
        "E - Contact us\n"
        "F - Book a meeting\n\n"
        "Reply with a letter, or simply tell me what you are trying to design, program, or improve."
    )


PRODUCT_MENU = (
    "Great — which product are you considering?\n\n"
    "1 - Fusion 360 (integrated CAD/CAM/CAE)\n"
    "2 - PowerMill (complex 3, 4 & 5-axis CAM)\n"
    "3 - FeatureCAM (automated milling, turning & wire EDM)\n"
    "4 - PartMaker (Swiss lathe & turn-mill)\n"
    "5 - AutoCAD (2D/3D CAD)\n"
    "6 - PowerShape (mold, die, electrode & manufacturing CAD)\n\n"
    "Reply with a number, or describe your machine and the work you do."
)


SERVICE_MENU = (
    "Of course. Which kind of support would help most?\n\n"
    "1 - Software sales & implementation\n"
    "2 - Training & Autodesk certification\n"
    "3 - Custom post-processor development\n"
    "4 - CNC programming services\n"
    "5 - Support for an existing post-processor\n\n"
    "Reply with a number, or describe the challenge in your own words."
)


SOLUTION_MENU = (
    "Let’s match the solution to your shop. Which situation is closest?\n\n"
    "1 - Product design, simulation, electronics or documentation\n"
    "2 - 2D drafting / general CAD\n"
    "3 - Mold, die, electrode or difficult imported geometry\n"
    "4 - Mold & die or complex 3/4/5-axis programming\n"
    "5 - Repetitive milling, turning, turn-mill or wire EDM\n"
    "6 - Swiss-type lathe or multi-spindle turn-mill\n"
    "7 - I’m not sure yet\n\n"
    "You can reply with a number or explain what you make, your machine, and what is slowing you down."
)


PRODUCTS = {
    "fusion": {
        "label": "Fusion 360",
        "aliases": ("1", "fusion", "fusion 360", "fusion360", "cad cam cae"),
        "message": (
            "Fusion 360 keeps 3D design, CAM, simulation, electronics, drawings, and collaboration "
            "in one cloud-connected platform. On the manufacturing side it covers 2-axis turning, "
            "3-axis milling, 5-axis with the Machining Extension, mill-turn, and sheet-metal workflows.\n\n"
            "The website lists Fusion 360 Basic at ₹43,000/year and Manufacturing at ₹1,29,000/year "
            "per seat. Mechman can help with licensing, implementation, training, and post setup.\n\n"
            "What are you hoping to design or machine, and which CNC machine/controller do you use?"
        ),
    },
    "powermill": {
        "label": "PowerMill",
        "aliases": ("2", "powermill", "power mill", "5 axis", "5-axis", "mold", "die"),
        "message": (
            "PowerMill is Mechman’s high-end choice for complex 3, 4, and simultaneous 5-axis work — "
            "especially aerospace, mold & die, automotive tooling, and precision parts. Its website-listed "
            "strengths include Vortex clearance, barrel and trochoidal strategies, collision detection, "
            "machine simulation, and robot programming.\n\n"
            "What kind of parts are you programming today, and what machine, axis configuration, and "
            "controller are on your shop floor?"
        ),
    },
    "featurecam": {
        "label": "FeatureCAM",
        "aliases": ("3", "featurecam", "feature cam", "wire edm", "automatic feature"),
        "message": (
            "FeatureCAM is aimed at shops that want to automate repetitive programming. It recognizes "
            "holes, pockets, slots, and turned features from imported CAD, then applies reusable machining "
            "knowledge across milling, turning, turn-mill, Swiss, and wire EDM workflows.\n\n"
            "Which recurring parts or operations consume the most programming time for your team?"
        ),
    },
    "partmaker": {
        "label": "PartMaker",
        "aliases": (
            "4",
            "partmaker",
            "part maker",
            "swiss",
            "citizen",
            "star",
            "tsugami",
            "hanwha",
        ),
        "message": (
            "PartMaker is purpose-built for Swiss-type lathes and multi-spindle turn-mill machines. It "
            "supports synchronized spindles, sub-spindle and live tooling, process synchronization, "
            "back-working operations, and collision checking. The site specifically mentions Citizen, "
            "Star, Tsugami, Hanwha, and Mazak Integrex.\n\n"
            "Which machine model and controller do you run, and what type of precision parts do you make?"
        ),
    },
    "autocad": {
        "label": "AutoCAD",
        "aliases": ("5", "autocad", "auto cad", "2d", "drafting"),
        "message": (
            "AutoCAD covers professional 2D drafting and 3D modeling, with web and mobile access plus "
            "specialized Architecture, Mechanical, Electrical, MEP, Plant 3D, and Map 3D toolsets in the "
            "full edition. AutoCAD LT is the 2D-focused option.\n\n"
            "Is your main requirement 2D drafting, 3D modeling, or one of the specialized industry toolsets?"
        ),
    },
    "powershape": {
        "label": "PowerShape",
        "aliases": ("6", "powershape", "power shape", "electrode", "mesh repair"),
        "message": (
            "PowerShape is manufacturing CAD for molds, dies, electrodes, and other complex parts. It "
            "combines surface, solid, and mesh modeling, can repair third-party geometry, and links closely "
            "with PowerMill and FeatureCAM for downstream machining.\n\n"
            "Are you working on molds, dies, electrodes, mesh repair, or another complex-geometry workflow?"
        ),
    },
}


SERVICES = {
    "implementation": {
        "label": "Software sales & implementation",
        "aliases": ("1", "sales", "license", "licence", "implementation", "renewal", "buy"),
        "message": (
            "Mechman handles genuine Autodesk software procurement, licensing, installation, and machine-side "
            "setup for Fusion 360, PowerMill, FeatureCAM, PartMaker, AutoCAD, and PowerShape, with support "
            "from Vadodara and delivery across India.\n\n"
            "Which software are you considering, how many users need it, and is this a new license or renewal?"
        ),
    },
    "training": {
        "label": "Training & certification",
        "aliases": ("2", "training", "course", "certification", "batch", "learn"),
        "message": (
            "Mechman is an Autodesk Authorized Training Center. Training is available online, at the Vadodara "
            "center, or at your factory, with Autodesk certification on applicable courses and custom corporate "
            "programs for teams of three or more. Courses cover Fusion 360, PowerMill, FeatureCAM, PartMaker, "
            "AutoCAD, and PowerShape.\n\n"
            "Which software and skill level are you interested in, how many people will attend, and what format "
            "would suit you best?"
        ),
    },
    "post": {
        "label": "Custom post-processor development",
        "aliases": ("3", "post", "post processor", "post-processor", "g-code", "controller"),
        "message": (
            "Mechman builds custom posts for Fusion 360, PowerMill, FeatureCAM, PartMaker, HSM/HSMWorks, and "
            "InventorCAM — from 3-axis mills and lathes to 5-axis, Swiss, turn-mill, robots, and additive. "
            "The process includes scoping, build and test, documentation, and minor after-delivery adjustments.\n\n"
            "Please share your machine make/model, controller and version, CAM software and version, and the "
            "operations or G/M-code requirements you need the post to handle."
        ),
    },
    "programming": {
        "label": "CNC programming services",
        "aliases": (
            "4",
            "cnc programming",
            "programming service",
            "outsource",
            "toolpath",
            "setup sheet",
        ),
        "message": (
            "Mechman offers outsourced CNC programming for mold & die, 4/5-axis, turn-mill, and Swiss parts. "
            "The website describes a model-to-proven-toolpath service with setup sheets.\n\n"
            "What part are you planning to run, which machine/controller will cut it, and what timeline are you working to?"
        ),
    },
    "post_support": {
        "label": "Existing post-processor support",
        "aliases": (
            "5",
            "post support",
            "existing post",
            "post fix",
            "modify post",
            "post modification",
        ),
        "message": (
            "Mechman supports adjustments to existing post projects as well as new builds. To understand the "
            "issue, the team will need the existing post, machine and controller details, CAM software/version, "
            "and a sample of the incorrect versus expected NC output.\n\n"
            "What is the post doing now, and what output or machine behavior should change?"
        ),
    },
}


SOLUTIONS = {
    "design": (
        "Fusion 360",
        "Fusion 360 brings design, simulation, electronics, drawings, collaboration, and CAM into one workflow.",
    ),
    "drafting": (
        "AutoCAD",
        "For 2D drafting or general-purpose 2D/3D CAD, AutoCAD is the closest fit.",
    ),
    "mold_design": (
        "PowerShape",
        "For mold, die, electrode, mesh repair, and difficult manufacturing geometry, PowerShape is the focused option.",
    ),
    "complex_cam": (
        "PowerMill",
        "For complex mold & die, aerospace, or 3/4/5-axis programming, PowerMill is the specialist CAM platform.",
    ),
    "automated_cam": (
        "FeatureCAM",
        "For repetitive milling, turning, turn-mill, or wire EDM, FeatureCAM adds automatic feature recognition and reusable machining knowledge.",
    ),
    "swiss": (
        "PartMaker",
        "For Swiss-type lathes and multi-spindle turn-mill work, PartMaker is purpose-built for the workflow.",
    ),
}


ABOUT = (
    "Mechman Solutions was founded in Vadodara in 2015 by Sagar Brahmbhatt, who began on the manufacturing "
    "floor and has 17+ years of Autodesk CAM and post-processor experience. The company is an Autodesk "
    "Authorized Channel Partner and Authorized Training Center.\n\n"
    "The website reports 100+ companies served, 150+ active licenses, and 500+ professionals trained. Its "
    "team covers technical demos, licensing, Fusion 360 support, training, PowerMill 5-axis work, and custom "
    "post-processors across Gujarat and pan-India.\n\n"
    "Would you like to book a meeting with the team, or is there something specific you want to know first?\n\n"
    "Reply BOOK to arrange a meeting, or M for the main menu."
)


CONTACT = (
    "You can reach Mechman Solutions here:\n\n"
    f"📍 {COMPANY['address']}\n"
    f"📞 {COMPANY['phone']}\n"
    f"✉️ {COMPANY['email']}\n"
    f"🕐 {COMPANY['hours']}\n\n"
    "Would you like me to collect the details for a meeting with the team?\n\n"
    "Reply BOOK to continue, or M for the main menu."
)


QUALIFIED_CTA = (
    "Thanks — that gives the team useful context. The best next step is a short meeting so a Mechman "
    "specialist can review the requirement with you and recommend the right path.\n\n"
    "Reply BOOK to arrange it, ASK to add another detail, or M for the main menu."
)


UNSURE_SOLUTION = (
    "No problem — describe the part or product you make, the machine and controller you use, and the step "
    "that currently takes too long or causes errors. I’ll use that to point you in the right direction."
)


HELP = (
    "You can reply with a menu letter/number or just write naturally. At any time:\n\n"
    "BOOK - arrange a meeting\n"
    "M - main menu\n"
    "BACK - main menu\n"
    "START - restart the conversation"
)
