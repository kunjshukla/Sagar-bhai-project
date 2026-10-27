from __future__ import annotations

import pytest

from mechman_bot.flow import ConversationEngine
from mechman_bot.storage import BotStore


@pytest.fixture()
def store() -> BotStore:
    instance = BotStore(":memory:")
    yield instance
    instance.close()


@pytest.fixture()
def engine(store: BotStore) -> ConversationEngine:
    return ConversationEngine(store)


def reply(engine: ConversationEngine, text: str, chat: str = "919999999999@s.whatsapp.net"):
    return engine.handle(
        chat,
        text,
        display_name="Kunj Shah",
        phone="919999999999",
    )


def test_welcome_is_personal_and_exposes_all_top_level_choices(engine: ConversationEngine) -> None:
    result = reply(engine, "Hi")

    assert "Hi Kunj" in result.messages[0]
    for choice in ("A - Products", "B - Services", "C - Solutions", "F - Book a meeting"):
        assert choice in result.messages[0]


def test_product_flow_asks_an_open_question_then_offers_meeting(engine: ConversationEngine) -> None:
    assert "which product" in reply(engine, "A").messages[0].lower()

    product = reply(engine, "PowerMill")
    assert "3, 4, and simultaneous 5-axis" in product.messages[0]
    assert product.messages[0].endswith("shop floor?")

    qualified = reply(engine, "We make aerospace impellers on a 5-axis Fanuc machine")
    assert "Reply BOOK" in qualified.messages[0]


def test_post_processor_flow_collects_technical_context(engine: ConversationEngine) -> None:
    reply(engine, "B")
    result = reply(engine, "3")

    assert "machine make/model" in result.messages[0]
    assert "CAM software and version" in result.messages[0]


def test_natural_post_request_beats_generic_five_axis_product_match(
    engine: ConversationEngine,
) -> None:
    result = reply(engine, "I need a PowerMill post for a Fanuc-controlled 5-axis machine")

    assert "custom posts" in result.messages[0]
    assert "machine make/model" in result.messages[0]


def test_solution_flow_recommends_partmaker_for_swiss(engine: ConversationEngine) -> None:
    reply(engine, "C")
    result = reply(engine, "6")

    assert "PartMaker is the closest fit" in result.messages[0]
    assert "which machine/controller" in result.messages[0]


def test_contact_details_are_from_the_website(engine: ConversationEngine) -> None:
    result = reply(engine, "E")

    message = result.messages[0]
    assert "+91 99137 89065" in message
    assert "Makarpura GIDC" in message
    assert "Monday to Saturday" in message


def test_complete_booking_is_persisted_and_returned(
    engine: ConversationEngine, store: BotStore
) -> None:
    assert "What name" in reply(engine, "BOOK").messages[0]
    reply(engine, "Raj Patel")
    reply(engine, "Precision Works")
    reply(engine, "We need a PowerMill demo for a 5-axis mold job")
    reply(engine, "1")
    reply(engine, "Thursday, 29 October")
    summary = reply(engine, "11:00 AM")
    assert "Here’s the meeting request" in summary.messages[0]

    result = reply(engine, "1")

    assert result.meeting is not None
    assert result.meeting["company"] == "Precision Works"
    assert "meeting request #1 is recorded" in result.messages[0]
    rows = store.list_meetings()
    assert len(rows) == 1
    assert rows[0]["status"] == "requested"
    assert rows[0]["preferred_time"] == "11:00 AM"


def test_booking_inherits_qualified_topic(engine: ConversationEngine, store: BotStore) -> None:
    reply(engine, "A")
    reply(engine, "FeatureCAM")
    reply(engine, "We repeat families of turned automotive parts")
    reply(engine, "BOOK")
    reply(engine, "Asha")
    mode_prompt = reply(engine, "ABC Components")

    assert "FeatureCAM" in mode_prompt.messages[0]
    assert "turned automotive parts" in mode_prompt.messages[0]


def test_duplicate_message_claim_is_idempotent(store: BotStore) -> None:
    assert store.claim_message("wamid-123") is True
    assert store.claim_message("wamid-123") is False


def test_restart_clears_an_in_progress_flow(engine: ConversationEngine) -> None:
    reply(engine, "BOOK")
    reply(engine, "Raj")

    result = reply(engine, "START")

    assert "A - Products" in result.messages[0]
