import unittest

from analyzer import (
    GROUP_STYLE_MAP,
    analyze_lyrics,
    find_last_chinese_char,
    get_final_info,
)


class AnalyzerTests(unittest.TestCase):
    def test_finds_last_chinese_character_after_punctuation(self):
        self.assertEqual(find_last_chinese_char("月亮代表我的心。"), "心")
        self.assertEqual(find_last_chinese_char("月亮代表我的心 (live) 🎵"), "心")

    def test_non_chinese_line_degrades_without_crashing(self):
        score, _, results, _, _, main_group, _ = analyze_lyrics(
            ["hello world!", "月亮代表我的心。"]
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["rhyme_group"], "unknown")
        self.assertFalse(results[0]["recognized"])
        self.assertEqual(main_group, "人辰")
        self.assertEqual(score, 50)

    def test_empty_lines_are_ignored_and_original_indexes_are_kept(self):
        _, _, results, _, _, _, _ = analyze_lyrics(
            ["风吹过天空", "", "醒来仍然心动"]
        )

        self.assertEqual([item["line_idx"] for item in results], [1, 3])

    def test_same_rhyme_group_scores_one_hundred(self):
        score, level, results, _, _, main_group, _ = analyze_lyrics(
            ["我站在风中。", "等远方的钟！", "仍为你心动？"]
        )

        self.assertEqual(score, 100)
        self.assertEqual(main_group, "中东")
        self.assertEqual(level, "主韵高度集中")
        self.assertTrue(all(item["recognized"] for item in results))

    def test_get_final_info_handles_missing_character(self):
        self.assertEqual(get_final_info(None), ("N/A", "unknown", "0", False))

    def test_rhyme_group_colors_are_unique(self):
        colors = [
            style["background"]
            for group, style in GROUP_STYLE_MAP.items()
            if group != "unknown"
        ]
        self.assertEqual(len(colors), len(set(colors)))

    def test_cliche_detection_is_presented_as_risk(self):
        _, _, _, suspicious, _, _, _ = analyze_lyrics(
            ["月亮代表我的心", "我还站在这里"]
        )

        self.assertTrue(suspicious)
        self.assertTrue(any("建议检查" in reason for _, reason in suspicious))


if __name__ == "__main__":
    unittest.main()
