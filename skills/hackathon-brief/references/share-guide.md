# Shareable brief and PDF

The planning brief (`brief.md`) is for the team running the event. The shareable brief is for two other audiences: the sales team and AEs who invite people, and the prospects who are invited. Its job is to make both groups want to be there. Write it after the planning brief is approved, from the same answers.

Start the message that hands it over with one line naming the audience, for example "Written for: sales teams and invited developers at joint customers."

## Files

- `share.html`: the designed page, authored for print (Letter)
- `share.pdf`: printed from `share.html` with `references/render-pdf.py`

Both go in the event folder, next to `brief.md`.

## Structure: 2 pages maximum, and it should read like an ad

The planning brief carries the detail. This one is short, loud, and built to be forwarded. Every line is either a reason to want to be there or a fact needed to say yes.

1. **Page 1, the ad (safe to forward to prospects).** A big headline a developer would repeat, date, time, and place set large, a row of big-number proof points drawn from real facts (build hours, mentors, prize pool, licences needed), what you walk away with, and what to expect on the day in one compact line or bar. Nothing on this page needs a footnote except the draft line.
2. **Page 2, for reps (marked internal).** Why a rep should send customers (what it gives them), who to invite, two lines to say, the four questions prospects ask with short answers, what not to promise, and the dates reps need.

If a fact does not fit on two pages, it belongs in `brief.md`. Judging weights, full agendas, and setup detail go in the planning brief and the Luma page, not here. For a public event, leave page 2 out and give reps a separate sales-kit file.

Page 1 is written for the prospect and page 2 for the rep, so say in the hand-over line who each page is for.

## What goes in, what stays out

- **In:** date and time, place, who it is for, the theme, what is provided, what to bring, the agenda, the published judging criteria, prizes with "official rules apply", registration route, setup deadlines, the follow-up the sales team does.
- **Out:** budget, cost per head, break-even, risks, owner names for internal tasks, `TBC` tables, other customers' names, unconfirmed commitments. Never put internal numbers or risks on a page a prospect might see.
- **Unconfirmed facts** (provisional date, prizes awaiting legal review, credits awaiting confirmation) are either left out or carried with an explicit footer line: "Draft: date, prizes and credits subject to confirmation." Tell the user which facts are carried provisionally.
- **No invented facts.** Every claim traces to an answer in the interview. No made-up URLs; say "Your invitation includes the registration link" until the Luma link exists.

## Voice

Exciting but specific, developer to developer. Lead with what the person gets and builds, not with Postman. Punchy: short sentences, concrete numbers, verbs that show a result. No "supercharge", "unlock", "revolutionize", or "leverage"; no em dashes; no exclamation marks; no emoji. Hype words add nothing; a real number and a real deliverable do. Say the hard parts in one short line (laptop admin rights, setup deadline); developers trust that. Promise the goal ("the goal is an agent running by 6 PM"), not the outcome.

## Design

Use the repo's existing Postman system (precedence: the user's words, then the project system, then your choices):

- White page; text `#1A1D21`, dim `#5F6670`, border `#DADDE2`, tile `#F7F8FA`
- Postman orange `#FF6C37` for the accent, `#C2410C` for orange text (contrast on white), tint `#FFF6F1`
- Space Grotesk for display and body, JetBrains Mono for labels, times, and numbers (Google Fonts link; fallback Arial and monospace)
- `@page` Letter, margins about 0.5in, one `.page` section per printed page with `break-after: page`
- Define every color as a token in `:root`; print is a single light theme, so no dark blocks

Design choices that make it specific to the event instead of a template:
- A dark hero block on page 1 with the headline set very large, the accent on the second half of the headline, and date, time, and place in the mono face
- Big-number proof points (large numerals, small caption) built only from real, confirmed facts
- If the agenda is shown, draw it as one bar to scale using the real clock times, with the build window dominant
- Use the event's real facts as the typography, such as large times and the date
- Left-aligned, no card on every block, no emoji, no gradient; keep the orange in one or two places per page
- Marketing energy comes from the copy and the scale of the type, not from decoration

Check the PDF by converting pages to images (`pdftoppm -r 60 -png`) and looking at each page once: no text clipped, nothing running off a page, no page more than one-third empty, and page breaks where intended. Fix once and re-render.
