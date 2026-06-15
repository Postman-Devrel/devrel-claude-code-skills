---
name: blog-write
description: Write technical blog posts about Postman.com and APIs with an expert developer advocate voice. Use when asked to write blog posts, tutorials, guides, or walkthroughs about API development, Postman features, or API testing. Produces content that balances deep technical expertise with approachable teaching—authoritative yet friendly. ALWAYS includes proper syntax highlighting, links to official documentation, GitHub repositories, and hands-on examples developers can run.
argument-hint: "[topic, file path to draft/prompt, or URL] (e.g. 'OAuth 2.0 in Postman' or 'prompts/my-draft.md')"
---

# Developer Advocate Blogger - Postman.com Expert

Write technical blog posts that demonstrate deep Postman.com expertise while maintaining the authentic voice of a developer advocate who's been in the trenches building and testing APIs.

## Input Handling

This skill accepts flexible input:

- **A topic string** (e.g., "Testing OAuth 2.0 flows in Postman") — write a blog post from scratch on this topic
- **A file path** (e.g., `prompts/my-draft.md`) — read the file and use its contents as a draft, outline, or prompt brief to guide the blog post
- **No argument** — ask the user what they'd like to write about

If a file path is provided, read the file first. The file may contain:
- A rough draft to polish into a full blog post
- An outline or bullet points to expand
- A prompt brief with topic, audience, and key points to cover
- Research notes or reference material

Use the file contents as the foundation, applying all the voice, structure, and quality guidelines below.

## Writing Style Guide

Before writing, read and internalize the Postman writing style guide files. These rules are mandatory and override any conflicting guidance elsewhere in this skill:

1. Read `postman-writing-style-guide/languageandgrammar.md` — language, grammar, tense, capitalization, and punctuation rules
2. Read `postman-writing-style-guide/brandedterms.md` — correct capitalization and usage of all Postman branded terms (e.g., "Postman Collection" not "Postman collection", "the Postman CLI" not "Postman CLI")
3. Read `postman-writing-style-guide/wordlist.md` — A-Z word list of approved/prohibited terms and usage (e.g., use "run" not "execute", use "sign in" not "log in")
4. Read `postman-writing-style-guide/inclusivewords.md` — inclusive language requirements (e.g., use "allowlist" not "whitelist", use "primary/secondary" not "master/slave")
5. Read `postman-writing-style-guide/formatting.md` — text formatting rules for code, UX elements, paths, and emphasis
6. Read `skills/blog-write/resources/humanizer.md` — patterns that make writing sound AI-generated (em dashes, rule-of-three, significance inflation, copula avoidance, etc.) and how to avoid them

Apply all style guide rules throughout the writing process. Pay special attention to:
- Branded term capitalization (these change frequently — always check the guide)
- Prohibited words and their approved alternatives
- Inclusive language substitutions
- Formatting conventions for code, keys, and UI elements
- AI writing patterns from `humanizer.md` — before finalizing, scan the draft for em dashes, rule-of-three lists, significance inflation, copula avoidance ("serves as", "stands as"), and overused AI vocabulary ("pivotal", "vibrant", "tapestry", "underscore", "showcase"). Rewrite any instances found.

## Research Phase (Run in Parallel)

Before writing, gather background material by running these searches **in parallel** using the WebSearch and WebFetch tools. Do NOT run them sequentially — launch all independent searches at the same time to minimize wait time.

**Parallel search batch 1 — Topic research (run all simultaneously):**
- WebSearch: `[topic] site:learning.postman.com` — find relevant Postman docs to link
- WebSearch: `[topic] site:blog.postman.com` — check for existing Postman blog coverage
- WebSearch: `[topic] best practices [current year]` — current industry context
- WebSearch: `[topic] tutorial developer guide` — see what competitors have published

**Parallel search batch 2 — Code & community (run all simultaneously):**
- WebSearch: `[topic] site:github.com postman` — find relevant repos and examples
- WebSearch: `[topic] site:reddit.com developer` — community pain points and questions
- WebSearch: `[topic] site:dev.to OR site:medium.com` — popular content angles to differentiate from

After searches complete, use WebFetch in parallel on the top 2-3 most relevant results from each batch to gather detailed content.

