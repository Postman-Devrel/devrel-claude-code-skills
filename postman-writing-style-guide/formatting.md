Here's the page converted to Markdown:

````markdown
# Text formatting

Follow these guidelines for text formatting in documentation.

| Element | Formatting | Example |
|---------|------------|---------|
| **code** | For inline code, use single backticks. For code blocks, use three backticks and specify a language. | The request body of the webhook is available inside the `` `globals.previousRequest` `` object. |
| **definitions** | Italics. This is most helpful in a lede paragraph the first time you use a new term, either for Postman or a third-party item. | Example: "*Swagger* is a suite of open-source tools built around the OpenAPI Specification…" |
| **icons** | Icon first, then the tooltip name or label in bold after. | See [Frequently-used LC images](https://postmanlabs.atlassian.net/wiki/spaces/TW/pages/3600449661) |
| **keys** | Bold. Also bold the + between a key and modifier. | **Cmd+C** |
| **UX elements** | Bold. In a path separated by `>`s, bold the greater-than signs. For example, "Select **View** **>** **Developer** **>** **Show DevTools**." This also includes sections of the UI such as the **About Me** section of a Postman user profile. | Enter a **name**, then select **Integrate any other application you don't find in the gallery**. |
| **paths** | - Use code font, or use a code block if it's part of a larger script or snippet. - Use placeholders such as `path/to/file`. - Don't use brackets to denote a variable or something a user has to change. - Ensure paths don't contain PII such as usernames or element IDs. - You can use shell variables such as `$HOME` to avoid using a path on your machine. - Due to a Markdown limitation, we can't use italics in a path. | |
| **Text a user enters** | - Use quotes for things a user types in. - Use italic for placeholders. - Use code blocks for longer items. - Don't use `code` for things a user types in. | Enter "Postman" as your service provider. Enter "Team *name*" to post your team's name. |
| **Smart quotes, em-dashes, en-dashes, ellipses** | We use the `remark-smartypants` plugin to prettify these in rendered output: - Straight quotes ( " and ' ) into "curly" quote HTML entities - Backticks-style quotes (`` ``like this'' ``) into "curly" quote HTML entities - Dashes (`---` and `--`) into en- and em-dash entities - Three consecutive dots (`...`) into an ellipsis entity | |
| **emphasis** | Avoid using italics or bold for emphasis for words that aren't already covered in other formatting rules above. | No: You should **Avoid** using bold when you think you **should** be emphasizing words. |

## See also

- [Postman Docs Markdown formatting](https://postmanlabs.atlassian.net/wiki/spaces/TW/pages/3679060249)
- [Formatting common text elements - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/text-formatting/formatting-common-text-elements)
- [Formatting text in instructions - Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/procedures-instructions/formatting-text-in-instructions)
````