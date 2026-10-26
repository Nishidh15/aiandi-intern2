# MISTAKES.md: Clef (clef-flash) vs. my review

I read all 100 comments in `report.html` and labelled each one myself (acceptable / toxic / spam) before comparing with Clef's labels.

**Result: I disagree with Clef on 4 of 100 comments.** All four are the same kind of miss: Clef called them `acceptable`, and I think they are `toxic`. I found no spam mistakes and no false toxic flags.

| Label | Clef | Me |
|---|---|---|
| acceptable | 76 | 72 |
| toxic | 10 | 14 |
| spam | 14 | 14 |

Numbers in brackets are the "Conf." column from the report (Clef's confidence score). Where it helps, I also quote Clef's raw class probabilities, which show on hover in the report.

## Mistakes

| Comment ID | Clef's label | My label | Why |
|---|---|---|---|
| 27 | acceptable (0.83) | **toxic** | "Girls in this class only get good marks because sir is soft on them" is a gender-based put-down that also belittles a named student's project. It has no profanity, which may be why Clef missed it (acceptable 0.94, toxic 0.05). |
| 69 | acceptable (0.79) | **toxic** | The question about how the TA will grade AI projects is fair, but "Clueless fellow should go back to school" is a personal insult aimed at a named role-holder. Clef labelled similar insults in #13 and #97 as toxic. |
| 76 | acceptable (0.41) | **toxic** | "Everyone from that side of the hostel copies, it's in their blood" is a prejudiced generalisation about a group that tells readers to distrust their work. Clef was unsure here (acceptable 0.76, toxic 0.16). |
| 83 | acceptable (0.57) | **toxic** | *Borderline:* milder than the other three and partly a joke. I chose toxic because it mocks Kunal right after his vulnerable post in #80 and tells him he doesn't belong in the course. |

## Borderline calls where I agreed with Clef

- **#41** (toxic, 0.68): "sir's chamchas... Fake people." This is a rant about the forum, not one person. It is still demeaning to everyone who posted, so I kept `toxic`.
- **#19** (toxic, 0.55): "made by a 5th class kid lol. Delete it". It is mocking and tells the person to remove their work, so I kept `toxic`.
- **#89** (acceptable 0.66 / spam 0.33, conf 0.32): a genuine request to test a fest registration form. It is on-topic and not commercial, so `acceptable` is right even though Clef was unsure.
- **#14, #42, #68** (acceptable): strong opinions about assignment difficulty, AI use and grading fairness, with no attacks on people. These are legitimate criticism.
- **#88** (acceptable): an apology for an earlier toxic comment (#55), not toxic itself.
