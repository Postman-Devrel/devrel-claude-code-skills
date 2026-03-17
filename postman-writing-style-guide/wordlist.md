Here's the page converted to Markdown:

````markdown
# A-Z word list

This is a dictionary of terms and usage we follow. Also see [Term collections](#) for lists of terms specific to certain scenarios.

---

## A

**abort** — Don't use. Alternative terms are end, close, stop, or cancel. See [Abort, Abortion - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/abort)

**above, below** — Avoid using when referring to other sections of text, such as "in the instructions below." An alternative is earlier/following. See [Write accessible documentation | Google developer documentation style guide](https://developers.google.com/style/accessible-documentation)

**accessible** — Only use when describing interactions that are easy for everyone to use. Don't use to refer to things that are available, such as items with visibility controlled by RBAC.

**against** — Don't use when referring to running on a platform or operating system. Use on instead. See [Against - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/against)

**Agent Mode** — Branded term; use Postman Agent Mode on first occurrence. The following terms apply:
- AI credits — Use Postman AI credits instead of Agent Mode credits.
- Postman AI add-on — (Not Agent Mode add-on)
- Pay-as-you-go — (never pay-as-you-go pricing, pay-as-you-go-billing — it's a standalone term)
- Avoid using overages. Instead, use pay-as-you-go.
- Use Postman AI when referring to Postman's AI features in general.
- Use Agent Mode when describing specific AI features.

**agnostic** — Don't use. Use platform-independent.

**AI** — All uppercase. Use the following terms for AI components within Postman:
- AI Request block — like other Flows blocks
- AI request
- AI agent
- AI model
- AI model provider
- AI-generated — Hyphenate.

**allow** — Avoid using to describe things that Postman makes possible for the user. (Also avoid using enable or let for the same purpose.) Allow can be used in a security or role context. See [Allow, Allows - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/allow)

**and/or** — Don't use. You can typically use or. See [And/Or - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/and-or)

**API** — All uppercase.

**API definition** — Deprecated; don't use. Use API specification instead. Use the term API definition instead of API specification, API spec, or API schema. This is based on the feature Multi-file API Definition.

**API error codes** — API error code descriptions should be Title Case instead of ALL CAPS and not use code format, such as 404 Not Found and 500 Internal Server Error.

**API-first** — "first" is lowercase.

**API methods** — API methods (also known as HTTP methods or REST methods) are all-caps and unstyled, such as GET, POST, or DELETE. You can bold items when referring to them in the dropdown list in the request builder.

**Apple silicon** — When referring to Mac's M1/M2 System on a Chip, use Apple silicon. If referring specifically to the M1 or M2, use M1 chip or M2 chip.

**API specification** — Use the term API specification instead of API definition. Subsequent uses can use specification. Don't use spec. Deprecation notes:
- Starting with the release of Spec Hub in FY2026 Q1, this supersedes the previous use of API definition instead of API specification.
- Existing API Builder docs can continue to use the term API definition.
- In cases where API Builder API definitions and Spec Hub API specifications are used in the same place, you can use API specification to refer to both.

**ARM** — Capitalized. Use ARM64 (no space or hyphen) to refer to the 64-bit variant.

**Artemis** — Don't use in user-facing documentation.

**author** — Don't use as a verb. Use write instead. Use writer as a noun when referring to people who write documentation and style guides.

---

## B

**black-box testing** — Don't use. Use opaque-box testing or specification-based testing.

**blacklist** — Don't use. Use blocklist.

**bold** — See Text formatting.

**Boolean** — Always capitalize, unless it's code that is specifically lowercase. (Example: OpenAPI data types are all lowercase.) See [Boolean - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/b/boolean)

**bottom bar** — The expanding/collapsing area that contains the console and terminal.

**branded terms** — See Branded Terms.

**button** — When including inline buttons in Postman Docs content, use the following format: `[button-img] button-name`. When the button has a label, use it for button-name. If it doesn't, use the hover text. If it doesn't have either, come up with something sensible based on the button filename. Exception: for the + button, just use + for the button-name.
- Use bold format for the button name.
- Use the same capitalization as the button name.
- Avoid using the word "button" if you can clearly refer to it by its label. Don't use "icon."
- If the button name gets truncated to a shorter form when the UI is at a reduced width, use the full name.
- If there's a choice in Aether between a small and large button, use the large one. (Exception: the trash button.)
- See [button - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/b/button)

**bulleted lists** — See lists.

**BYOK** — The feature name is BYOK Encryption. For first use in a doc, use Bring Your Own Key (BYOK) Encryption. For subsequent uses in a doc, use BYOK.

---

## C

**capitalization** — See Capitalization.

**carry out** — Use perform, run, or complete instead.

**checkbox** — Don't use check box or box. Use select and clear to describe interacting with a checkbox. See [check, checkbox, check mark - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/c/check-box)

**choose** — See click.

**click** — Use click when referring to the act of pressing a mouse button when the mouse cursor is over a button, link, icon, menu item, or other UX control. Don't use select.
- You can use click even if the user is using a touchpad, touchscreen, or alternative input device.
- Use single-click or right-click as a verb when describing that specific interaction.
- Don't use click on.
- Use select when referring to picking a checkbox, radio button, or dropdown list item. You can also use select when referring to the action of clicking and dragging over text.
- Use choose to loosely describe decisions a user has to make, possibly outside of the UI. For example, "Choose a source control provider, such as GitHub or GitLab."
- In multi-select situations (you can do something on one or more requests in a collection) you select the items, but you can describe that you click each item.
- You press physical keys.

**command-line** — Hyphenated when used as an adjective. For example, Newman is a command-line tool. Not hyphenated when used as a noun ("enter your commands on a command line"). Don't use CLI. One exception: the Postman CLI is a branded term and can be used, but don't use the term CLI to refer to it; always use the Postman CLI. See [command line, command-line - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/c/command-line)

**commas** — Use serial commas, aka Oxford commas. ("This, that, and the other.")

**Connector blocks** — Flows has a block type called Connector blocks. Connector is capitalized. Each Connector block is specific to a third-party service like Figma or Calendly and the service name appears as the block title. Bold Connector when referring to a block.
- To refer to a specific Connector block in a flow, qualify it like "the Figma Connector block" (only bold Connector).
- "Connections" are the wires that connect blocks to each other. Connector blocks have connected services, not connections.
- The services are "third-party services" or just "services" (not apps). Note the hyphen in "third-party"; this is consistent with MS and Apple style guides.

**continuous integration and continuous delivery (CI/CD)** — Don't use continuous integration (CI) and continuous delivery (CD).

**contractions** — Use them. An exception is if you're issuing a warning. ("You will not be able to undo this.") See [Use contractions - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/word-choice/use-contractions)

**cookbook** — In Postman Docs, for first use/title, use Postman \<n\> Cookbook, and subsequently use cookbook. (A cookbook contains recipes.)

**crash** — Don't use. Use stop responding for UI interaction, or fail for things like CI runs or scripts. See [crash - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/c/crash)

**cross-origin resource sharing (CORS)** — Spell out with CORS in parenthesis on first use, then use CORS. It's origin and not object, and it is hyphenated.

**curl** — The software project itself is named cURL, but the program and library are named curl. In general, unless specifically defining the name of the project, use curl. An exception is that the term cURL is used incorrectly in the Postman UX, and you may need to write around that.

---

## D

**dashes** — Avoid using em-dashes for parenthetical remarks within sentences. Consider rewriting the sentence for simplicity. When using an em-dash or en-dash in Markdown in Postman Docs, use `---` or `--` and it will render as an HTML entity on build.

**data** — Both singular and plural. Don't use datum for plural. Always use with a singular verb. Don't use "the data are." See [data, datum - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/d/data)

**definitions** — Use italics for the first introduction on a page. ("A faucet is a valve controlling the release of a liquid or gas.") See [Formatting common text elements - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/text-formatting/formatting-common-text-elements)

**developers** — Avoid, except in specific context. Use users instead. Use developer when necessary to refer to the subset of users who design APIs or write code scripts.

**dialog** — Use dialog when needed, but since focus moves to the dialog and a user can't do anything out of it, you seldom need it. An exception is any interaction with the OS or a third-party UI.
- Things are in and not on dialogs.
- Titles are sentence case, even if the UX is in all caps.
- Don't use modal or dialog box.
- See [dialog box, dialog, dialogue - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/d/dialog-box)

**directional information** — Avoid using direction in descriptions unless necessary. Use icons inline in sentences to show what you mean.

**disable, disabled** — Don't use. Use turn off, deselect, inactive, unavailable, deactivated. When referring to the opposite state, use turn on/off, select/deselect, active/inactive, available/unavailable, or activate/deactivate.

**discriminator, discrimination** — Don't use. Use condition, property, or test.

**domain names** — Any domain in an example URL that isn't owned by Postman needs to be example.com or one of its subdomains.

**dropdown list** — Avoid talking about UI items, but when needed, use dropdown list. Don't use dropdown menu or use dropdown as a noun. See [dropdown - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/d/dropdown)

**Dummy** — Use sample, example, or inert.

**dynamic CTA placeholders** — When referring to a CTA that uses a dynamic name, such as "Run \<collection name\>", use a lowercase placeholder in italics. For example: Run *collection name*.

---

## E

**easy** — Avoid.

**eg** — Use for example instead.

**element** — Requests, collections, APIs, environments, monitors, mock servers, and workspaces are collectively and generically called elements. Don't use entities, unless it's required to write around the UI.

**em-dash, en-dash** — See dashes.

**enable** — Avoid using when you mean turn on, select, or give the ability to. See also disable.

**end user** — Not hyphenated. Avoid in documentation, and simply use user instead.

**enter** — Don't use type when instructing someone to enter a value. See [Describing interactions with UI - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/procedures-instructions/describing-interactions-with-ui). To describe the key, use "Return or Enter." See keys and shortcuts.

**entity** — Don't use. See element.

**etc** — Don't use. Also avoid and so on, and consider making the sentence more specific instead.

**execute** — Don't use. Use run instead. See [execute - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/e/execute)

**expiry** — Use expiration instead.

---

## F

**file types** — Use the formal name of the type and not the filename extension to refer to the file type. For example, use zip file (all lowercase, no code style). Do not use Zip file, ZIP file, or .zip file. See [Filenames and file types | Google developer documentation style guide](https://developers.google.com/style/filenames)

**first person** — Avoid using first person in core docs ("let's" and "we").

**foo, bar, fubar, foobar** — Don't use. Either use "example" or "sample," or if you need more than a few placeholders, use the Greek alphabet or phonetic alphabet.

**footer** — The bottom of the Postman app. Don't use status bar. Don't use when referring to the bottom bar.

**free plan** — Use to describe Postman's unpaid plan.

**frequently asked questions** — Don't hyphenate frequently-asked.

---

## G

**Gerunds** — (Verbs used as nouns, or words ending in -ing.) Don't use in headings. For example, it's Get started, not Getting started. See Headings in Postman Docs.

**Git** — Capitalized unless specifically referring to the command.

**globals, global variables** — Use global variable or global variables to refer to one or multiple global variables. Use globals to refer to all global variables. Note that unlike environments or collections, there isn't a proper name for the container that holds global variables.

**grayed out** — Don't use. Use unavailable, or turned off. See [gray, grayed out - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/g/grayed-out)

---

## H

**hang** — Don't use. Use stop responding, stop, close.

**hard-code, hardcode, hard code** — Use "hard code" for verbs or nouns, "hard-code" for adjectives. Write around this when a more specific meaning is appropriate, like static, predefined, or read-only.

**header** — The top of the Postman app. Don't use menu bar.

**headings** — See Headings in Postman Docs.

---

## I

**ID** — Avoid using ID alone. Use collection ID or user ID instead. Also don't use id in lowercase unless it's in code.

**icon** — Unless you're talking about an app's icon, you probably mean button. (See above.)

**identity provider (IdP)** — Spell out first mention in lowercase with IdP in parenthesis, then use IdP for subsequent uses.

**inclusive language** — See Inclusive Language.

**invite** — Can be used as a noun or a verb. You can use invitation for the noun if it's needed for clarification.

**italics** — See Text formatting.

---

## J

**JSR** — The JavaScript Registry. All caps. Note that npm is all lowercase, and it does look unusual to say "npm and JSR," but that's the correct usage.

**just** — Avoid.

---

## K

**keys and shortcuts** — Follow [Describing interactions with UI - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/procedures-instructions/describing-interactions-with-ui) and the [keys and keyboard shortcuts term collection](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/term-collections/keys-keyboard-shortcuts).
- You press keys, not select, click, or hit.
- Shortcuts should use plus between them, not minus. Don't include spaces before or after the +.
- Special keys include:
  - Ctrl and Alt for Windows and Linux
  - Command and Option for Mac. (Not Cmd.) Microsoft recommends using the symbol ⌘ instead of "Command."
  - Control for Mac (this is a different key than Ctrl for Windows.)
  - Shift
  - Return and Enter — It's Return on the Mac and Enter on PC, so use "Return or Enter."
  - Esc
- Key names are not all caps. Key names are bold.
- Spell out the Mac shortcut, then the Windows/Linux shortcut. Don't use Ctrl/Cmd.
- Example: To open the console, select **Command+Option+C** or **Ctrl+Alt+C**.
- We don't document inline every keyboard shortcut. Only important or notable keyboard shortcuts are documented.

**kill** — Avoid.

**know** — Avoid using informally, such as "Now that you know how to create requests, add them to a collection." (We don't know what they know.) Use "To learn more about…" or "For more information…"

---

## L

**launch** — Avoid. Use open instead.

**left sidebar** — See sidebar.

**let's** — Avoid in Postman Docs.

**lists** — Use them, especially in procedures.
- Numbered lists denote a set of steps to follow. Don't number a list of unordered items.
- If a bulleted list has a mix of complete and incomplete sentences, all sentences end in a period.
- For definition lists, use dashes instead of colons to separate terms from definitions. Don't use tables for simple definition lists in Postman Docs.
- When introducing lists, the sentence that appears before the list (before the colon) should be a complete sentence.
- See Procedures for more guidance on procedure lists.

**log in, log out** — Use sign in and sign out.

---

## M

**master, slave** — Don't use. Use primary/secondary, or main/branch.

**MCP** — Use the following terms:
- Model Context Protocol (MCP)
- MCP client
- MCP server
- MCP host
- MCP request
- Server-sent events (SSE)
- Streamable HTTP (Preferred over SSE)

**member** — Don't use. Use user instead, unless referring to the users in a Postman team, which are team members.

**menu** — Don't use. Write around it. ("Select Workspaces in the header…")

**menu bar** — The menu at the very top of your screen. You can also use "your computer's menu bar" if needed. This can be used instead of taskbar on Windows computers when referring to where the Postman app icon is shown.

**metaphors** — Be careful when using metaphors or choosing examples. These don't always translate across different cultures and languages.

**might** — Avoid using informally, like "You might want to add an example." Use "To learn more about…" or "For more information…"

**modal** — See dialog.

---

## N

**navigate** — Avoid. Instead, use go to, to describe going directly to a webpage or website, whether by entering a URL or selecting a link.

**normal** — Use expected, typical.

**npm** — Always lowercase.

**numbered lists** — See lists.

**numbers** — Spell out numbers zero through nine, with the exceptions listed in the [Microsoft Style Guide on numbers](https://docs.microsoft.com/en-us/style-guide/numbers). Numbers with a unit of measurement are not spelled out, such as 8 miles, 3 inches, 7 km, etc.

---

## O

**old** — Don't use. See previous versions.

**orphan** — Don't use.

**optional/optionally** — See Procedures.

**OS X/OSX** — As of 2016, it's macOS. (One word, not two.)

---

## P

**paid plans** — Use paid plans as shorthand to collectively refer to "Basic, Professional, and Enterprise plans." Use free plan to refer to the antonym.

**Pay-as-you-go** — Never pay-as-you-go pricing, pay-as-you-go-billing — it's a standalone term.

**pane** — Don't use panel. See [pane - Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/p/pane)

**parallel construction** — In construction like "Enter your email/username and your password…" avoid using the slash and use or instead.

**plan** — Don't use tier. Use plan to collectively refer to free and all paid plans. Users are on a plan. Features are available with a plan. You can also say a feature is in a plan.

**please** — Avoid please except in situations where the user is asked to do something inconvenient.

**Postman desktop app, Postman web app** — These are branded terms. See Branded Terms for more information.

**the Postman CLI** — Branded term. Always use "the" in front of it, and don't call it "the CLI" or "the cli."

**pre-, post-** — Avoid hyphenating words beginning with pre- or post-, such as preexisting, preorder, or predetermined. A notable exception is pre-request and post-response when referring to the sections in a Postman script tab.

**previous versions** — Don't use old/older/newer. Use earlier, later, or latest.

**Private API Monitoring** — Use to refer to the feature as a whole. The following usage applies:
- Team Admins can create/manage a runner when they create/edit a monitor.
- Team Admins get access to a management screen called "Runner settings."

**protobuf** — For the general name of the data format, introduce it as protobuf (protocol buffers) then use protobuf for subsequent references. Use ".proto file" to specifically refer to a file. Do not use ".PROTO," "proto file," or "PROTO."

---

## R

**reauthenticate** — Don't hyphenate.

**recipe** — Lowercase, in the context of cookbooks. (See cookbook.)

**resend** — Don't hyphenate ("re-send").

**return** — Use "Return or Enter." See keys and shortcuts.

**right-click** — Even though you should use select instead of click, you can use right-click when specifically talking about the secondary mouse action used to do things like open a context menu. See [right-click - Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/r/right-click)

**roles**
- Role names are capitalized.
- Role names are not bold.
- Role container names are capitalized.
- Team/workspace role names and element role names follow the same rules.

---

## S

**-(s)** — Don't use to indicate an optional pluralization. Generally, you can use only the plural.

**System for Cross-domain Identity Management (SCIM)** — Spell out first mention with SCIM in parentheses. Note that domain is lowercase according to the IETF.

**see** — Use view. ("To learn more, see some_topic" is okay.)

**see also** — As a heading in the Postman Docs at the bottom of a page, this is sentence case (See also).

**segregate** — Don't use. Use divide, isolate, quarantine, sequester, insulate.

**select** — See click.

**sidebar** — Use left sidebar and right sidebar. Note the lowercase.
- Items in the sidebar are tabs. See tabs for more information.
- Don't use abbreviated navigation to describe the multiple steps of going to an item in a tab.
- If you're writing about the left sidebar many times and not mentioning the right sidebar, you can use only sidebar in subsequent uses to refer to the left sidebar.
- A user can swap the left and right sidebars. You don't need to address this.

**sign in** — Use sign in instead of log in. Use sign in to instead of sign into.

**simple/simply** — Don't use. Simplicity is subjective. What's simple for us might be complex for our users. If something really is simple, it should be self-evident.

**single sign-on (SSO)** — Spell out first mention with SSO in parentheses. Note that it is all lowercase with a hyphen, unless referring to the UI in a third-party app.

**should** — Avoid, especially when indicating probability. Don't say "select ABC and your collection should be converted." Either it works, or something's wrong.

**Slack integration** — Don't use. Use "integration for Slack" instead.

**slashes** — Don't use as a substitute for or. For example, instead of "hide/unhide," use "hide or unhide."

**slot** — Don't use; use seat instead.

**Socket.IO** — Proper name; use this capitalization except in code.

**source control** — Don't use; use version control instead.

**specification, spec** — See API specification.

**STDIO** — All caps when referring to the general concept of Standard Input/Output. Use lowercase when applicable in a code sample.

**sub-** — In general, don't hyphenate words beginning with sub-, such as subheading and subsection, unless it's necessary to avoid confusion. See [sub - Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/s/sub)

---

## T

**tabs** — The following refers to items in the left and right sidebar. (This isn't for the tabs in the Workbench.)
- Tab names are bold and are title case.
- Use Aether icons similar to buttons.
- You can either click tabs or open tabs.
- Follow the naming in the tooltips of the tab icons.
- You can use Items to collectively refer to each state of the Items tab.
- The things in a tab are panels, but can be described by name, such as Collections, Environments, etc. Don't use all-caps.
- Individual elements are in a panel.
- You expand a panel, but you can also say click if it makes more sense.

**task bar, taskbar** — See menu bar.

**template** — See Branded Terms.

**the** — For branded terms, unless explicitly stated in Branded Terms, don't precede the term with the article the.

**third-party** — Hyphenate when it's used as a modifier, like "third-party integrations."

**ticket** — Avoid when referring to a support ticket. Instead, use support request.

**time** — Don't make time-specific references like now, soon, or new, especially when referring to features. (It's acceptable to use new when creating an element, like creating a new collection.) Don't make reference to specific time duration, such as "installation will take less than ten minutes." (Specifying an exact time range is an implied guarantee.)

**toggle** — Don't use toggle switch, toggle option, or option.
- Write around using toggle when convenient, such as definition lists.
- Toggle names are bold.
- Don't indicate direction. ("Toggle to the left of…")

**trash**
- When referring to trash in the app footer: "Select \<icon\> Trash in the footer."
- If it's the trash can icon being used for something else (for example, deleting a comment on a collection), use the icon name, unbolded: "Select the delete icon \<icon\>."
- Don't use trash can, trash icon, or trash button.

**try** — Avoid.

**TypeScript** — Don't use typescript, Typescript, or TS.

**types, types in collections**
- Use types to refer to the descriptive details you can configure for parameters, headers, and body data. The term types in collections no longer needs to be used to describe this feature.
- The term property to refer to the descriptive details you can configure for parameters, headers, and body data is now obsolete.
- Use schema to describe what's generated from the request body (that's in JSON format).

---

## U

**UI** — Don't use to refer to parts of the Postman app.

**users** — Use users for general use, or developers for specific context. Avoid using members except when referring specifically to users on Postman teams.

**utilize** — Use use instead.

**UX items** — For the "real" names of the meatballs, the hamburger, the gear, the eyeball, and more, see Frequently-used LC images.

---

## V

**variables pane, variables icon** — The variables icon is in the top-right, next to the environment selector. The variables pane is the pane that opens on the right when you select the variables icon. Neither is capitalized.

**vault** — See Branded Terms for usage of Postman Vault.

**verify** — Use verify sparingly. Use be sure or check when suggesting to investigate a condition. It can be used when referring to places it's used in the UX. (Verify sync, Verify domain)

**versions** — When referring to Postman major versions, use a lowercase v, such as Postman v11 and Postman v12.

**versus, vs.** — Don't use vs. Rewrite to avoid using versus.

**version control** — Use instead of source control, unless it's called source control in the UX.

**via** — Do not use, except for geographical usage.

---

## W

**we** — Avoid using first person in core docs. "Let's" and "we" are appropriate in tutorials and blog posts but typically not in the documentation.

**whether** — Don't use whether or not.

**white-box testing** — Don't use. Use transparent-box testing, clear-box testing, or structural testing.

**whitelist** — Don't use. Use allowlist.

**widow** — Don't use.

**Wi-Fi** — Not wifi or wi-fi.

**workbench** — The main window or "main work area" in Postman. This is lowercase and not a branded term.

---

## Y

**You will see** — Do not use. Use there is or there are instead. Example: Instead of "Above the message display, you will see four icons" use "Above the message display, there are four icons."

---

## Z

**zip file** — All lowercase, no code style. Do not use Zip file, ZIP file, or .zip file.

---

## Note

Footnotes next to an item are links to the style review cycle where the item was introduced or modified. See the cycle page for more information on the decision made.
````