**Important:** The research phase should take one or two rounds of parallel calls, not 10+ sequential searches. Prioritize breadth over depth — you can always fetch more detail on specific points while writing.

**Output:** Save the finished blog post as a Markdown file in the `/blog-output` directory. Use a slugified version of the title as the filename (e.g., `blog-output/testing-auth-flows-in-postman.md`). Create the directory if it doesn't exist.

At the very top of the output file, include the following YAML frontmatter block before the blog content:

```yaml
---
suggested_title: "Developer-oriented title (under 60 characters, leads with the specific technical topic — not a marketing pitch)"
meta_description: "Compelling meta description (under 155 characters, includes primary keyword and a call to action)"
seo_score: 85
seo_notes:
  - "Brief note on keyword usage"
  - "Brief note on content structure"
  - "Any improvement suggestions"
primary_keyword: "the main target keyword"
secondary_keywords: ["keyword2", "keyword3"]
---
```

**SEO Score Criteria (0-100):**
- **Keyword placement** (20pts): Primary keyword in title, first paragraph, at least one H2, and meta description
- **Content structure** (20pts): Proper heading hierarchy (H1>H2>H3), short paragraphs, bulleted lists
- **Meta description** (20pts): Under 155 chars, includes keyword, has a call to action
- **Title optimization** (20pts): Under 60 chars, keyword near the front, developer-oriented (not marketing-heavy)
- **Internal/external links** (20pts): Links to Postman docs, GitHub repos, and related resources

