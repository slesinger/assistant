import asyncio
import inspect
import json
import logging
from asyncio import Queue, CancelledError
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

from google.cloud import texttospeech
import simpleaudio as sa
import hashlib
from os import path

ttsClient = texttospeech.TextToSpeechClient()

import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

def say(text, device):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    wav = "tts-cache/" + md5.hexdigest() + ".wav"

    if not path.exists(wav):
        print("SYNTEZA")
        voice = texttospeech.VoiceSelectionParams(
            language_code="cs-CZ", 
            name="cs-CZ-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.85
        )

        response = ttsClient.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(wav, "wb") as out:
            out.write(response.audio_content)

    wave_obj = sa.WaveObject.from_wave_file(wav)
    play_obj = wave_obj.play()
    play_obj.wait_done()


"""
Call it as: curl --request POST   --url http://localhost:5005/webhooks/plustts/webhook   --header 'content-type: application/json'   --data '{"sender":"loznice", "message":"kolik je hodin", "metadata": { "satelite": "jidelna"} }'
Configure in credentials.yml by adding: "channels.plustts.PlusttsInput:"
"""

logger = logging.getLogger(__name__)


class PlusttsInput(InputChannel):

    @classmethod
    def name(cls) -> Text:
        return "plustts"

    @staticmethod
    async def on_message_wrapper(
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
        text: Text,
        queue: Queue,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> None:
        collector = QueueOutputChannel(queue)

        message = UserMessage(
            text, collector, sender_id, input_channel=input_channel, metadata=metadata
        )
        await on_new_message(message)

        await queue.put("DONE")

    async def _extract_sender(self, req: Request) -> Optional[Text]:
        return req.json.get("sender", None)

    # noinspection PyMethodMayBeStatic
    def _extract_message(self, req: Request) -> Optional[Text]:
        return req.json.get("message", None)

    def _extract_input_channel(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def stream_response(
        self,
        on_new_message: Callable[[UserMessage], Awaitable[None]],
        text: Text,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> Callable[[Any], Awaitable[None]]:
        async def stream(resp: Any) -> None:
            q = Queue()
            task = asyncio.ensure_future(
                self.on_message_wrapper(
                    on_new_message, text, q, sender_id, input_channel, metadata
                )
            )
            while True:
                result = await q.get()
                if result == "DONE":
                    break
                else:
                    await resp.write(json.dumps(result) + "\n")
            await task

        return stream

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender(request)
            text = self._extract_message(request)
            should_use_stream = rasa.utils.endpoints.bool_arg(
                request, "stream", default=False
            )
            input_channel = self._extract_input_channel(request)
            metadata = self.get_metadata(request)

            if should_use_stream:
                return response.stream(
                    self.stream_response(
                        on_new_message, text, sender_id, input_channel, metadata
                    ),
                    content_type="text/event-stream",
                )
            else:
                collector = CollectingOutputChannel()
                # noinspection PyBroadException
                try:
                    await on_new_message(
                        UserMessage(
                            text,
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
                        )
                    )
                except CancelledError:
                    logger.error(
                        f"Message handling timed out for " f"user message '{text}'."
                    )
                except Exception:
                    logger.exception(
                        f"An exception occured while handling "
                        f"user message '{text}'."
                    )
                for msg in collector.messages:
                    print(msg['text'])
                    say(msg['text'], "loznice")

                return response.json(collector.messages)

        return custom_webhook


class QueueOutputChannel(CollectingOutputChannel):
    """Output channel that looks up TTS cache and calls TTS if need be."""

    @classmethod
    def name(cls) -> Text:
        return "plustts"

    # noinspection PyMissingConstructor
    def __init__(self, message_queue: Optional[Queue] = None) -> None:
        super().__init__()
        self.messages = Queue() if not message_queue else message_queue

    def latest_output(self) -> NoReturn:
        raise NotImplementedError("A queue doesn't allow to peek at messages.")

    async def _persist_message(self, message) -> None:
        await self.messages.put(message)
