# AI Personal Assistant

This project provides a personal assistant agent that manages tasks related to your email inbox, calendar, Notion to-do list, Slack interactions, and handles any research you may have. The assistant communicates with you via your preferred communication channel **(Telegram, Slack, or WhatsApp)**, keeping you informed about your schedule, tasks, emails, messages, and helping with research topics, people, or even companies.

The personal assistant is a **hierarchical multi-agents** system with a **supervisor agent** (manager) and several sub-agents that handle specific tasks and tools for efficient task management.

## Overview

### Main Agent: Assistant Manager

The Assistant Manager is your personal assistant that orchestrates the tasks and communication between you and the sub-agents. The manager is responsible for:

- Receiving and analyzing your messages from your chosen communication channel.
- Delegating tasks to the appropriate sub-agent (Email, Calendar, Notion, Slack, or Researcher).
- Communicating updates, messages, and any queries back to you via your preferred channel.

### Sub-Agents

The manager agent can communicate with five specialized sub-agents:

1.  **Email Agent:** Can handle all your email-related tasks, including sending emails, retrieving specific emails, and checking for important messages from your contacts list.
2.  **Calendar Agent:** Can manage your calendar by creating new events and retrieving and checking your scheduled events.
3.  **Notion Agent:** Can manage your to-do list in Notion, helping you add, remove, or check tasks as needed.
4.  **Slack Agent:** Can manage your Slack interactions by reading messages from channels or DMs and sending messages on your behalf.
5.  **Researcher Agent:** Can perform web research, scrape websites, and gather information from LinkedIn profiles to assist with research tasks.

All the sub-agents report back to the Assistant Manager after completing their respective tasks.

## Tech Stack

-   **LangGraph & LangChain**: Frameworks used for building the AI agents and interacting with LLMs (GPT-4, Llama 3, Gemini).
-   **LangSmith**: For monitoring the different LLM calls and AI agents' interactions.
-   **Google APIs**: Provides access to Google services like Calendar, Contacts, and Gmail.
-   **Notion Client**: Interface for interacting with Notion to manage and update to-do lists.
-   **Slack SDK**: For interacting with Slack, sending and receiving messages.
-   **Tavily Search API**: For performing web searches.
-   **Telegram API**: Depending on your choice of communication channel.
-   **WhatsApp API via Twilio Sandbox (for testing)**: A way to integrate WhatsApp communication.