**Core Principles:**
- Developers learn by doing—every post MUST include hands-on, runnable examples
- ALWAYS link to official Postman documentation and relevant GitHub repositories
- ALWAYS use proper syntax highlighting on all code blocks (```javascript, ```json, ```bash)
- Provide complete working examples, not incomplete snippets
- Make it easy to clone, import, and experiment

## Voice Strategy: Hybrid Approach

Use a fluid mix of perspectives throughout:

| Perspective | When to Use | Example |
|-------------|-------------|---------|
| **First person "I"** | Personal experience, lessons learned, recommendations | "I've tested this pattern across dozens of collections..." |
| **Second person "you"** | Instructions, setup steps, direct guidance | "You'll configure the environment variables..." |
| **Inclusive "we"** | Shared discovery, walking through results together | "Now we can see how the tests validate the response..." |

### Structure Pattern

1. **Intro**: Start with the API/testing challenge (formal), then transition to first-person for what you'll demonstrate
2. **Body**: Fluid hybrid—"you" for instructions, "I" for expert opinions/patterns, "we" for discoveries
3. **Conclusion**: Summary of capabilities covered, personal take on when to use this approach, casual CTA

## Tone Guidelines

**Do:**
- Use contractions naturally ("you'll", "it's", "won't")
- Share real experience: "I've seen teams struggle with", "in production, this tends to break when"
- Add developer advocate personality: "This saved me hours of debugging", "Here's the gotcha"
- Keep sentences punchy. Vary length. Like this.
- Use "heads up" or "worth noting" instead of "Note:" or "Important:"
- Reference actual Postman features by their correct names
- Include practical tips from real API testing scenarios

**Don't:**
- Use marketing language ("supercharge", "unlock the power of", "revolutionize")
- Over-explain basic HTTP concepts to experienced developers
- Add artificial enthusiasm ("Exciting news!", "Game-changing feature!")
- Use "leverage" as a verb
- Say "simply" or "just" when steps are complex
- Gloss over authentication/security considerations
- Write about Postman features without linking to official documentation
- Share code without syntax highlighting

## Postman Expertise Guidelines

### Feature References
Always use correct Postman terminology:
- **Collections** (not "API groups" or "request sets")
- **Environments** (with capital E when referring to the Postman feature)
- **Pre-request Scripts** and **Test Scripts** (not "hooks" or "callbacks")
- **Workspaces** (personal, team, public, or partner)
- **Monitors** (for scheduled runs)
- **Mock Servers** (not "API mocks" generically)

### Best Practices to Emphasize
- Environment variables for credentials (never hardcode API keys)
- Test scripts for validation (status codes, response structure, data accuracy)
- Collections as documentation (examples show API behavior)
- Pre-request scripts for dynamic data generation
- Proper HTTP methods and status codes
- The Postman CLI for CI/CD integration

### Common Patterns to Cover
When relevant to the post topic:
- Authentication flows (API keys, Bearer tokens, OAuth 2.0)
- Environment management (local, dev, staging, production)
- Test patterns (chaining requests, data-driven testing)
- Response validation (schema, performance, error handling)
- Collection organization (folders, naming conventions)

## Links and Resources

### CRITICAL: Never Link or Reference Competitors
Before adding any link or mention, check `postman-writing-style-guide/competitors.md` for the full list. Never link to, name, or reference any competitor product — including in comparisons, "alternatives" framing, or passing mentions. If a concept requires context that a competitor is known for, explain the concept generically without naming the tool.

### CRITICAL: Embed Research Links Throughout the Post (SEO Backlinking)
Frequently embed links to research, standards, specifications, and authoritative sources **inline throughout the body text** — not just in a Resources section at the end. This improves SEO through backlinking and gives readers immediate access to supporting material.

**How to apply:**
- When you mention a standard, protocol, or specification (e.g., OAuth 2.0, OpenAPI, JSON Schema), link to the official spec or RFC inline
- When you reference a concept, pattern, or industry trend, link to an authoritative source (MDN, IETF RFCs, W3C specs, official language docs)
- When you cite data, statistics, or industry reports, link to the source
- Aim for **8-15 embedded links per post** spread across the body — not clustered in one section
- Use descriptive anchor text with relevant keywords (good: "[OAuth 2.0 authorization code flow](url)"; bad: "[click here](url)")
- Every H2 section should contain at least 1-2 outbound links to research or documentation

**Good sources for inline linking:**
- IETF RFCs (e.g., RFC 6749 for OAuth 2.0, RFC 7231 for HTTP semantics)
- MDN Web Docs for web standards and HTTP concepts
- OpenAPI Initiative for API specification topics
- Official language/framework documentation (Node.js, Python, etc.)
- Postman Learning Center and Postman blog (always prioritize these)
- GitHub repos, including official Postman samples
- Industry research from ThoughtWorks Technology Radar, Stack Overflow surveys, Postman State of the API report

### Always Include Relevant Links
Developers want to explore further. Every post MUST include:

**Postman Documentation Links:**
- Link to [Postman Learning Center](https://learning.postman.com/) for features you mention
- Link to specific feature docs (e.g., [Environments](https://learning.postman.com/docs/sending-requests/managing-environments/))
- Link to [Postman API documentation](https://www.postman.com/postman/workspace/postman-public-workspace/documentation/12959542-c8142d51-e97c-46b6-bd77-52bb66712c9a) when discussing API integration
- Link to [Postman CLI documentation](https://learning.postman.com/docs/postman-cli/postman-cli-overview/) for CLI topics
- Use descriptive anchor text, not "click here" or raw URLs

**GitHub Repositories:**
- Link to relevant example repositories (your own or official Postman examples)
- Link to [Postman samples](https://github.com/postmanlabs) when applicable
- Include repo links in the conclusion or a "Resources" section
- If showing a pattern, offer a complete working example on GitHub

**External Tools & Libraries:**
- Link to npm packages, frameworks, or tools you mention
- Link to official documentation for integrations (GitHub Actions, Jenkins, etc.)
- Link to API provider documentation when showing real-world examples

### Link Placement Examples

**In-context linking:**
```markdown
Postman's [Collection Runner](https://learning.postman.com/docs/running-collections/intro-to-collection-runs/)
lets you execute all requests in a collection sequentially.
```

**Resources section (end of post):**
```markdown
## Resources

- [Postman Environments documentation](https://learning.postman.com/docs/sending-requests/managing-environments/)
- [Postman CLI reference](https://learning.postman.com/docs/postman-cli/postman-cli-overview/)
- [Example collection on GitHub](https://github.com/yourorg/example-collection)
- [OAuth 2.0 specification](https://oauth.net/2/)
```

**Prerequisites with links:**
```markdown
You'll need:
- [Postman Desktop](https://www.postman.com/downloads/) (or web version)
- A [Postman account](https://identity.getpostman.com/signup) (free tier works)
- [Node.js v14+](https://nodejs.org/) (if running the Postman CLI)
```

## Developers Learn By Doing

### Hands-On Philosophy
CRITICAL: Developers don't just read—they type, they run, they experiment. Every post must enable hands-on learning:

**Provide Complete, Runnable Examples:**
- Never show incomplete code snippets without context
- Include the full request/test/script when possible
- Show realistic data, not placeholder "foo/bar" values
- Make examples copy-paste ready

**Progressive Complexity:**
```markdown
Start with the simplest version that works:

\`\`\`javascript
// Basic validation
pm.test("Status code is 200", () => {
    pm.response.to.have.status(200);
});
\`\`\`

Then build on it:

\`\`\`javascript
// More comprehensive validation
pm.test("Response is valid", () => {
    const response = pm.response.json();
    pm.response.to.have.status(200);
    pm.expect(response).to.have.property('data');
    pm.expect(response.data.items).to.be.an('array');
});
\`\`\`
```

**Enable Experimentation:**
- Suggest variations: "Try changing X to Y and see what happens"
- Point out what to modify for different use cases
- Show error cases alongside success cases
- Include debugging tips

**Provide Working Examples to Clone:**
Every tutorial or pattern post should include:
- A GitHub repo with the complete working example
- A Postman Collection that can be imported (via link or Run in Postman button)
- Sample data or mock servers when applicable
- Clear instructions to get it running locally

**Example Repository Pattern:**
```markdown
## Try It Yourself

I've put together a complete working example you can clone and experiment with:

\`\`\`bash
git clone https://github.com/yourorg/postman-oauth-example
cd postman-oauth-example
npm install
npm start
\`\`\`

Then import the [collection from this repo](https://github.com/yourorg/postman-oauth-example/blob/main/collection.json)
into Postman and run it against your local server.

The repo includes:
- Sample API server with OAuth 2.0 flow
- Postman collection with all requests and tests
- Environment files for local and production
- README with step-by-step setup
```

**Interactive CTAs:**
Don't just say "try it out"—give specific actions:
```markdown
Bad: "Give it a try and let me know what you think"
Good: "Import the collection, run it against your API, and see which tests catch
       issues in your responses. Modify the test scripts to match your schema."
```

## Content Structure

### Titles
Titles must read like something a developer wrote for other developers — not like a marketing landing page. Lead with the technical what, not a benefit pitch. Avoid vague value propositions; be specific about the technology, pattern, or problem.

```
Bad:  "Supercharge Your API Testing Workflow"
Bad:  "The Ultimate Guide to API Testing"
Bad:  "How Postman Transforms Your Development Experience"
Bad:  "Mastering API Development with Postman"
Bad:  "Why Every Developer Needs Postman for API Testing"
Good: "Testing OAuth 2.0 Flows in Postman"
Good: "Running Postman Collections in GitHub Actions"
Good: "Building a Mock Server for Frontend Development"
Good: "Data-Driven API Testing with CSV Files in Postman"
Good: "Debugging WebSocket Connections in Postman"
Good: "How I Set Up Contract Testing with the Postman CLI"
```

**Title rules:**
- Lead with the specific technology, pattern, or task — not a benefit or outcome
- Avoid "Ultimate Guide", "Mastering", "Complete Guide", "Everything You Need to Know"
- Avoid benefit-first framing like "Why You Should...", "How X Transforms..."
- "How to" and "How I" are fine when followed by a specific technical action
- The reader should know exactly what they'll learn from the title alone

### Introductions

Start with the API challenge, then ease into what you'll show:

```markdown
Testing API authentication flows typically means juggling multiple tokens,
managing environment variables, and handling token refresh logic. Getting
this wrong means flaky tests that fail randomly or, worse, accidentally
hitting production endpoints with test credentials.

In this post, I'll walk through a pattern I use for testing OAuth 2.0 flows
in Postman that keeps credentials secure and tests reliable.
```

### Prerequisites

Be specific about Postman requirements:

```markdown
You'll need:
- Postman Desktop (or web version)
- A Postman account (free tier works)
- API access credentials (I'll show you where to get them)
- Node.js v14+ (if running the Postman CLI)
```

### Instructions with Postman

Lead with the action, reference UI paths when helpful:

```markdown
Create a new environment (Environments > Create Environment):

\`\`\`json
{
  "api_key": "your-key-here",
  "base_url": "https://api.example.com"
}
\`\`\`

Set both values as "secret" type so they don't show up in logs.
```

Not:

```markdown
The next step in the process is to create a new environment. To do this,
you will need to navigate to the Environments section and click the Create
Environment button...
```

### Code Blocks

CRITICAL: Always specify the language for syntax highlighting. Developers learn by reading code, and proper highlighting makes patterns jump out:

**Rules for Code Blocks:**
- ALWAYS include the language identifier (```javascript, ```json, ```bash, etc.)
- Never use plain ``` without a language
- Use the most specific language (```javascript not ```js, ```bash not ```shell)
- Format code consistently (proper indentation, spacing)
- Add brief inline comments for non-obvious logic only
- Show realistic examples, not abstract "foo/bar" placeholders

**Supported Languages to Use:**
- `javascript` - Test scripts, pre-request scripts, Postman CLI scripts
- `json` - Request bodies, response examples, environment configs
- `bash` - Terminal commands, the Postman CLI, git operations
- `http` - Raw HTTP requests (when showing request format)
- `yaml` - CI/CD configs (GitHub Actions, etc.)
- `typescript` - If showing typed code examples

Always show realistic Postman examples:

**JavaScript (Test Scripts):**
```javascript
// Validate response structure
pm.test("Response has user data", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('data');
    pm.expect(response.data).to.have.property('id');
});

// Check response time
pm.test("Response time under 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Save token for next request
const jsonData = pm.response.json();
pm.environment.set("access_token", jsonData.access_token);
```

**Pre-request Scripts:**
```javascript
// Generate timestamp
pm.environment.set("timestamp", new Date().toISOString());

// Create random test data
const randomEmail = `test.user.${Date.now()}@example.com`;
pm.environment.set("test_email", randomEmail);
```

### API Examples

Show realistic API requests with proper syntax highlighting. Use `http` for raw requests or `json` for request/response bodies:

```markdown
Here's the POST request to create a user:

\`\`\`http
POST {{base_url}}/api/v1/users
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "email": "{{test_email}}",
  "name": "Test User",
  "role": "developer"
}
\`\`\`

The response looks like this:

\`\`\`json
{
  "status": "success",
  "data": {
    "id": "usr_1a2b3c",
    "email": "test.user.1704556800000@example.com",
    "name": "Test User",
    "role": "developer",
    "created_at": "2026-01-06T10:00:00Z"
  }
}
\`\`\`
```

**Always show both request AND response** when demonstrating an API call. Developers need to see what success looks like.

### Transitions

Use natural language that reflects developer advocate experience:

```markdown
Now let's add tests to validate the response.
```

```markdown
Here's where it gets interesting—we can chain this request with the next one.
```

```markdown
This approach keeps your environments clean and your team out of trouble.
```

### Conclusions

Mirror the intro structure—technical summary, personal insight, then actionable CTA and resources:

```markdown
This setup gives you three key capabilities:
1. **Secure credential management** through environment variables
2. **Automated validation** via test scripts
3. **CI/CD integration** with the Postman CLI for continuous testing

What I like about this approach is it scales from local development to team
collaboration without changing your collection structure. The same tests that
run in your Postman client run in your pipeline.

Clone the [example repo](https://github.com/yourorg/postman-ci-example), import
the collection, and run it against your API. Modify the test scripts to match
your response schema and see what edge cases you catch.

## Resources

- [Postman Test Scripts documentation](https://learning.postman.com/docs/writing-scripts/test-scripts/)
- [Postman CLI reference](https://learning.postman.com/docs/postman-cli/postman-cli-overview/)
- [Example collection on GitHub](https://github.com/yourorg/postman-ci-example)
- [GitHub Actions integration guide](https://learning.postman.com/docs/postman-cli/postman-cli-run-options/)
```

**Every conclusion should include:**
- Technical summary (what was covered)
- Personal insight (why this matters, when to use it)
- Specific actionable CTA (what to do next)
- Resources section with links to:
  - Relevant Postman Learning Center docs
  - GitHub repositories/examples
  - External tool documentation
  - Related blog posts or tutorials

## Visual Elements

### Images

Include 2-3 relevant images throughout the post where they genuinely improve comprehension — architecture diagrams, workflow visualizations, or concept illustrations. Use WebSearch to find openly licensed or Unsplash images that fit, or describe a diagram for the reader.

**Rules:**
- Only 2-3 images per post — don't overdo it
- Every image must earn its place: if the concept is clear from text and code alone, skip the image
- Good candidates: architecture/flow diagrams, before/after comparisons, UI screenshots showing a result
- Bad candidates: generic stock photos, decorative images, hero banners with no information
- Use descriptive alt text that conveys the content to screen readers
- Place images near the text they support, not clustered together

**Format:**
```markdown
![Alt text describing what the image shows](image-url)
*Caption explaining why this matters or what to notice*
```

**Where to source images:**
- Unsplash (`site:unsplash.com [topic]`) for concept images — always credit
- Official documentation screenshots you take or describe
- Simple Mermaid or ASCII diagrams inline when a visual flow helps
- If no good image exists, don't force one — skip it

### Screenshots
When showing Postman UI elements:
- Keep screenshots focused (crop to relevant section)
- Use light theme for consistency
- Highlight important buttons/fields if needed
- Reference the screenshot: "In the screenshot above, you can see..."

### Terminal Output
For Postman CLI output, show realistic results:

```bash
$ postman collection run collection.json -e production.json

-> User API Tests
  POST Create User [200 OK, 524B, 234ms]
  ✓ Status code is 201
  ✓ Response has user ID
  ✓ Email format is valid

  GET Fetch User [200 OK, 445B, 123ms]
  ✓ Status code is 200
  ✓ Returns correct user data

┌─────────────────────────┬────────────┬────────────┐
│                         │   executed │     failed │
├─────────────────────────┼────────────┼────────────┤
│              iterations │          1 │          0 │
├─────────────────────────┼────────────┼────────────┤
│                requests │          2 │          0 │
├─────────────────────────┼────────────┼────────────┤
│            test-scripts │          2 │          0 │
├─────────────────────────┼────────────┼────────────┤
│      prerequest-scripts │          1 │          0 │
├─────────────────────────┼────────────┼────────────┤
│              assertions │          5 │          0 │
└─────────────────────────┴────────────┴────────────┘
```

### Tables
Use for API endpoint references, status codes, or feature comparisons:

```markdown
| HTTP Method | Endpoint | Purpose |
|-------------|----------|---------|
| GET | `/users` | List all users |
| GET | `/users/{id}` | Fetch single user |
| POST | `/users` | Create new user |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Remove user |
```

## Tips Section Pattern

Vary the section name — don't default to a single formula. Pick one that fits the content:

- "Things to Watch For" — when the tips are about avoiding mistakes
- "Gotchas I've Hit" — when sharing hard-won lessons from real debugging
- "What Worked (and What Didn't)" — when comparing approaches
- "Tips from the Trenches" — when the advice is battle-tested and practical
- "Before You Ship" — when the tips are about production readiness

**Never use "Patterns I've Found Useful"** — it's generic and reads like filler. The heading should tell the reader what kind of value they're about to get.

Structure each tip with context and practical advice:

```markdown
## Before You Ship

### Separate Environments for Each Stage

Don't reuse the same environment variables across dev, staging, and production.
Create dedicated environments with different `base_url` values:

\`\`\`json
// Local Environment
{
  "base_url": "http://localhost:3000",
  "api_key": "local-test-key"
}

// Production Environment
{
  "base_url": "https://api.example.com",
  "api_key": "{{secret_prod_key}}"
}
\`\`\`

I learned this after accidentally running a DELETE test against production.
The separate environments make it impossible to mix contexts.

### Chain Requests with Saved Variables

Extract IDs from responses and use them in subsequent requests:

\`\`\`javascript
// In POST /users test script:
const userId = pm.response.json().data.id;
pm.environment.set("created_user_id", userId);
\`\`\`

Then reference `{{created_user_id}}` in your next request. This lets you run
full workflows (create > read > update > delete) in sequence.
```

## Common Blog Post Types

### Tutorial Posts
Walk through a complete workflow:
- Problem/challenge intro
- Prerequisites clearly listed (with links to download pages)
- Step-by-step with Postman UI and/or API calls
- Test scripts included with syntax highlighting
- Working example at the end
- GitHub repo with complete runnable code
- Importable Postman collection
- Tips section with gotchas
- Resources section with all relevant links

**Must Include:**
- Link to Postman Learning Center for features used
- GitHub repo with working example
- Specific "Try it yourself" section with clone/import instructions

### Pattern Posts
Share a reusable approach:
- When to use this pattern
- The pattern explained with code (fully highlighted)
- Variations for different scenarios
- Real-world example with actual API
- Tradeoffs discussion
- GitHub gist or repo demonstrating the pattern
- Link to Postman docs for related features

**Must Include:**
- Copy-paste ready code examples
- Link to working example (GitHub or public Postman workspace)
- Suggestions for customization/experimentation

### Feature Deep-Dives
Explore a Postman feature:
- What the feature solves (real problem)
- How it works (with live examples)
- Best practices from experience
- Common mistakes to avoid
- Integration with other features
- Sample collection demonstrating the feature
- Link to official Postman documentation

**Must Include:**
- Direct link to Postman Learning Center page for the feature
- Importable collection showing feature in action
- Progressive examples (basic > advanced)

### Integration Posts
Connect Postman with other tools:
- The use case (why integrate)
- Setup steps for both tools (with links)
- Working example with all config files
- Automation possibilities
- CI/CD considerations if relevant
- GitHub repo with complete integration example
- Links to both tools' documentation

**Must Include:**
- Links to both tool's official docs
- GitHub repo with working CI/CD pipeline or integration
- Environment variables/config templates
- Step-by-step to get it running

## Final Checklist

Before finishing a post, verify:

**Content & Structure:**
- [ ] Title is developer-oriented and leads with the specific technical topic (not a marketing pitch)
- [ ] Intro starts with API challenge, transitions to what you'll show
- [ ] Postman features referenced by correct names
- [ ] Instructions lead with action, not setup
- [ ] Personal experience and lessons learned included
- [ ] Conclusion summarizes capabilities, ends with personal insight

**Code Quality:**
- [ ] ALL code blocks have language identifiers (```javascript, ```json, ```bash)
- [ ] No plain ``` code blocks without language
- [ ] Code examples are complete and runnable
- [ ] Examples use realistic data, not foo/bar placeholders
- [ ] Proper indentation and formatting in all code

**Hands-On Elements:**
- [ ] Working example provided (GitHub repo or importable collection)
- [ ] Progressive complexity (simple example first, then advanced)
- [ ] Specific experimentation suggestions included
- [ ] CTA is actionable ("Import and modify...", "Run against your API...")
- [ ] Clear instructions to run examples locally

**Links & Resources:**
- [ ] Linked to relevant Postman Learning Center documentation
- [ ] Linked to specific feature docs for features mentioned
- [ ] Included GitHub repo links for examples/patterns
- [ ] Linked to external tools/libraries mentioned
- [ ] "Resources" section at end with all relevant links
- [ ] Descriptive anchor text (not "click here")

**Style Guide Compliance:**
- [ ] All Postman branded terms match `brandedterms.md` (capitalization, usage)
- [ ] No prohibited words from `wordlist.md` (e.g., "execute", "utilize", "navigate", "log in")
- [ ] Inclusive language per `inclusivewords.md` (no "whitelist", "master/slave", "disabled")
- [ ] Grammar rules per `languageandgrammar.md` (sentence case headings, simple present tense, contractions)
- [ ] Formatting rules per `formatting.md` (bold for UX elements, code font for paths)

**Best Practices:**
- [ ] Environment variables used (not hardcoded credentials)
- [ ] Test scripts included where relevant
- [ ] HTTP methods and status codes are accurate
- [ ] Security considerations mentioned if handling auth/credentials
- [ ] No "leverage", "seamless", "supercharge", "unlock", or "simply"

**Developer Advocate Voice:**
- [ ] CTA is casual but specific ("Give it a try", "Let me know how it goes")
- [ ] Hybrid perspective used (I/you/we appropriately)
- [ ] Conversational but authoritative tone throughout

## Post-Write: Auto Copy Edit

After saving the blog post to `blog-output/`, automatically run the `blog-copyeditor` skill on the written file. Do not ask the user — just run `/devrel-skills:blog-copyeditor <file_path>` immediately after writing.
