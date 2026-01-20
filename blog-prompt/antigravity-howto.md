Write a blog post using the /devrel-blogger command. The post should be similar to https://quintonwall.substack.com/p/using-postman-mcp-server-with-gemini and provides step-by-step instructions  how a developer can perform the following actions:
- install the MCP server into Antigravity. https://antigravity.google/docs/mcp, including a description of which install options you should choose: minimum, full, code. We are going to use minimal in this example. Also, include a reference to the correct setup for developers in the EU. 
- Define a standard workflow for Postman MCP in antigravity
    - Existing collections
        - list workspaces
        - select workspace "Quintons Playzone"
        - list collection
        - select collection "Fleet Logistics API"
        - run collection so I can see the test code coverage output
        - create a simple react app and use the collection to generate routes
    - Existing code (based on https://github.com/Postman-Devrel/fleet-logistics-api)
        - list workspace
        - select workspace  "Quintons Playzone"
        - create a collection from code (routes)
        - add tests (only available if we install full mcp)
        - add monitoring (only available if we install full mcp)


For Postman MCP reference, use this guide:
- https://github.com/postmanlabs/postman-mcp-server/blob/main/README.md

Save the blog post in the /blogs directory in markdown format.
