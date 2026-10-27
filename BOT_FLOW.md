# Mechman WhatsApp bot flow

The bot is deterministic: every outgoing sentence is written in `mechman_bot/content.py`. It does not call an LLM and it does not invent company, product, price, support, or customer information.

## Conversation principles

- Greet the WhatsApp display name when available.
- Accept both menu choices and natural phrases such as “I need a post for a Fanuc 5-axis.”
- Ask one useful open-ended question after presenting an offering.
- Keep `BOOK`, `M`, `BACK`, `START`, and `HELP` available throughout the conversation.
- Do not pretend a calendar slot is confirmed. Record the requested slot, create a request number, and clearly say the Mechman team will confirm it.
- Keep the meeting CTA contextual by carrying the selected offering and the visitor's technical answer into the booking summary.

## Top-level flow

```text
Hi / Hello / Start
  |
  +-- A Products
  |     +-- Fusion 360
  |     +-- PowerMill
  |     +-- FeatureCAM
  |     +-- PartMaker
  |     +-- AutoCAD
  |     +-- PowerShape
  |            |
  |            +-- Open technical question -> BOOK / add detail / menu
  |
  +-- B Services
  |     +-- Software sales & implementation
  |     +-- Training & certification
  |     +-- Custom post-processor
  |     +-- CNC programming
  |     +-- Existing post support
  |            |
  |            +-- Open requirement question -> BOOK / add detail / menu
  |
  +-- C Solutions
  |     +-- Design/simulation/electronics -> Fusion 360
  |     +-- 2D drafting/general CAD -> AutoCAD
  |     +-- Mold/die/electrode geometry -> PowerShape
  |     +-- Complex 3/4/5-axis -> PowerMill
  |     +-- Repetitive milling/turning/EDM -> FeatureCAM
  |     +-- Swiss/turn-mill -> PartMaker
  |     +-- Unsure -> describe part + machine + bottleneck
  |            |
  |            +-- BOOK / add detail / menu
  |
  +-- D About Mechman -> BOOK / menu
  +-- E Contact -> BOOK / menu
  +-- F Book a meeting
```

## Welcome copy

> Hi {first name} 👋 Welcome to Mechman Solutions.
>
> We help manufacturers choose, implement, and get real results from Autodesk CAD/CAM software. What would you like to explore?
>
> A - Products<br>
> B - Services<br>
> C - Solutions for your shop<br>
> D - About Mechman<br>
> E - Contact us<br>
> F - Book a meeting
>
> Reply with a letter, or simply tell me what you are trying to design, program, or improve.

## Open-ended qualifying questions

| Route | Question captured before the meeting CTA |
|---|---|
| Fusion 360 | What are you hoping to design or machine, and which CNC machine/controller do you use? |
| PowerMill | What parts do you program, and what machine, axis configuration, and controller are on your floor? |
| FeatureCAM | Which recurring parts or operations consume the most programming time? |
| PartMaker | Which machine model/controller do you run, and what precision parts do you make? |
| AutoCAD | Is the need 2D drafting, 3D modeling, or a specialized industry toolset? |
| PowerShape | Is the work molds, dies, electrodes, mesh repair, or another complex geometry workflow? |
| Software implementation | Which software, how many users, and new license or renewal? |
| Training | Which software/skill level, how many learners, and which training format? |
| Post-processor | Machine make/model, controller/version, CAM/version, and required operations or G/M codes? |
| CNC programming | What part, which machine/controller, and what production timeline? |
| Existing post support | What happens now, and what should the output or machine behavior be? |

## Meeting flow

When `PUBLIC_BOOKING_URL` is configured, the bot sends the custom booking form. It only asks for Name, Phone, Email, and an available Date/Time. The chat flow below remains as an offline fallback when no public booking URL is configured.

```text
BOOK
  -> booking name
  -> company/workshop (PERSONAL is accepted)
  -> meeting purpose (skipped when already learned from the branch)
  -> format: online / phone / Vadodara office / customer factory
  -> preferred date
  -> preferred time
  -> summary
       1 Confirm -> SQLite request + optional staff WhatsApp alert
       2 Change  -> restart meeting details
       3 Menu    -> discard unsubmitted request
```

The confirmation message states “meeting request is recorded,” assigns an ID, and says the final slot is pending team confirmation. This is intentional because the website supplies office hours but no calendar, capacity, meeting duration, or scheduling API.

## Example: natural non-menu route

```text
Visitor: I need a post for a Fanuc-controlled 5-axis machine.

Bot: Mechman builds custom posts for Fusion 360, PowerMill, FeatureCAM,
PartMaker, HSM/HSMWorks, and InventorCAM ...

Please share your machine make/model, controller and version, CAM software
and version, and the operations or G/M-code requirements you need the post
to handle.

Visitor: PowerMill 2026, Fanuc 31i, head-head, TCP and safe retracts.

Bot: Thanks — that gives the team useful context. The best next step is a
short meeting so a Mechman specialist can review the requirement with you ...

Reply BOOK to arrange it, ASK to add another detail, or M for the main menu.
```
