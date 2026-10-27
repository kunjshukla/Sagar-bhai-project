"""Deterministic, hard-coded conversation state machine."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from . import content
from .storage import BotStore


@dataclass(frozen=True)
class FlowResult:
    messages: tuple[str, ...]
    meeting: dict[str, str] | None = None


def _clean(value: str, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())[:limit]


def _normalized(value: str) -> str:
    value = _clean(value).casefold()
    return re.sub(r"[^a-z0-9+#&₹ -]+", " ", value).strip()


def _matches(value: str, aliases: Iterable[str]) -> bool:
    normalized = _normalized(value)
    if not normalized:
        return False
    for alias in aliases:
        candidate = _normalized(alias)
        if normalized == candidate:
            return True
        if len(candidate) > 2 and candidate in normalized:
            return True
    return False


class ConversationEngine:
    """Resolve one inbound message into one or more hard-coded replies."""

    def __init__(self, store: BotStore, booking_url: str = "") -> None:
        self.store = store
        self.booking_url = booking_url.rstrip("/")

    def handle(
        self,
        chat_key: str,
        text: str,
        *,
        display_name: str = "",
        phone: str = "",
    ) -> FlowResult:
        text = _clean(text)
        normalized = _normalized(text)
        state = self.store.get_state(chat_key)

        if display_name and not state.get("display_name"):
            state["display_name"] = _clean(display_name, 80)
        if phone:
            state["phone"] = _clean(phone, 40)

        if normalized in {"start", "restart", "hi", "hello", "hey", "namaste"}:
            state = {
                "stage": "menu",
                "lead": {},
                "context": {},
                "display_name": _clean(display_name, 80) or state.get("display_name", ""),
                "phone": _clean(phone, 40) or state.get("phone", ""),
            }
            self.store.save_state(chat_key, state)
            return FlowResult((content.main_menu(state.get("display_name", "")),))

        if normalized in {"m", "menu", "main menu", "back", "cancel"}:
            state["stage"] = "menu"
            state["context"] = {}
            self.store.save_state(chat_key, state)
            return FlowResult((content.main_menu(state.get("display_name", "")),))

        if normalized in {"help", "options", "commands"}:
            self.store.save_state(chat_key, state)
            return FlowResult((content.HELP,))

        if self._is_booking_intent(normalized):
            return self._start_booking(chat_key, state)

        stage = state.get("stage", "menu")
        handlers = {
            "menu": self._handle_menu,
            "products": self._handle_products,
            "services": self._handle_services,
            "solutions": self._handle_solutions,
            "qualification": self._handle_qualification,
            "book_name": self._book_name,
            "book_company": self._book_company,
            "book_purpose": self._book_purpose,
            "book_mode": self._book_mode,
            "book_date": self._book_date,
            "book_time": self._book_time,
            "book_confirm": self._book_confirm,
        }
        handler = handlers.get(stage, self._handle_menu)
        return handler(chat_key, state, text)

    @staticmethod
    def _is_booking_intent(normalized: str) -> bool:
        return normalized in {
            "f",
            "book",
            "book meeting",
            "book a meeting",
            "meeting",
            "demo",
            "book demo",
        }

    def _handle_menu(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        normalized = _normalized(text)
        if normalized in {"a", "product", "products", "software"}:
            state["stage"] = "products"
            self.store.save_state(chat_key, state)
            return FlowResult((content.PRODUCT_MENU,))
        if normalized in {"b", "service", "services", "support"}:
            state["stage"] = "services"
            self.store.save_state(chat_key, state)
            return FlowResult((content.SERVICE_MENU,))
        if normalized in {"c", "solution", "solutions", "recommend"}:
            state["stage"] = "solutions"
            self.store.save_state(chat_key, state)
            return FlowResult((content.SOLUTION_MENU,))
        if normalized in {"d", "about", "about us", "company", "who are you"}:
            state["stage"] = "menu"
            self.store.save_state(chat_key, state)
            return FlowResult((content.ABOUT,))
        if normalized in {
            "e",
            "contact",
            "contact us",
            "address",
            "phone",
            "email",
            "location",
            "hours",
        }:
            state["stage"] = "menu"
            self.store.save_state(chat_key, state)
            return FlowResult((content.CONTACT,))

        # Service intent takes precedence when a message contains both a product/machine
        # term and a service term, e.g. "PowerMill post for a 5-axis Fanuc".
        service = self._find_catalog_item(text, content.SERVICES)
        if service:
            return self._select_item(chat_key, state, "service", service, content.SERVICES[service])
        product = self._find_catalog_item(text, content.PRODUCTS)
        if product:
            return self._select_item(chat_key, state, "product", product, content.PRODUCTS[product])

        if any(
            token in normalized
            for token in ("machine", "part", "axis", "turning", "milling", "mold", "controller")
        ):
            state["stage"] = "solutions"
            state["context"] = {"initial_need": text}
            self.store.save_state(chat_key, state)
            return FlowResult((content.SOLUTION_MENU,))

        self.store.save_state(chat_key, state)
        return FlowResult(
            (
                "I want to make sure I point you to the right team. You can choose A-E, reply BOOK, "
                "or tell me what you make, which machine/controller you use, and what you want to improve.\n\n"
                + content.main_menu(state.get("display_name", "")),
            )
        )

    def _handle_products(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        key = self._find_catalog_item(text, content.PRODUCTS)
        if not key:
            self.store.save_state(chat_key, state)
            return FlowResult(("I didn’t catch the product yet.\n\n" + content.PRODUCT_MENU,))
        return self._select_item(chat_key, state, "product", key, content.PRODUCTS[key])

    def _handle_services(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        key = self._find_catalog_item(text, content.SERVICES)
        if not key:
            self.store.save_state(chat_key, state)
            return FlowResult(("I didn’t catch the service yet.\n\n" + content.SERVICE_MENU,))
        return self._select_item(chat_key, state, "service", key, content.SERVICES[key])

    def _handle_solutions(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        normalized = _normalized(text)
        mapping = {
            "1": "design",
            "2": "drafting",
            "3": "mold_design",
            "4": "complex_cam",
            "5": "automated_cam",
            "6": "swiss",
        }
        solution_key = mapping.get(normalized)
        if solution_key is None:
            product_key = self._find_catalog_item(text, content.PRODUCTS)
            reverse = {
                "fusion": "design",
                "autocad": "drafting",
                "powershape": "mold_design",
                "powermill": "complex_cam",
                "featurecam": "automated_cam",
                "partmaker": "swiss",
            }
            solution_key = reverse.get(product_key or "")

        if normalized in {"7", "not sure", "unsure", "dont know", "don t know"}:
            state["stage"] = "qualification"
            state["context"] = {"kind": "solution", "key": "unsure", "label": "Needs assessment"}
            self.store.save_state(chat_key, state)
            return FlowResult((content.UNSURE_SOLUTION,))

        if solution_key:
            label, message = content.SOLUTIONS[solution_key]
            state["stage"] = "qualification"
            state["context"] = {"kind": "solution", "key": solution_key, "label": label}
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    f"Based on that, {label} is the closest fit. {message}\n\n"
                    "What do you make, which machine/controller do you use, and what would a better workflow change for your team?",
                )
            )

        state["stage"] = "qualification"
        state["context"] = {"kind": "solution", "key": "unsure", "label": "Needs assessment"}
        self.store.save_state(chat_key, state)
        return FlowResult((content.UNSURE_SOLUTION,))

    def _select_item(
        self,
        chat_key: str,
        state: dict[str, Any],
        kind: str,
        key: str,
        item: dict[str, Any],
    ) -> FlowResult:
        state["stage"] = "qualification"
        state["context"] = {"kind": kind, "key": key, "label": item["label"]}
        self.store.save_state(chat_key, state)
        return FlowResult((item["message"],))

    def _handle_qualification(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        normalized = _normalized(text)
        if normalized in {"ask", "add", "add detail", "more"}:
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    "Go ahead — share any other part, machine, controller, software, timeline, or team detail that matters.",
                )
            )

        context = state.setdefault("context", {})
        details = context.setdefault("details", [])
        details.append(_clean(text, 1000))
        context["details"] = details[-5:]
        state["stage"] = "qualification"
        self.store.save_state(chat_key, state)
        return FlowResult((content.QUALIFIED_CTA,))

    def _start_booking(self, chat_key: str, state: dict[str, Any]) -> FlowResult:
        previous_context = state.get("context", {})
        inferred_purpose = ""
        if previous_context:
            label = previous_context.get("label", "")
            details = previous_context.get("details", [])
            parts = [str(label).strip(), *[str(item).strip() for item in details]]
            inferred_purpose = " — ".join(part for part in parts if part)
        if self.booking_url:
            params = {
                "phone": state.get("phone", ""),
                "name": state.get("display_name", ""),
            }
            link = f"{self.booking_url}?{urlencode({k: v for k, v in params.items() if v})}"
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    "Perfect — please choose an available business-hours slot in Mechman’s meeting form:\n\n"
                    f"{link}\n\n"
                    "The form only asks for your name, phone, email, and preferred date/time. "
                    "After submission, the request appears in Mechman’s dashboard for confirmation.",
                )
            )
        state["stage"] = "book_name"
        state["lead"] = {"purpose": inferred_purpose}
        self.store.save_state(chat_key, state)
        return FlowResult(
            (
                "Perfect — I’ll collect a few details so the right Mechman specialist can confirm the meeting.\n\n"
                "What name should I use for the booking?",
            )
        )

    def _book_name(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        if len(_clean(text)) < 2:
            return FlowResult(("Please share the name you’d like us to use for the booking.",))
        state.setdefault("lead", {})["name"] = _clean(text, 100)
        state["stage"] = "book_company"
        self.store.save_state(chat_key, state)
        return FlowResult(
            (
                "Thanks. Which company or workshop are you with? If this is personal, reply PERSONAL.",
            )
        )

    def _book_company(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        state.setdefault("lead", {})["company"] = (
            "Personal" if _normalized(text) == "personal" else _clean(text, 160)
        )
        if not state["lead"].get("company"):
            return FlowResult(("Please share your company/workshop name, or reply PERSONAL.",))
        if state["lead"].get("purpose"):
            state["stage"] = "book_mode"
            prompt = (
                f"I have the topic as: {state['lead']['purpose']}\n\n"
                "How would you prefer to meet?\n1 - Online video call\n2 - Phone call\n"
                "3 - Visit the Vadodara office\n4 - Onsite at your factory"
            )
        else:
            state["stage"] = "book_purpose"
            prompt = "What would you like the Mechman team to review or help you decide during the meeting?"
        self.store.save_state(chat_key, state)
        return FlowResult((prompt,))

    def _book_purpose(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        if len(_clean(text)) < 5:
            return FlowResult(
                (
                    "A short description will help us bring the right specialist. What would you like to discuss?",
                )
            )
        state.setdefault("lead", {})["purpose"] = _clean(text, 1000)
        state["stage"] = "book_mode"
        self.store.save_state(chat_key, state)
        return FlowResult(
            (
                "How would you prefer to meet?\n\n"
                "1 - Online video call\n2 - Phone call\n3 - Visit the Vadodara office\n4 - Onsite at your factory",
            )
        )

    def _book_mode(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        normalized = _normalized(text)
        modes = {
            "1": "Online video call",
            "online": "Online video call",
            "video": "Online video call",
            "video call": "Online video call",
            "2": "Phone call",
            "phone": "Phone call",
            "call": "Phone call",
            "phone call": "Phone call",
            "3": "Visit Mechman’s Vadodara office",
            "office": "Visit Mechman’s Vadodara office",
            "visit office": "Visit Mechman’s Vadodara office",
            "4": "Onsite at customer factory",
            "onsite": "Onsite at customer factory",
            "factory": "Onsite at customer factory",
        }
        mode = modes.get(normalized)
        if not mode:
            return FlowResult(
                (
                    "Please choose 1 for online, 2 for phone, 3 for the Vadodara office, or 4 for an onsite factory visit.",
                )
            )
        state.setdefault("lead", {})["mode"] = mode
        state["stage"] = "book_date"
        self.store.save_state(chat_key, state)
        return FlowResult(
            (
                "What date would suit you? You can write it naturally, for example “Thursday, 29 October”.\n\n"
                f"Mechman’s published hours are {content.COMPANY['hours']}.",
            )
        )

    def _book_date(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        if len(_clean(text)) < 3:
            return FlowResult(
                ("Please share a preferred date so the team can check availability.",)
            )
        state.setdefault("lead", {})["date"] = _clean(text, 120)
        state["stage"] = "book_time"
        self.store.save_state(chat_key, state)
        return FlowResult(
            ("And what time or time range works best for you? Please include AM/PM if applicable.",)
        )

    def _book_time(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        if len(_clean(text)) < 2:
            return FlowResult(
                ("Please share a preferred time or range, such as 11:00 AM or 3-5 PM.",)
            )
        state.setdefault("lead", {})["time"] = _clean(text, 120)
        state["stage"] = "book_confirm"
        self.store.save_state(chat_key, state)
        return FlowResult((self._confirmation_text(state["lead"]),))

    def _book_confirm(self, chat_key: str, state: dict[str, Any], text: str) -> FlowResult:
        normalized = _normalized(text)
        if normalized in {"1", "yes", "y", "confirm", "confirmed", "ok", "okay"}:
            lead = {key: str(value) for key, value in state.get("lead", {}).items()}
            phone = str(state.get("phone", ""))
            meeting_id = self.store.add_meeting(chat_key, phone, lead)
            lead["id"] = str(meeting_id)
            lead["phone"] = phone
            state["stage"] = "menu"
            state["lead"] = {}
            state["context"] = {}
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    f"You’re all set — meeting request #{meeting_id} is recorded. ✅\n\n"
                    f"Preferred slot: {lead.get('date', '')}, {lead.get('time', '')}\n"
                    f"Format: {lead.get('mode', '')}\n\n"
                    "A Mechman team member will confirm the final slot with you on WhatsApp or phone. "
                    f"If anything changes, call {content.COMPANY['phone']}.\n\n"
                    "Reply M whenever you’d like to explore another option.",
                ),
                meeting=lead,
            )
        if normalized in {"2", "change", "edit", "change details"}:
            state["stage"] = "book_name"
            state["lead"] = {}
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    "No problem — let’s update it from the start. What name should I use for the booking?",
                )
            )
        if normalized in {"3", "no", "menu", "cancel"}:
            state["stage"] = "menu"
            state["lead"] = {}
            self.store.save_state(chat_key, state)
            return FlowResult(
                (
                    "No problem — the request was not submitted.\n\n"
                    + content.main_menu(state.get("display_name", "")),
                )
            )
        return FlowResult(
            (
                "Please reply 1 to confirm, 2 to change the details, or 3 to return to the main menu.",
            )
        )

    @staticmethod
    def _confirmation_text(lead: dict[str, Any]) -> str:
        return (
            "Here’s the meeting request:\n\n"
            f"Name: {lead.get('name', '')}\n"
            f"Company/workshop: {lead.get('company', '')}\n"
            f"Topic: {lead.get('purpose', '')}\n"
            f"Format: {lead.get('mode', '')}\n"
            f"Preferred date: {lead.get('date', '')}\n"
            f"Preferred time: {lead.get('time', '')}\n\n"
            "1 - Confirm\n2 - Change details\n3 - Main menu"
        )

    @staticmethod
    def _find_catalog_item(text: str, catalog: dict[str, dict[str, Any]]) -> str | None:
        for key, item in catalog.items():
            if _matches(text, item.get("aliases", ())):
                return key
        return None
