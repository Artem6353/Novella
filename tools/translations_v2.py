# -*- coding: utf-8 -*-
"""
translations_v2.py — английские переводы правок сценария v2.0 (ТЗ от 2026-10-07).

Задачи 1–4, 8: правила петли, Лена как character, видение трагедии,
линия отца, имена детей. Ключи = id новых/переписанных реплик в
game/scenes/*.rpy. Подключается в translations.py ПОСЛЕДНИМ, чтобы
переписанные реплики перекрывали старые переводы тех же id.
"""

TRANS_V2 = {
# --- Задача 1: правила петли (D2_NIGHT_FOREST) ---
"d2_night_forest_0100": "At the camp boundary I stopped: behind me it was so dark the darkness felt touchable.",
"d2_night_forest_0101": "You still think this place punishes.",
"d2_night_forest_0102": "Lena's voice came from the darkness between the pines. Calm, without echo — the way people speak nearby, not far away.",
"d2_night_forest_0103": "It isn't a punishment, Artyom. It's a loop. And it has three rules.",
"d2_night_forest_0104": "First: the signal is not accepted — the shift repeats. Until the call for help is heard to the end, the day starts over.",
"d2_night_forest_0105": "Second: only an outsider can break the loop. Someone who wasn't here for twenty years. Someone who arrived with a ticket, not with a memory.",
"d2_night_forest_0106": "Third: the end comes when the farewell is complete. Not when it is forgotten — when it is said out loud and heard to the end.",
"d2_night_forest_0107": "I turned around. There was no one on the path. Only the bell somewhere far away struck a fourth time — and dissolved.",
"d2_night_forest_0108": "Three rules. I memorized them. Because you won't be repeating them.",

# --- Задача 2: Лена как character ---
"d2_lena_warning_0100": "And one more thing. I want to be let go. Not forgotten — let go. Those are different words, and I spent twenty years learning the difference.",
"d3_lena_branch_0100": "She sat on the edge of the table — no longer a counselor, just a tired woman who hadn't been allowed to sit down for twenty years.",
"d3_lena_branch_0101": "I was strict, imagine that: twenty-two years old, a unit of forty kids, and I drilled them through line-ups like soldiers on a string.",
"d3_lena_branch_0102": "And all the while I dreamed of leaving for the city. Studying, wearing other people's sweaters in the dorm, staying up at night — from life, not from lights-out.",
"d3_lena_branch_0103": "I'm no saint, Artyom. I simply stayed. And sometimes it seems I stayed not instead of someone, but instead of something.",
"d3_lena_branch_0104": "What I fear most is that the sacrifice was for nothing. That if it was all in vain — then they were in vain too. And they weren't. Do you hear me? They weren't.",
# переписанные (де-мистификация; ключевая фраза «живой» остаётся ровно 2 раза)
"d1_night_walk_0004": "'Here it doesn't work that way,' she had said at the gate. I repeated it out loud to check how it sounds from the outside.",
"d3_lena_branch_0049": "She smiled. Wearily — the way people smile when they have decided to stop hiding.",
"d3_lena_branch_0050": "I'm not a riddle, Artyom. I'm a person who stayed behind. Ask me in words — and I'll answer in words.",
"d3_lena_branch_0051": "For the first time her voice sounded once. Only once — like any ordinary voice.",
"ending_forgotten_0014": "I wanted to answer him honestly. Something very simple. Like: I remember you. You were here. That is enough.",

# --- Задачи 3 и 8: видение трагедии, дети, молодой Игорь (D4_TRUTH) ---
"d4_truth_0100": "And then the camp showed me. Without asking — the way it shows what had been hidden for twenty years.",
"d4_truth_0101": "The storm came from the river side. The sky cracked — and the pier came alive in the lightning.",
"d4_truth_0102": "Twenty children stood on the boards in pajamas and jackets thrown over bare shoulders. Three closest to the water: Misha, nine, holding the hand of Kostya, eight. Anya, seven, clutching a paint jar to her chest.",
"d4_truth_0103": "Lena, will the boat hold everyone?",
"d4_truth_0104": "The boat will hold. I counted.",
"d4_truth_0105": "The radio hut on the bank blinked with a red lamp. A young man — Igor, nineteen, a wristwatch without a strap — shouted callsigns into the microphone that no one accepted.",
"d4_truth_0106": "Pine Shore calling Zarechye. Over. Pine Shore calling Zarechye…",
"d4_truth_0107": "The signal was not accepted. The dispatcher was asleep. Lightning struck the transformer — and the light on the pier went out entirely, like a breath.",
"d4_truth_0108": "Lena didn't scream. She counted. She pushed the boat off the pier — with her hands, waist-deep in freezing water — and shouted at the children to row for the far bank.",
"d4_truth_0109": "The boards of the pier went down. Quietly. Fearfully quietly: no scream, no splash — only the rain, which suddenly became the only sound in the world.",
"d4_truth_0110": "The boat reached the bank. In the morning the children were counted. All of them. Except her.",
"d4_truth_0111": "The vision let me go as suddenly as it had taken me. The pier was empty again. Only the boards under my feet were wet — although it hadn't rained for four days.",
"d4_truth_0112": "You led them out. Everyone you could reach.",
"d4_truth_0113": "Everyone I could reach.",
"d2_journal_0100": "In the margins, in pencil, in a child's hand: “Misha (9) — boat duty. Kostya (8) — winds the receiver. Anya (7) — paints the dawn so that it comes.”",

# --- Задача 4: отец ---
"d2_radio_repair_0100": "The tape hissed. And through the hiss, almost at the edge of hearing, something was added that hadn't been there before: a whisper.",
"d2_radio_repair_0101": "Lena, forgive me. I'll say it tomorrow.",
"d2_radio_repair_0102": "Tomorrow never came. I stood with the cassette in my hands and for the first time didn't know whose heart was beating louder — mine or the tape's.",
"ending_true_0100": "And behind her back, where the square was already turning into light, stood a man in an old jacket. He didn't come closer. He nodded — to her, not to me. And that was enough for both of them.",
"ending_true_0101": "Dad. I won't stay silent for twenty years. Do you hear me? I won't stay silent at all.",
"ending_true_0102": "Signal accepted. Broadcast delivered. Farewell completed.",
"ending_true_0103": "The three rules of the loop closed one after another, like three strikes of the bell. I said it out loud — so that the one who for twenty years never listened to the end would hear.",
"ending_secret_0100": "The three strikes of the bell still lived inside me. As did her “thank you for coming.” Some things don't dissolve at dawn — they just become quieter.",
}
