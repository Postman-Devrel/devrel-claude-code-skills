# Shareable brief and PDF

The planning brief (`brief.md`) is for the team running the event. The shareable brief is for two other audiences: the sales team and AEs who invite people, and the prospects who are invited. Its job is to make both groups want to be there. Write it after the planning brief is approved, from the same answers.

Start the message that hands it over with one line naming the audience, for example "Written for: sales teams and invited developers at joint customers."

## Files

- `share.html`: the designed page, authored for print (Letter)
- `share.pdf`: printed from `share.html` with `references/render-pdf.py`

Both go in the event folder, next to `brief.md`.

## Structure (4 pages for a closed event; trim or extend for other types)

1. **Cover and pitch.** Title, one line a developer would repeat, the key facts (date, time, place, who), and three reasons to come, each tied to something the attendee gets.
2. **What you'll build.** What teams build, what the event provides, what attendees bring, and what to do before the day. Required technology in plain language.
3. **The day.** The agenda drawn to scale, how teams are judged (the published criteria and weights), and prizes.
4. **For the sales team.** Who to invite, what to say, the dates AEs need, answers to the questions prospects ask, what not to promise, and what happens after the event. This page is marked for internal use; for a public event, move it into a separate `sales-kit` file instead of the prospect PDF.

## What goes in, what stays out

- **In:** date and time, place, who it is for, the theme, what is provided, what to bring, the agenda, the published judging criteria, prizes with "official rules apply", registration route, setup deadlines, the follow-up the sales team does.
- **Out:** budget, cost per head, break-even, risks, owner names for internal tasks, `TBC` tables, other customers' names, unconfirmed commitments. Never put internal numbers or risks on a page a prospect might see.
- **Unconfirmed facts** (provisional date, prizes awaiting legal review, credits awaiting confirmation) are either left out or carried with an explicit footer line: "Draft: date, prizes and credits subject to confirmation." Tell the user which facts are carried provisionally.
- **No invented facts.** Every claim traces to an answer in the interview. No made-up URLs; say "Your invitation includes the registration link" until the Luma link exists.

## Voice

Plain, specific, developer to developer. Lead with what the person gets and builds, not with Postman. No "supercharge", "unlock", "revolutionize", or "leverage"; no em dashes; no exclamation marks; no emoji. Short sentences. Say the hard parts honestly (laptop admin rights, setup deadline); developers trust that.

## Design

Use the repo's existing Postman system (precedence: the user's words, then the project system, then your choices):

- White page; text `#1A1D21`, dim `#5F6670`, border `#DADDE2`, tile `#F7F8FA`
- Postman orange `#FF6C37` for the accent, `#C2410C` for orange text (contrast on white), tint `#FFF6F1`
- Space Grotesk for display and body, JetBrains Mono for labels, times, and numbers (Google Fonts link; fallback Arial and monospace)
- `@page` Letter, margins about 0.5in, one `.page` section per printed page with `break-after: page`
- Define every color as a token in `:root`; print is a single light theme, so no dark blocks

Design choices that make it specific to the event instead of a template:
- Draw the agenda as a bar to scale, using the real clock times, with the build window as the dominant segment
- Draw judging weights as bars to scale
- Use the event's real facts as the typography, such as large times and the date
- Left-aligned, no card on every block, no emoji, no gradient hero; keep the orange in one or two places per page

Check the PDF by converting pages to images (`pdftoppm -r 60 -png`) and looking at each page once: no text clipped, nothing running off a page, no page more than two-thirds empty, and page breaks where intended. Fix once and re-render.
