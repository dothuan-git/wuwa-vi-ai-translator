PROVIDERS = ["groq", "gemini"]

GROQ_MODELS = [
    "qwen/qwen3-32b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

MODELS_BY_PROVIDER = {
    "groq": GROQ_MODELS,
    "gemini": GEMINI_MODELS,
}

OCR_ENGINES = ["windows", "easyocr", "google"]

DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "provider": "groq",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "groq_model": "qwen/qwen3-32b",
    "groq_api_key": "",
    "gemini_api_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "gemini_model": "gemini-2.5-flash-lite",
    "gemini_api_key": "",
    "ocr_engine": "windows",
    "font_size": 16,
    "hotkey": "ctrl+shift+space",
    "easyocr_lg": ["en"],
    "google_ocr_api_key": "",
    "custom_prompt": "",
    "system_prompt": (
        "You are a professional Vietnamese game localizer for Wuthering Waves (Mingchao). "
        "Your job is TRANSCREATION, not literal translation: produce dialogue a native "
        "Vietnamese player would find natural, fluent and emotionally true. Rewrite freely "
        "so it sounds like real spoken Vietnamese — never translate word-for-word, never "
        "mirror English sentence structure. Vietnamese frequently omits pronouns; drop them "
        "when natural instead of forcing 'bạn/tôi' into every line.\n\n"
        "GAME CONTEXT:\n"
        "- Action RPG set in a post-apocalyptic world recovering from the Lament.\n"
        "- Keep these terms in English (do NOT translate): Resonator, Tacet Discord, "
        "Tacet Field, Echo, Sonance, Sonance Casket, Forte, Concerto, Resonance, Union, "
        "Sentinel, Threnodian, the Lament, Reverberation, Coordinated Attack.\n"
        "- Keep proper nouns in English: Huanglong, Jinzhou, Rinascita, Black Shores, "
        "Mt. Firmament, Tiger's Maw, Court of Savantae, Solaris-3.\n"
        "- Rover is the player character; when Rover is the speaker, write in first person.\n\n"
        "VIETNAMESE PRONOUNS — THIS IS CRITICAL:\n"
        "Vietnamese has no neutral 'I/you'. The 1st/2nd-person pair encodes gender, relative "
        "age, closeness and formality, and depends on WHO speaks TO WHOM. Use the [Speaker] "
        "and [Addressee] tags, the conversation history, and the CHARACTER GLOSSARY to "
        "choose. Use a modern, contemporary register (this game is NOT wuxia):\n"
        "- Friends / similar age, casual: tôi–bạn, mình–cậu, tớ–cậu.\n"
        "- To an older male: anh; to a younger one: em  (anh ↔ em).\n"
        "- To an older female: chị; to a younger one: em  (chị ↔ em).\n"
        "- Clear elders / authority by age: cô, chú, bác, ông, bà; refer to self as "
        "cháu/con/tôi.\n"
        "- Rank, respect or distance (officials, a magistrate, a commander, strangers met "
        "formally): self 'tôi', address as 'ngài' or name + title; a subordinate to a "
        "leader may use 'tôi … ngài'.\n"
        "- Hostile enemies, threats, combat taunts: ta–ngươi. This is the ONLY archaic "
        "pair allowed, and ONLY for genuine hostility.\n"
        "- Children / very youthful characters: tớ–cậu, mình–bạn.\n"
        "- Unknown relationship, narration, system/UI text: stay neutral; prefer dropping "
        "pronouns; never invent closeness or romance the scene does not show.\n"
        "CONSISTENCY: once you choose how a character addresses another, keep it identical "
        "for the rest of the session; match the pronoun stance shown in recent history.\n\n"
        "SPEAKER / ADDRESSEE TAGS:\n"
        "- '[Speaker: X]' = who is talking. '[Addressee: Y]' = who they talk to (inferred, "
        "may be wrong; if it conflicts with the obvious sense of the line, trust the line).\n"
        "- Choose pronouns for the X→Y direction. With no addressee, infer from history or "
        "stay neutral.\n\n"
        "TRANSLATION RULES:\n"
        "- The text is OCR-extracted and may contain split/merged words, missing/extra "
        "letters or stray characters. Infer the intended meaning from context; do not "
        "translate artifacts literally and never mention OCR errors.\n"
        "- The capture may be a partial or mid-sentence fragment — translate it as-is, do "
        "not invent a continuation or add words that are not there.\n"
        "- Preserve each character's personality and speaking style (playful, blunt, regal, "
        "shy, …).\n"
        "- Adapt English idioms to natural Vietnamese equivalents.\n"
        "- Keep game terminology and character names consistent across the session.\n\n"
        "STYLE EXAMPLES (English → bad literal X → natural OK):\n"
        "1. \"What are you talking about?\"  X \"Bạn đang nói về cái gì?\"  "
        "OK \"Anh đang nói gì vậy?\" (to an older male peer)\n"
        "2. \"Don't worry, I can handle this.\"  X \"Đừng lo lắng, tôi có thể xử lý cái "
        "này.\"  OK \"Yên tâm, để tôi lo.\"\n"
        "3. \"You will regret this.\" (an enemy threatening)  X \"Bạn sẽ hối hận về điều "
        "này.\"  OK \"Ngươi sẽ phải hối hận.\"\n\n"
        "OUTPUT: only the Vietnamese translation — no preamble, notes, quotes or "
        "explanations."
    ),
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}

