Here's the page converted to Markdown:

````markdown
# Language and Grammar

## Table of Contents

1. [Abbreviations](#abbreviations)
2. [Acronyms](#acronyms)
3. [Active Voice](#active-voice)
4. [Ampersand](#ampersand)
5. [Capitalization](#capitalization)
6. [Contractions](#contractions)
7. [Date](#date)
8. [Date and Time](#date-and-time)
9. [Ellipses](#ellipses)
10. [Entities (WIP)](#entities-wip)
11. [Exclamation marks](#exclamation-marks)
12. [File types](#file-types)
13. [Hyphens](#hyphens)
14. [Numbers](#numbers)
15. [Periods](#periods)
16. [Pronouns](#pronouns)
17. [Time](#time)
18. [Titles and Headers](#titles-and-headers)
19. [Units of Measurement](#units-of-measurement)
20. [Tense](#tense)

---

## Abbreviations

Avoid using abbreviations and write out the whole word even if doing so takes up more space.

- Better for localization — abbreviations don't translate very easily or very well
- Better for accessibility — a screenreader will often read out the individual letters of an abbreviation

---

## Acronyms

Avoid using acronyms and write out the phrase, unless the acronym is in common usage like "API."

- Acronyms are difficult to translate
- Acronyms sound technical and jargon-y and may be overwhelming to new users

---

## Active Voice

Use active voice in most cases and passive voice sparingly.

- Use active voice in most instances because it is clearer, shorter, and more conversational
- Passive voice can be used to soften bad news in cases where active voice comes across too harshly, such as "No results found" or "Your payment was declined."

---

## Ampersand

Avoid using ampersands and use "and" instead.

- Ampersands are less accessible and can't be picked up by screenreaders
- They also create difficulties with translation and localization

---

## Capitalization

### Sentence case

**What is it?** When the first letter of a sentence or phrase and proper nouns are capitalized.

**When to use it?** Postman uses sentence case in nearly all instances of its UI (exceptions noted below).

**Why?** Sentence case is easiest for users to read (the vast majority of the writing people encounter is written in sentence case).

### Title case

**What is it?** When major words are capitalized but minor words, such as "the" and "a," are lowercase. Check out [titlecase.com](https://titlecase.com/) to make sure you're title-casing correctly.

**When to use it?**

- Button labels — This is to help buttons stand out typographically from the rest of the content
- Branded terms
- Dedicated spaces — areas in the app that are dedicated to a specific function should be treated like proper nouns. These would include: Console Log, Collection Runner, Scratchpad, Bootcamp, API Network, Private API Network, Interceptor, etc.

**Why?** Avoid using title case in other instances because in addition to being more difficult to read, people also tend to associate it with formality, and overuse can cause stress by implying something is official when it's not.

### All caps

Avoid. All-caps writing is harder to read because the shape of the letters are less differentiated, which puts extra stress on people with reading/cognitive disabilities such as dyslexia.

If trying to emphasize a point, use bold instead. Using all-caps for emphasis feels shout-y, like we're yelling at the user.

---

## Contractions

Use contractions to keep the UI copy concise and conversational.

| Preferred | Avoid |
|-----------|-------|
| You won't be able to restore this collection from trash. | You will not be able to restore this collection from trash. |

---

## Date

See the [Date & Time spec](https://postmanlabs.atlassian.net/wiki/spaces/CD/pages/3118698991) for how to display dates and for information on when to use relative vs absolute date.

---

## Date and Time

See the [Date & Time spec](https://postmanlabs.atlassian.net/wiki/spaces/CD/pages/3118698991/Date+and+time+spec#Style-Guidelines) for how to display date and time and when to use relative vs absolute date and time.

---

## Ellipses

Ellipses (…) indicate an action is in process or to indicate truncation. Ellipses should always consist of:

- Three periods in a row
- No spaces between the periods
- No spaces between the ellipses and preceding or following text

---

## Entities (WIP)

When referring to entities, the entity name always precedes the entity type.

| Preferred | Avoid |
|-----------|-------|
| The Spotify Playlist collection | The collection Spotify Playlist |
| The Authentication API | The API authentication |

When the entity type is clear from context, you can leave it out and only use the entity name.

| Preferred | Avoid |
|-----------|-------|
| The Spotify Playlist collection was moved to My Workspace. | The Spotify Playlist collection was moved to the My Workspace workspace. |

---

## Exclamation marks

Use very, very sparingly. Overuse hurts the overall tone and makes the writing seem unprofessional. Unsure whether to use it still? Check out [this handy chart](https://cdn2.hubspot.net/hub/53/file-2378784241-jpg/Workflow2_b.jpg).

---

## File types

For acronyms, use all caps without a period: PDF, JPG, PNG, etc.

For all other file types, write out the full name.

---

## Hyphens

- Use to separate a range of numbers, for example: 500ms - 600ms
- Use for compound adjectives, for example: "API-first development strategy"

---

## Numbers

Use numerals, don't spell it out.

For numbers greater than 1,000 use a comma as a thousands separator. Do not put any space between the comma and the next number.

---

## Periods

Use only when there is a full sentence description.

**Do not take periods:**

- Headings
- Titles
- Labels
- Menu items
- Buttons

**Do take periods:**

- Complete sentences (has a subject and verb)
- Body text and descriptions
- Help text

---

## Pronouns

### Addressing developers

Think of the UI as a conversation between the system and the user. We address developers as "you." Using second-person maintains a consistent voice and promotes a friendly, conversational quality.

Use "I/My" only in instances where we want a developer to take particular ownership of an action, i.e. a checkbox with the label "I agree to the terms and conditions."

### Referring to Postman

Refer to Postman as "we" but avoid inserting Postman into the conversation as much as possible.

---

## Time

See the [Date & Time spec](https://postmanlabs.atlassian.net/wiki/spaces/CD/pages/3118698991) for how to display time and information on when to use relative vs absolute time.

---

## Titles and Headers

When possible, use headers in any standalone container, such as tooltip, toast, or card.

- Headings make content easier to scan, so adding them can reduce cognitive load.

Headings should:

- Highlight the most important concept or piece of information. Think of it as a newspaper headline — if someone only reads the heading they should get the basic idea of what happened.
- Help developers understand what they'll find in the section below
- Be concise, leaving out nonessential words to improve scannability
- Be sentence case
- Not be punctuated

See content patterns for: Error messages, success messages.

---

## Units of Measurement

There should be a space between the number and the unit, for example: 575 KB

- TB — Terabyte
- MB — Megabyte
- KB — kilobyte
- GB — Gigabyte

[Chicago Manual of Style](https://www.chicagomanualofstyle.org/book/ed17/part2/ch10/psec049.html) Exceptions: K (thousand), use '100K' and not '100 K'

---

## Tense

Write in the simple present or past tense. Avoid using present or past perfect tense (have/had).

| Preferred | Avoid |
|-----------|-------|
| Monitor created | Monitor has been created |
````