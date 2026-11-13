"""Image routing regression checks; no API calls or credentials."""
import base64
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import router
from PIL import Image

class ImageRoutingTests(unittest.TestCase):
    def setUp(self):
        router._image_down = False
        block = patch("subprocess.run", side_effect=AssertionError("No subprocess allowed in offline tests"))
        block.start()
        self.addCleanup(block.stop)
        buf = io.BytesIO()
        Image.new("RGB", (2, 2), "blue").save(buf, "PNG")
        self.png = buf.getvalue()

    def test_generation_emits_selected_model(self):
        with patch.object(router, "_post", return_value={"data": [{"b64_json": base64.b64encode(self.png).decode()}]}) as transport:
            self.assertEqual(router.image("blue circle"), self.png)
        endpoint, body, _ = transport.call_args.args
        self.assertEqual(endpoint, "/images/generations")
        self.assertEqual(body["model"], "cx/gpt-image-2.6-sunburst")

    def test_failure_propagates_without_switching_backend(self):
        with patch.object(router, "_image_9router", side_effect=RuntimeError("image quota exhausted")):
            with patch.object(router, "_image_codex", create=True) as fallback:
                with self.assertRaisesRegex(RuntimeError, "image quota exhausted"):
                    router.image("blue circle")
                fallback.assert_not_called()

    def test_reference_failure_propagates_without_switching_backend(self):
        if not hasattr(router, "image_ref"):
            return
        with patch.object(router, "_image_ref_9router", side_effect=RuntimeError("bad reference")):
            with patch.object(router, "_image_ref_codex", create=True) as fallback:
                with self.assertRaisesRegex(RuntimeError, "bad reference"):
                    router.image_ref("same subject", ["reference.png"])
                fallback.assert_not_called()

if __name__ == "__main__":
    unittest.main()