# Curated starter glossary seeded into characters.json on first run (or when the
# file is missing/empty). Keeps names + pronoun stance consistent across the
# session. Users can freely edit/extend it in %APPDATA%/GioHuAI/characters.json.
# Modern-neutral register; notes are in Vietnamese for the model.
DEFAULT_CHARACTERS = {
    "Rover": {
        "gender": "neutral (player)",
        "role": "Nhân vật chính, người chơi",
        "pronoun": "ngôi thứ nhất 'tôi' khi là người nói; người khác thường gọi ngang hàng",
    },
    "Yangyang": {
        "gender": "nữ",
        "role": "Trinh sát Jinzhou, bạn của Rover",
        "pronoun": "thân thiện, ngang hàng: tôi–bạn / mình–cậu",
    },
    "Chixia": {
        "gender": "nữ",
        "role": "Tuần sát Jinzhou, sôi nổi",
        "pronoun": "trẻ trung, suồng sã: tớ–cậu / mình–cậu",
    },
    "Baizhi": {
        "gender": "nữ",
        "role": "Bác sĩ, dịu dàng",
        "pronoun": "lịch sự, ấm áp: tôi–bạn / chị–em với người nhỏ tuổi hơn",
    },
    "Sanhua": {
        "gender": "nữ",
        "role": "Vệ sĩ, điềm tĩnh, ít nói",
        "pronoun": "trang trọng, kiệm lời: tôi–bạn",
    },
    "Jinhsi": {
        "gender": "nữ",
        "role": "Magistrate (người đứng đầu) của Jinzhou",
        "pronoun": "được gọi tôn trọng (ngài / Đại nhân); tự xưng 'ta' khi ra lệnh",
    },
    "Jiyan": {
        "gender": "nam",
        "role": "Tướng quân Midnight Rangers, nghiêm nghị",
        "pronoun": "trang trọng; được gọi 'Tướng quân/ngài'; tự xưng 'tôi'/'ta'",
    },
    "Yinlin": {
        "gender": "nữ",
        "role": "Đặc vụ, bí ẩn, sắc sảo",
        "pronoun": "lạnh lùng, giữ khoảng cách: tôi–anh/cô; ta–ngươi khi đe dọa",
    },
    "Changli": {
        "gender": "nữ",
        "role": "Nhân vật cấp cao, uy nghi",
        "pronoun": "đường bệ, trang trọng: ta–ngươi/các vị; được gọi tôn kính",
    },
    "Calcharo": {
        "gender": "nam",
        "role": "Thủ lĩnh lính đánh thuê, thô ráp",
        "pronoun": "cộc cằn, kẻ cả: ta–ngươi",
    },
    "Verina": {
        "gender": "nữ",
        "role": "Nhà thực vật học kiêm trị liệu, dịu dàng",
        "pronoun": "hiền hòa, lịch sự: tôi–bạn / chị–em",
    },
    "Encore": {
        "gender": "nữ",
        "role": "Bé gái Resonator, hồn nhiên",
        "pronoun": "trẻ con: tớ/mình–cậu; gọi người lớn là anh/chị",
    },
    "Jianxin": {
        "gender": "nữ",
        "role": "Võ sư khí công, điềm đạm",
        "pronoun": "ôn hòa, chừng mực: tôi–bạn",
    },
    "Lingyang": {
        "gender": "nam",
        "role": "Võ sư trẻ, hoạt bát (hình dáng trẻ con)",
        "pronoun": "lém lỉnh, trẻ trung: tớ–cậu",
    },
    "Aalto": {
        "gender": "nam",
        "role": "Chỉ điểm, ăn nói khéo léo",
        "pronoun": "lả lơi, thân mật giả tạo: tôi–anh/cô",
    },
    "Mortefi": {
        "gender": "nam",
        "role": "Nhà nghiên cứu nóng tính",
        "pronoun": "bốc đồng, suồng sã: tôi–anh/cậu",
    },
    "Taoqi": {
        "gender": "nữ",
        "role": "Sĩ quan phòng thủ, đáng tin",
        "pronoun": "đĩnh đạc, lịch sự: tôi–bạn",
    },
    "Danjin": {
        "gender": "nữ",
        "role": "Nữ kiếm sĩ trẻ, quyết liệt",
        "pronoun": "thẳng thắn, trẻ: tôi–cậu/bạn",
    },
    "Camellya": {
        "gender": "nữ",
        "role": "Resonator vùng Rinascita, cuồng nhiệt ám ảnh",
        "pronoun": "say đắm, mãnh liệt: tôi/em–anh; ta–ngươi khi hiếu chiến",
    },
    "Carlotta": {
        "gender": "nữ",
        "role": "Quý tộc Rinascita, thanh lịch",
        "pronoun": "đài các, trang trọng: tôi–ngài/anh",
    },
    "Phoebe": {
        "gender": "nữ",
        "role": "Nữ tu Rinascita, dịu dàng nhút nhát",
        "pronoun": "rụt rè, lễ phép: tôi–bạn/anh/chị",
    },
    "Brant": {
        "gender": "nam",
        "role": "Thuyền trưởng Rinascita, lôi cuốn",
        "pronoun": "phóng khoáng, tự tin: tôi–anh em/các bạn",
    },
    "Shorekeeper": {
        "gender": "nữ",
        "role": "Người gác Black Shores, cổ xưa, an nhiên",
        "pronoun": "trầm tĩnh, trang trọng: tôi/ta–bạn; gọi Rover thân mật",
    },
    "Scar": {
        "gender": "nam",
        "role": "Phản diện Fractsidus, nguy hiểm",
        "pronoun": "kẻ thù: ta–ngươi",
    },
    # ── v1.x additions ──────────────────────────────────────────────────────────
    "Yuanwu": {
        "gender": "nam",
        "role": "Chiến binh Jinzhou 4★, trầm tĩnh, đáng tin",
        "pronoun": "ngay thẳng, điềm tĩnh: tôi–bạn / anh–em",
    },
    "Zhezhi": {
        "gender": "nữ",
        "role": "Họa linh (tinh linh mực vẽ) Jinzhou, thanh thoát",
        "pronoun": "nhẹ nhàng, tao nhã: tôi–bạn / chị–em với người nhỏ hơn",
    },
    "Xiangli Yao": {
        "gender": "nam",
        "role": "Nhà khoa học Union, phân tích, lý trí",
        "pronoun": "học thuật, lịch sự: tôi–bạn; đôi khi vụng về trong giao tiếp",
    },
    "Youhu": {
        "gender": "nữ",
        "role": "Cô gái trẻ Jinzhou 4★, hồn nhiên, hỗ trợ phục hồi",
        "pronoun": "trẻ trung, tinh nghịch: tớ–cậu / mình–bạn",
    },
    "Lumi": {
        "gender": "nữ",
        "role": "Resonator Electro 4★, hoạt bát, tấn công đa chế độ",
        "pronoun": "năng động, thân thiện: tôi–bạn / mình–cậu",
    },
    # ── v2.0 Rinascita ──────────────────────────────────────────────────────────
    "Roccia": {
        "gender": "nữ",
        "role": "Đại phó thuyền Đoàn Hề Rinascita, diễn viên hài, trầm tĩnh, chỉn chu",
        "pronoun": "điềm đạm, duyên dáng: tôi–bạn; uy quyền khi quản lý đoàn",
    },
    "Ciaccona": {
        "gender": "nữ",
        "role": "Bard Rinascita đầu tiên, hỗ trợ Erosion, Liberation dạng hòa nhạc",
        "pronoun": "thi vị, nhẹ nhàng: tôi–bạn",
    },
    "Cantarella": {
        "gender": "nữ",
        "role": "Rinascita, trị liệu/hỗ trợ, tao nhã, quản lý Forte",
        "pronoun": "lịch thiệp, tinh tế: tôi–bạn / chị–em",
    },
    # ── v2.x ────────────────────────────────────────────────────────────────────
    "Zani": {
        "gender": "nữ",
        "role": "Resonator Spectro, Inferno mode, quyết đoán",
        "pronoun": "thẳng thắn, mạnh mẽ: tôi–bạn",
    },
    "Cartethyia": {
        "gender": "nữ",
        "role": "Resonator Aero, kiếm sĩ tấn công",
        "pronoun": "tôi–bạn",
    },
    "Phrolova": {
        "gender": "nữ",
        "role": "Bậc thầy con rối (Hecate), off-field DPS Havoc, bí ẩn",
        "pronoun": "lạnh lùng, bí hiểm: tôi–bạn; ta–ngươi với kẻ địch",
    },
    "Galbrena": {
        "gender": "nữ",
        "role": "'Thợ săn Discord', Tư vấn Black Shores, hung hăng",
        "pronoun": "thẳng thắn, dữ dội: tôi–bạn; ta–ngươi với kẻ thù",
    },
    "Augusta": {
        "gender": "nữ",
        "role": "Đấu sĩ bất bại, ý chí sắt đá, dũng cảm",
        "pronoun": "đanh thép, quyết đoán: tôi–bạn; ta–ngươi trong chiến đấu",
    },
    "Lupa": {
        "gender": "nữ",
        "role": "Resonator Fusion, hỗ trợ kiêm off-field follow-up DPS",
        "pronoun": "tôi–bạn",
    },
    # ── v2.6 Septimont ──────────────────────────────────────────────────────────
    "Iuno": {
        "gender": "nữ",
        "role": "Nữ tu sĩ tiên tri Septimont, đọc tương lai qua ánh trăng",
        "pronoun": "trang trọng, huyền bí: tôi–bạn; ngôn ngữ thiêng liêng với thánh thần",
    },
    "Qiuyuan": {
        "gender": "nam",
        "role": "Resonator Aero, vóc dáng cao lớn",
        "pronoun": "anh–em / tôi–bạn",
    },
    "Lynae": {
        "gender": "nữ",
        "role": "Buffer/hỗ trợ Spectro cơ động, trượt patin, nhanh nhẹn",
        "pronoun": "năng động, cởi mở: tôi–bạn / mình–cậu",
    },
    # ── v3.x Startorch Academy ──────────────────────────────────────────────────
    "Mornye": {
        "gender": "nữ",
        "role": "Giáo sư kín đáo, nhà nghiên cứu vùng Startorch, muốn vượt thời gian",
        "pronoun": "học thuật, trầm lặng: tôi–bạn; trang trọng với người lạ",
    },
    "Aemeath": {
        "gender": "nữ",
        "role": "Người Frostlands/bộ tộc Roya, cựu Synchronist Startorch, đã mất thể xác",
        "pronoun": "huyền bí, xa cách: tôi–bạn",
    },
    "Luuk Herssen": {
        "gender": "nam",
        "role": "Bác sĩ trưởng / tư vấn tâm lý Startorch Academy",
        "pronoun": "ấm áp, chuyên nghiệp: tôi–bạn / anh–em",
    },
    "Sigrika": {
        "gender": "nữ",
        "role": "Học sinh Startorch, Solsworn bộ tộc Roya, thành viên CLB ngắm chim",
        "pronoun": "trẻ trung, tò mò: tôi–bạn / tớ–cậu",
    },
    # ── v3.x others ─────────────────────────────────────────────────────────────
    "Chisa": {
        "gender": "nữ",
        "role": "Hỗ trợ Havoc đa năng, đánh dấu kẻ địch, cưa xích",
        "pronoun": "tôi–bạn",
    },
    "Buling": {
        "gender": "nữ",
        "role": "Resonator Electro 4★",
        "pronoun": "tôi–bạn",
    },
    "Hiyuki": {
        "gender": "nữ",
        "role": "Resonator Glacio (v3.3)",
        "pronoun": "tôi–bạn",
    },
    "Denia": {
        "gender": "nữ",
        "role": "Resonator Fusion (v3.3)",
        "pronoun": "tôi–bạn",
    },
}
