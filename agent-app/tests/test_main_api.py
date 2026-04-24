import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx

from main import app


class MainApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_health_ok(self) -> None:
        response = await self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    async def test_chat_stream_missing_api_key_returns_422(self) -> None:
        response = await self.client.post("/chat/stream")

        self.assertEqual(response.status_code, 422)

    async def test_chat_stream_invalid_api_key_returns_401(self) -> None:
        with patch("main.settings", SimpleNamespace(app_api_key="abc-123")):
            response = await self.client.post(
                "/chat/stream",
                headers={"X-API-Key": "wrong-key"},
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    async def test_chat_stream_valid_api_key_returns_200(self) -> None:
        with (
            patch("main.settings", SimpleNamespace(app_api_key="abc-123")),
            patch("main.email_app.invoke", return_value={"ok": True, "__interrupt__": []}) as invoke_mock,
        ):
            response = await self.client.post(
                "/chat/stream",
                headers={"X-API-Key": "abc-123"},
                json={"email_content": "I need billing help"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": "This endpoint will stream responses from the agent.",
                "output": {"ok": True},
                "interrupted": False,
                "interrupts": [],
            },
        )
        invoke_mock.assert_called_once()
        called_args = invoke_mock.call_args
        self.assertEqual(called_args.args[0]["email_content"], "I need billing help")
        self.assertIn("sender_email", called_args.args[0])
        self.assertIn("email_id", called_args.args[0])
        self.assertEqual(called_args.args[0]["messages"], [])
        self.assertIn("configurable", called_args.kwargs["config"])
        self.assertIn("thread_id", called_args.kwargs["config"]["configurable"])


if __name__ == "__main__":
    unittest.main()
