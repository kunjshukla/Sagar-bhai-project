"""Neonize transport adapter.

Keeping Neonize-specific protobuf handling here lets the conversation engine
remain independent of WhatsApp and easy to test.
"""

from __future__ import annotations

import logging
from typing import Any

from .config import Settings
from .flow import ConversationEngine, FlowResult
from .pairing import PairingState
from .storage import BotStore

LOGGER = logging.getLogger(__name__)
IGNORED_SERVERS = {"g.us", "broadcast", "newsletter"}


class WhatsAppBot:
    def __init__(
        self,
        settings: Settings,
        pair_phone: str = "",
        *,
        store: BotStore | None = None,
        pairing_state: PairingState | None = None,
    ) -> None:
        # Imports stay local so flow tests do not need to load Neonize's native core.
        from neonize.client import NewClient

        settings.ensure_directories()
        self.settings = settings
        self.pair_phone = "".join(character for character in pair_phone if character.isdigit())
        self.store = store or BotStore(settings.bot_database)
        self.pairing_state = pairing_state or PairingState()
        self.engine = ConversationEngine(self.store, booking_url=settings.public_booking_url)
        self.client = NewClient(str(settings.session_database))
        self._register_handlers()

    def _register_handlers(self) -> None:
        from neonize import extract_text
        from neonize.events import ConnectedEv, DisconnectedEv, MessageEv

        self.client.event.qr(lambda _client, code: self.pairing_state.set_qr(code))

        @self.client.event(ConnectedEv)
        def on_connected(_client: Any, _event: Any) -> None:
            LOGGER.info("Connected to WhatsApp")
            self.pairing_state.set_connected()

        @self.client.event(DisconnectedEv)
        def on_disconnected(_client: Any, _event: Any) -> None:
            LOGGER.warning("Disconnected from WhatsApp")
            self.pairing_state.set_disconnected()

        @self.client.event(MessageEv)
        def on_message(client: Any, event: Any) -> None:
            try:
                source = event.Info.MessageSource
                if bool(getattr(source, "IsFromMe", False)):
                    return

                chat = source.Chat
                server = str(getattr(chat, "Server", ""))
                if server in IGNORED_SERVERS:
                    return

                message_id = str(getattr(event.Info, "ID", ""))
                if not self.store.claim_message(message_id):
                    LOGGER.debug("Skipped duplicate WhatsApp message %s", message_id)
                    return

                chat_user = str(getattr(chat, "User", ""))
                chat_key = f"{chat_user}@{server}" if server else chat_user
                sender = getattr(source, "Sender", None)
                phone = str(getattr(sender, "User", "")) or chat_user
                display_name = str(getattr(event.Info, "PushName", ""))
                incoming_text = str(extract_text(event.Message) or "").strip()

                if incoming_text:
                    result = self.engine.handle(
                        chat_key,
                        incoming_text,
                        display_name=display_name,
                        phone=phone,
                    )
                else:
                    result = FlowResult(
                        (
                            "Thanks — I received the file or media. Tell me what you would like our engineers "
                            "to review, or reply BOOK to arrange a meeting around it.",
                        )
                    )

                client.reply_message("\n\n".join(result.messages), event)
                if result.meeting and self.settings.team_alert_number:
                    client.send_message(
                        self.settings.team_alert_number,
                        self._format_team_alert(result.meeting),
                    )
            except Exception:
                LOGGER.exception("Failed while handling an inbound WhatsApp message")

    def run(self) -> None:
        try:
            if self.pair_phone:
                from neonize.proto.waCommon_pb2 import ClientName

                code = self.client.PairPhone(
                    self.pair_phone,
                    show_push_notification=True,
                    client_name=ClientName.LINUX,
                )
                print(f"Enter this code in WhatsApp Linked Devices: {code}")
            self.client.connect()
        except Exception as exc:
            self.pairing_state.set_error(str(exc))
            raise

    def send_text(self, phone: str, message: str) -> None:
        """Send an outbound message through the active Neonize session."""
        self.client.send_message(phone, message)

    @staticmethod
    def _format_team_alert(meeting: dict[str, str]) -> str:
        return (
            "New Mechman meeting request\n\n"
            f"Request: #{meeting.get('id', '')}\n"
            f"Name: {meeting.get('name', '')}\n"
            f"Phone: {meeting.get('phone', '')}\n"
            f"Company: {meeting.get('company', '')}\n"
            f"Topic: {meeting.get('purpose', '')}\n"
            f"Format: {meeting.get('mode', '')}\n"
            f"Preferred: {meeting.get('date', '')}, {meeting.get('time', '')}\n\n"
            "Status: Pending team confirmation"
        )
