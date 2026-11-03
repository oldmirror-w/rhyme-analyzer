import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def create_app(self):
        app = AppTest.from_file("app.py")
        app.run(timeout=15)
        self.assertEqual(len(app.exception), 0)
        return app

    def test_initial_page_has_expected_controls(self):
        app = self.create_app()

        self.assertEqual(len(app.text_area), 1)
        self.assertEqual(
            [button.label for button in app.button],
            ["开始分析", "加载示例", "清空"],
        )

    def test_sample_button_fills_text_area(self):
        app = self.create_app()

        app.button[1].click().run(timeout=15)

        self.assertIn("我把旧梦留在风中", app.text_area[0].value)
        self.assertEqual(len(app.exception), 0)

    def test_analysis_accepts_punctuation_and_creates_results(self):
        app = self.create_app()
        lyrics = "我站在风中。\n等远方的钟！\n仍为你心动？"

        app.text_area[0].set_value(lyrics).run(timeout=15)
        app.button[0].click().run(timeout=15)

        self.assertEqual(len(app.exception), 0)
        self.assertIsNotNone(app.session_state["analysis"])
        score = app.session_state["analysis"][0]
        self.assertEqual(score, 100)
        card_markup = next(
            item.value for item in app.markdown if 'class="lyric-list"' in item.value
        )
        self.assertNotRegex(card_markup, r"\n\s{4,}<")

    def test_clear_button_removes_text_and_results(self):
        app = self.create_app()
        app.text_area[0].set_value("我站在风中\n仍为你心动").run(timeout=15)
        app.button[0].click().run(timeout=15)

        app.button[2].click().run(timeout=15)

        self.assertEqual(app.text_area[0].value, "")
        self.assertIsNone(app.session_state["analysis"])

    def test_user_html_is_escaped_in_result_cards(self):
        app = self.create_app()
        lyrics = "<b>危险内容</b>心。\n仍为你停在这里"

        app.text_area[0].set_value(lyrics).run(timeout=15)
        app.button[0].click().run(timeout=15)

        markdown_values = "\n".join(item.value for item in app.markdown)
        self.assertIn("&lt;b&gt;危险内容&lt;/b&gt;心。", markdown_values)
        self.assertNotIn("<b>危险内容</b>心。", markdown_values)


if __name__ == "__main__":
    unittest.main()
