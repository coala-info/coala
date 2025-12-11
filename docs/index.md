---
layout: home

hero:
  name: "Coala"
  text: "Convert CMD Tools into LLM Agents"
  tagline: Leverage the Model Context Protocol (MCP) to bridge command-line tools and Large Language Models
  image:
    src: /Coala.svg
    alt: Coala
    size: large
  actions:
    - theme: brand
      text: Get Started
      link: /guide/
    - theme: alt
      text: View on GitHub
      link: https://github.com/rworkflow/coala

features:
  - icon: 🔒
    title: Local Data Handling
    details: Run professional tools on local data securely, without uploading sensitive files to the cloud.
  - icon: 🔌
    title: Universal Integration
    details: Easily convert any command-line tool into an MCP-based agent with minimal effort.
  - icon: 🌐
    title: CWL Ecosystem
    details: Leverage the vast, open-source CWL community—especially strong in bioinformatics—for tool definitions.
  - icon: 🤖
    title: Natural Language Interface
    details: Access advanced tools and workflows through natural language, lowering the barrier to entry.
  - icon: 🐳
    title: Containerized Execution
    details: Tools run in isolated containers, ensuring reproducibility and avoiding dependency conflicts.
  - icon: ⚡
    title: Flexible & Scalable
    details: Works with any LLM or client that supports MCP, enabling vendor-agnostic, modular workflows.

---

## Overview

Coala (local COmmAnd-line LLM-agent Adapter) is a Python package that converts any command-line tool into a Large Language Model (LLM) agent. This allows you to interact with the tool using natural language, making it easier to use and integrate with other applications.

The framework works by converting CWL (Common Workflow Language) tool definitions into MCP-compatible agents that can be discovered and invoked by LLMs through natural language queries. Here's how it works: you create an MCP server instance using `mcp_api`, register your domain-specific tools by providing their CWL definitions via `add_tool()`, and then start the server. The MCP server exposes these tools as discoverable agents that any MCP-compatible client (like Cursor) can query and invoke.

When an LLM needs to use a tool, it queries the MCP server for available tools, selects the appropriate one, and invokes it with the necessary parameters. The tool executes within a containerized environment (as specified in the CWL), processes the request, and returns results back through the MCP protocol to the LLM, which then presents the answer to the user in natural language.

## How It Works

Coala leverages the Model Context Protocol (MCP) to bridge command-line tools and Large Language Models (LLMs). MCP acts as a "USB-C port" for AI applications, standardizing how LLMs connect to tools and data, regardless of the underlying infrastructure or vendor.

### Infrastructure

The core infrastructure consists of:

- **MCP Server**: Hosted locally using `mcp_api`, it exposes tool agents over the MCP protocol.
- **Tool Agents**: Any CWL-described command-line tool can be wrapped and registered as an agent using `add_tool`.
- **MCP Client**: Typically running alongside an LLM, it discovers available tool agents, queries their capabilities, and invokes them as needed.

When an LLM decides to use a tool, it sends the required parameters to the MCP client, which then calls the appropriate agent on the MCP server. The agent pulls the necessary container and executes the tool with the provided parameters, returning results to the LLM.

