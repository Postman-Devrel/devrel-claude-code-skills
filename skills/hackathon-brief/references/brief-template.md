# Brief template

Write `hackathon-output/{slug}/brief.md` with these sections, in this order. Use tables where shown. Mark unconfirmed values `TBC`. Dates in the implementation plan are counted back from the event date; if the month is known but not the day, use "T-minus" weeks and a note to set the date.

````markdown
---
title: "{Theme title}: {Partner} x Postman Hackathon"
slug: {slug}
type: public | joint-customer | influencer | challenge-based
mode: in-person | virtual
city: {city or n/a}
target_month: {YYYY-MM}
status: draft
created: {YYYY-MM-DD}
---

# {Title}

## 1. Summary
Three to five sentences: what it is, who it is for, why now, what success looks like. Include the one-sentence theme developers can repeat.

## 2. Goals and success metrics
| Goal | Metric | Target | Source | Measure at |
|------|--------|--------|--------|------------|
One row per goal. Add 30, 60, and 90 day follow-up measurements. For sales influence include: target-list attendees, expansion opps within 180 days, closed-won within 180 days.

## 3. Event design
- Type, access model, mode, length, start time, location
- Partner and roles (who funds, who hosts, who staffs)
- Required technology and who provides access
- Participant machines and setup: machine requirements (admin rights, OS, network reach), hosted alternative, pre-event verification, fallback for failures, owner
- Team size and team formation approach
- Submission requirements (working demo, repo, 3 minute video)

## 4. Audience and invitations
- Invitee model and list owner
- Personas and target companies or list source
- Registration runs through Luma: custom registration questions (skills, role, company, use case, machine admin-access confirmation, eligibility checks), approval model (guest approval for closed events, waitlist for hybrid), and who approves guests
- Registrations needed = required attendees divided by show rate; fallback triggers stated on the same basis
- Registration target, expected attendance, no-show assumption, venue capacity

## 5. Agenda
Table based on the sample for this type, adapted to the theme and partner.

## 6. Judging
- Criteria table with what judges look for and weights, published before registration opens
- Judges (Postman, partner, independent), calibration session, tie-break rule
- Feedback to teams and public results

## 7. Prizes
| Prize | Value | Funded by | Awarded for |
|-------|-------|-----------|-------------|
Add the continuation path for winners (credits, funded project, exec sponsor, community listing).

## 8. Budget
| Line | Estimate | Funded by | Notes |
|------|----------|-----------|-------|
Venue, catering, AV and Wi-Fi, swag, prizes, credits, creative, staff travel, contingency (about 10%). Totals, then:

- Cost per registrant, cost per expected attendee, cost per target-list attendee
- Break-even: total cost divided by closed-won deals needed, and the deal value required
- Assumptions listed

## 9. Staffing
Roles table: event lead, sales liaison, partner lead, mentors (ratio and count), judges, MC, creative, venue and catering, Luma and Discord, on-site support. Owner or `TBC`.

## 10. Implementation plan
Phased table: Task | Owner | Due | Notes. Phases and minimum tasks:

**T-10 to 8 weeks: Foundations**
- Confirm partner terms, funding split, and contacts
- Lock date and venue (or virtual platform); contract, deposit, capacity, accessibility, AV, Wi-Fi load test plan
- Approve brief, budget, and judging criteria
- Provision access: workspaces, credits, sandbox or gateway; test with a fresh account
- Name staff and mentors

**T-8 to 6 weeks: Build the assets**
- Creative: key art, social card, Luma banner, slides, badges and signage (file the creative request)
- Luma registration page with theme, agenda, rules, judging criteria, prizes, and the signup fields; private until approved
- Discord channel and support rota
- Starter kit, sample repo, setup guide; dry run with someone new
- Setup verification: registration check for machine requirements, setup email sequence, pre-event setup session or hello-world test, fallback for failures (loaner, hosted environment, team pairing), setup support channel
- Sales enablement: one page for the sales team (who to invite, talk track, link, deadline), plus a CRM list or campaign for tracking invites
- Common Room influencer list and outreach plan (influencer and mixed events)

**T-6 to 3 weeks: Invite and promote**
- Sales team briefing and invite window opens; weekly invite-to-registered report
- Partner co-marketing: partner channels, blog, newsletter, social
- Social media plan: announce, theme teaser, mentor and judge reveal, prize reveal, countdown, live posting, recap
- Email to waitlist and past event attendees
- Open public registration (if hybrid)
- Mentor and judge briefing sessions scheduled

**T-3 to 1 weeks: Prepare**
- Confirm headcount with venue; catering order, dietary needs, and overbuffer
- Send starter kit and setup guide to all registrants; pre-event workshop or office hours
- Team formation: channel, matching form, buddy pairing for first-timers
- Run of show, floor plan (teams by challenge area, mentor stations on foot traffic, quiet and social zones)
- Judge calibration session; scoring sheet and submission form tested
- Swag, prizes, badges, signage ordered and delivered

**Event week**
- Day before: Wi-Fi, power, projectors, audio, submission flow, check-in tested
- Day of: check-in, kickoff, hacking, mentor rotation, midpoint check, submissions, judging, demos, awards
- Photographer or recording, live social posting

**T+0 to 48 hours: Follow up**
- Thank-you email with recap and next step
- Publish winners, rules, and results; public recap post
- Repos and projects published; personal notes to standout teams, including non-winners
- Hand sales a list of attendees from target accounts with their project notes

**T+30, 60, 90 days: Measure and continue**
- Measure the goal metrics; report to stakeholders
- Continuation path for top projects: funding, community listing, SE or sales owner
- Alumni channel touchpoint; invite to the next event

## 11. Social and communications plan
Channels, cadence, messages, and owners for pre, during, and post event.

## 12. Risks and open questions
Unresolved principle conflicts, `TBC` items, the three biggest risks with a mitigation each.

## 13. Sources
Links for any partner, venue, or market facts that came from research, plus the best-practices sources used.
````

After writing, tell the user: the path, the three biggest risks, and the `TBC` count.
