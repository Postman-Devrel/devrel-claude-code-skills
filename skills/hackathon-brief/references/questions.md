# Interview script

Ask in this order, one question at a time. For each question: the ask, what a good answer looks like, what is weak, and the push-back to use. Skip any question the user has already answered (including inside a long first message); restate what you captured and move on. Never read field names aloud; ask about the event.

Push-back is strict on the core questions (Q1, Q5, Q6, Q7b, Q8, Q11, Q14, Q17): keep challenging until the answer is specific or the user explicitly parks it as `TBC` with an owner and a date. On the others, at most two attempts, then record the concern under "Risks and open questions" and continue. If the user says "you decide" on a substantive question, follow the "never invent" rule in SKILL.md.

---

## A. Shape

**Q1. Event type.** (AskUserQuestion, one question.) Public hackathon (open) / Joint customer hackathon (closed) / Influencer hackathon (hybrid) / Challenge-based hackathon (verified through Liftoff). Once chosen, show the proposed defaults from `formats.md` for that type (registration target, budget band, length) in two lines and say they are proposals.
- Weak: "a hackathon", or a type that conflicts with the later answers.
- Push-back: "Those four lead to different invite lists, budgets, and prizes. Which is closest? If it is a mix, which one drives registration?"

**Q2. Partner.** Who is the partner, who is the named contact, and what does the partner bring (people, credits, venue, audience, money)?
- Good: a named company, a contact, and at least one concrete contribution.
- Weak: "a partner TBD", or a partner with no stated contribution.
- Push-back: "A partner who brings nothing but a logo costs us the joint-event effect. What are they putting in: budget, engineers, customers, a venue, credits? If you do not know yet, who can find out, and by when?" If no partner (Postman only), record that and skip partner funding questions.

**Q3. In-person or virtual.** (AskUserQuestion.) If in-person, ask the city. If virtual, ask whether it is a single live day or runs over several days, and which time zones matter.
- Weak: in-person with no city, virtual with no time zone plan.
- Push-back (in-person): "Where, and why there? Is that where the invitees are?" (virtual): "Which time zones are most of your invitees in? Live moments should fit them."

**Q4. Target month.** Month and year, and any fixed date.
- Weak: no month; a month with a known conflict (major holidays, a big industry event in the same city, the partner's own launch window).
- Push-back: name the conflict you know of. Work backward: "That gives about N weeks to plan. The plan needs about 8 to 10 weeks of lead time for a public event. Is that workable?"

## B. Purpose (before theme, prizes, and budget)

**Q5. Goals.** (Multi-select via AskUserQuestion, then follow-ups.) Badges earned / Discord community engagement / product activation / community-contributed extensions such as skills and mods / sales and opportunity influence.
For each selected goal, ask for a target number, who measures it, and by when. Sales influence needs: attendees from the target customer list, expansion opportunities influenced within 180 days, closed-won deals influenced within 180 days.
- Good: "200 badges issued during the event, from Liftoff stats", "40 attendees from the 120-account target list, 6 expansion opps in 180 days".
- Weak: no number; "awareness"; five goals with equal weight; a goal the event design cannot move.
- Push-back: "How will we know that goal worked? Give me a number and where it is read from." If more than three goals: "Which one wins when they conflict? Each goal changes the format and the prizes." If the sales goal has no target list: "Who is on the list, and who owns it?"

**Q6. Theme.** What is the hackathon about? Examples to offer if they have none: building AI agents for production, badge speed run, Claude mod extensions, CI/SDLC skills, skill templates for Postman.
- Good: one sentence a developer could repeat, tied to a product and a real workflow.
- Weak: "build anything with Postman", or a theme that could belong to any company.
- Push-back: "Could another company run this theme unchanged? What makes it about Postman and the partner's product? What should someone have built by the end that they could not build easily in an afternoon?" Also test fit: does the theme push toward the goals in Q5?

**Q7. Required technology and access.** What must teams use to take part (Claude Code plus the Postman plugin, an MCP server, Astropods, two services from a Fabric Gateway, Copilot, and so on)? Who provides access (workspaces, credits, sandbox, gateway), and when is it ready?
- Good: a short "you must use" list, an owner for each access item, and a ready date.
- Weak: "teams can use whatever"; access with no owner; nothing tested.
- Push-back: "Who creates the workspaces and credits, and has someone signed up with a fresh account to test the path? Early friction loses the best participants." For closed events, point out the enterprise concept in `formats.md` as an example of requiring technology.

**Q7b. Participant machines and setup.** Applies to every hackathon, in person or virtual. What do participants build on, and what must be true of their machines? Ask:
- Will they use their own laptops? Do they need admin rights to install the required tools (CLIs, plugins, runtimes)? Enterprise laptops are often locked down.
- Which operating systems must the starter kit support (macOS, Windows, Linux)?
- Network: can corporate networks reach the required services (gateway, registries, package hosts, API endpoints)? For in-person, is the venue Wi-Fi sized for the headcount, and is there a wired or backup option?
- Is there a hosted or cloud environment as an alternative to local install, and do the required tools work in it?
- How is the setup verified before the day (registration check, setup email, pre-event setup session, a "hello world" test)?
- What happens to a participant who fails the check (removed, lent a machine with a headcount and budget line, joins a team that is ready)?
- Who owns the setup communications and support?
- Good: a stated machine requirement, a pre-event verification step, a fallback for failures, and a named owner.
- Weak: "they will figure it out", a check with no fallback, or no owner.
- Push-back: "What does someone with a locked-down laptop do at 2 PM on the day? Setup problems in the first hour cost more than any other single failure. Who verifies setup before the event, and what is the fallback?" Strict: treat this as a core question.

## C. Audience

**Q8. Who is invited?** (AskUserQuestion.) Open to everyone / joint customers via sales outreach / influencer list from Common Room / mixed. For closed or mixed: who owns the invite list and when is it final?
- Weak: "developers"; a closed event with no list owner.
- Push-back: "How will those people actually hear about it? Who sends the invite, and by when?" If the model conflicts with the type chosen in Q1, say so.

**Q9. Personas and target companies.** Roles (platform engineers, API developers, AI engineers, architects), named target accounts or list source for closed events, and the skill level to plan for (first-time builders, experienced, mixed).
- Weak: "everyone"; no account list on a sales-driven goal.
- Push-back: "Pick the one persona you would be happiest to see 100 of. Mixed skill levels need a team formation plan; do you have one?"

**Q10. Registration size and screening.** Registration target, venue capacity, expected attendance, and what to capture at signup (skills, role, company, eligibility checks like "has a Postman account" or "has the required tool", the use case they will bring, machine admin-access confirmation from Q7b). Registration runs through Luma for every hackathon: the signup fields become Luma custom registration questions, and closed or invite-only events use guest approval so only people on the list are admitted. Ask whether the event uses approval (closed), open registration (public), or approval with a waitlist (hybrid), and who approves guests. Check the numbers against each other: required attendees divided by the show rate gives the registrations needed, and any "open the fallback" trigger must be counted on the same basis (registrations or confirmed attendees).
- Weak: a target that does not match the type; no no-show assumption; signup that collects only an email.
- Push-back: "Free events lose a lot of registrants. What attendance rate should I plan for? Without skills and company at signup, you cannot form teams or match the sales list." If the user has no no-show number, mark it `TBC`; do not supply one.

## D. Money and format

**Q11. Budget and who pays.** Show the type default as a proposal. Ask for the real budget, the Postman and partner split, and what is already committed.
- Weak: "whatever it takes"; a budget far outside the type band with no reason; no split with the partner.
- Push-back: "That is N times the usual band for this type. What is it buying that the band does not? Who pays what?" Compute cost per expected attendee and show it.

**Q12. Length, start time, and (in person) catering.** Show the type default. In-person assumes catering; ask about dietary needs, and alcohol only for an evening event.
- Weak: a short event with a large build ambition (Q6, Q7).
- Push-back: "Can a team build that in this time? What will they have at the end: a demo, a repo, a deployed agent?"

**Q13. Prizes.** Total value, who funds it, the form (cash, credits, hardware, project funding), and what each prize is awarded for. Show the type default.
- Good: a prize that fits the persona; for joint customers, a path to production with an executive sponsor.
- Weak: cash only for senior engineers or enterprise buyers; prizes with no link to the goals; unfunded.
- Push-back: "Does this prize matter to the persona in Q9? What would get a platform team to build something real? Consider a funded path to production, credits, or access." Public events: "Is the $10,000 floor funded, and by whom?"

## E. Quality and follow-through

**Q14. Judging.** Propose the default rubric from `formats.md`, adapted to the theme. Ask the user to confirm the 4 to 6 criteria and weights, and name the judges.
- Good: criteria that reward what the theme asks for, published before registration opens, at least one Postman judge, one partner judge, and one independent developer judge.
- Weak: "judges decide"; sponsors-only panel; criteria that do not match the theme.
- Push-back: "Vague criteria drive off the people you most want. Will these be on the registration page? Who is the judge with no stake in either company? A working demo should outscore an ambitious broken one; does the rubric say that?"

**Q15. Mentors and support.** How many Postman and partner engineers can attend, and who is the support route for virtual events (Discord channel, response hours)?
- Good: a mentor count at roughly 1 per 8 to 10 attendees in person, named people, and a mentor briefing.
- Weak: "the team will help"; no named support route.
- Push-back: "At N attendees you need about M mentors. Who exactly? Partner mentors tend to steer teams toward their own product; will they be briefed to help with the participant's goal?"

**Q16. Preparation for participants.** Will there be a starter kit, sample repo, setup guide, or pre-event workshop, and who builds it?
- Weak: nothing, or an owner of "TBD".
- Push-back: "Participants who arrive prepared build better projects. Can the starter kit and setup guide go out a week before, and who owns it?"

**Q17. After the event.** What happens to the best projects and the people who built them? (AskUserQuestion, multi-select.) Showcase and publish / community listing of skills or mods / funded continuation / sales and SE follow-up / nothing planned.
- Weak: "nothing planned" or "we will see". Most prototypes are abandoned without a path and an owner.
- Push-back: "What happens to the top five projects at day 30, and who owns that? Strong non-winners also vanish unless someone follows up within 48 hours. Who sends those notes?"

## F. Team

**Q18. Owners.** Event lead, sales liaison, partner lead, creative contact, venue and catering owner, and who runs Luma and Discord. Unknown is fine; it becomes a task with `TBC` as the owner.
- Push-back only if there is no event lead: "Someone has to own this. Who is it?"

**Q19. Anything else?** Constraints, past events to learn from, partner requirements, legal or approval needs.

---

When all questions are done, run the self-check in SKILL.md before writing.
