# 🚀 Perplexica - An AI-powered search engine 🔎 <!-- omit in toc -->

<div align="center" markdown="1">
   <sup>Special thanks to:</sup>
   <br>
   <br>
   <a href="https://www.warp.dev/perplexica">
      <img alt="Warp sponsorship" width="400" src="https://github.com/user-attachments/assets/775dd593-9b5f-40f1-bf48-479faff4c27b">
   </a>

### [Warp, the AI Devtool that lives in your terminal](https://www.warp.dev/perplexica)

[Available for MacOS, Linux, & Windows](https://www.warp.dev/perplexica)

</div>

<hr/>

[![Discord](https://dcbadge.limes.pink/api/server/26aArMy8tT?style=flat)](https://discord.gg/26aArMy8tT)

![preview](.assets/perplexica-screenshot.png?)

## Table of Contents <!-- omit in toc -->

- [Overview](#overview)
- [Preview](#preview)
- [Features](#features)
- [Installation](#installation)
  - [Getting Started with Docker (Recommended)](#getting-started-with-docker-recommended)
  - [Non-Docker Installation](#non-docker-installation)
  - [Ollama Connection Errors](#ollama-connection-errors)
  - [Lemonade Connection Errors](#lemonade-connection-errors)
- [Using as a Search Engine](#using-as-a-search-engine)
- [Using Perplexica's API](#using-perplexicas-api)
- [Expose Perplexica to a network](#expose-perplexica-to-network)
- [One-Click Deployment](#one-click-deployment)
- [Upcoming Features](#upcoming-features)
- [Support Us](#support-us)
  - [Donations](#donations)
- [Contribution](#contribution)
- [Help and Support](#help-and-support)

## Overview

Perplexica is an open-source AI-powered chat assistant designed for internal usage. It provides intelligent conversations with support for local LLMs and file uploads, making it perfect for private, secure AI interactions within your organization.

This version has been modified for internal use and does not include web search capabilities, focusing on privacy and security for enterprise environments.

## Preview

![video-preview](.assets/perplexica-preview.gif)

## Features

- **Local LLMs**: You can utilize local LLMs such as Qwen, DeepSeek, Llama, and Mistral.
- **Writing Assistant Mode**: Helpful for writing tasks and general AI conversations.
- **File Upload Support**: Upload and analyze documents (PDF, DOCX, etc.) with intelligent processing.
- **Privacy-First**: No web search or external data collection - perfect for internal usage.
- **Local-First Architecture**: All processing happens on your infrastructure.
- **API Integration**: Integrate into your existing applications.
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, Groq, local models and more.

It has many more features like image and video search. Some of the planned features are mentioned in [upcoming features](#upcoming-features).

## Installation

There are mainly 2 ways of installing Perplexica - With Docker, Without Docker. Using Docker is highly recommended.

### Getting Started with Docker (Recommended)

1. Ensure Docker is installed and running on your system.
2. Clone the Perplexica repository:

   ```bash
   git clone https://github.com/ItzCrazyKns/Perplexica.git
   ```

3. After cloning, navigate to the directory containing the project files.

4. Rename the `sample.config.toml` file to `config.toml`. Configure the following fields based on your preferred LLM provider:

   - `OPENAI`: Your OpenAI API key. **You only need to fill this if you wish to use OpenAI's models**.
   - `CUSTOM_OPENAI`: Your OpenAI-API-compliant local server URL, model name, and API key. **You only need to configure these settings if you want to use a local OpenAI-compliant server**.
   - `OLLAMA`: Your Ollama API URL. **You need to fill this if you wish to use Ollama's models**.
   - `GROQ`: Your Groq API key. **You only need to fill this if you wish to use Groq's hosted models**.
   - `ANTHROPIC`: Your Anthropic API key. **You only need to fill this if you wish to use Anthropic models**.
   - `Gemini`: Your Gemini API key. **You only need to fill this if you wish to use Google's models**.
   - `DEEPSEEK`: Your Deepseek API key. **Only needed if you want Deepseek models.**
   - `AIMLAPI`: Your AI/ML API key. **Only needed if you want to use AI/ML API models and embeddings.**

     **Note**: You can change these after starting Perplexica from the settings dialog.

   - `SIMILARITY_MEASURE`: The similarity measure to use (This is filled by default; you can leave it as is if you are unsure about it.)

5. Ensure you are in the directory containing the `docker-compose.yaml` file and execute:

   ```bash
   docker compose up -d
   ```

6. Wait a few minutes for the setup to complete. You can access Perplexica at http://localhost:3000 in your web browser.

**Note**: After the containers are built, you can start Perplexica directly from Docker without having to open a terminal.

### Non-Docker Installation

1. Clone the repository and rename the `sample.config.toml` file to `config.toml` in the root directory. Ensure you complete all required fields in this file.
2. After populating the configuration run `npm i`.
3. Install the dependencies and then execute `npm run build`.
4. Finally, start the app by running `npm run start`

**Note**: Using Docker is recommended as it simplifies the setup process, especially for managing environment variables and dependencies.

See the [installation documentation](https://github.com/ItzCrazyKns/Perplexica/tree/master/docs/installation) for more information like updating, etc.

### Troubleshooting

#### Local OpenAI-API-Compliant Servers

If Perplexica tells you that you haven't configured any chat model providers, ensure that:

1. Your server is running and accessible.
2. You have specified the correct model name loaded by your local LLM server.
3. You have specified the correct API key, or if one is not defined, you have put _something_ in the API key field and not left it empty.

#### Ollama Connection Errors

If you're encountering an Ollama connection error, it is likely due to the backend being unable to connect to Ollama's API. To fix this issue you can:

1. **Check your Ollama API URL:** Ensure that the API URL is correctly set in the settings menu.
2. **Update API URL Based on OS:**

   - **Windows:** Use `http://host.docker.internal:11434`
   - **Mac:** Use `http://host.docker.internal:11434`
   - **Linux:** Use `http://<private_ip_of_host>:11434`

   Adjust the port number if you're using a different one.

3. **Linux Users - Expose Ollama to Network:**

   - Inside `/etc/systemd/system/ollama.service`, you need to add `Environment="OLLAMA_HOST=0.0.0.0:11434"`. (Change the port number if you are using a different one.) Then reload the systemd manager configuration with `systemctl daemon-reload`, and restart Ollama by `systemctl restart ollama`. For more information see [Ollama docs](https://github.com/ollama/ollama/blob/main/docs/faq.md#setting-environment-variables-on-linux)

   - Ensure that the port (default is 11434) is not blocked by your firewall.

#### Lemonade Connection Errors

If you're encountering a Lemonade connection error, it is likely due to the backend being unable to connect to Lemonade's API. To fix this issue you can:

1. **Check your Lemonade API URL:** Ensure that the API URL is correctly set in the settings menu.
2. **Update API URL Based on OS:**

   - **Windows:** Use `http://host.docker.internal:8000`
   - **Mac:** Use `http://host.docker.internal:8000`
   - **Linux:** Use `http://<private_ip_of_host>:8000`

   Adjust the port number if you're using a different one.

3. **Ensure Lemonade Server is Running:**

   - Make sure your Lemonade server is running and accessible on the configured port (default is 8000).
   - Verify that Lemonade is configured to accept connections from all interfaces (`0.0.0.0`), not just localhost (`127.0.0.1`).
   - Ensure that the port (default is 8000) is not blocked by your firewall.

## Using as a Chat Interface

Perplexica serves as an intelligent chat interface for your internal AI needs. You can:

1. Have conversations with various LLM providers
2. Upload and analyze documents
3. Get assistance with writing and general tasks
4. Access the application at `http://localhost:3000` after setup

## Using Perplexica's API

Perplexica provides an API for developers looking to integrate its AI chat capabilities into their own applications. You can run chat sessions, use multiple models and get intelligent responses.

For more details, check out the API documentation.

## Expose Perplexica to network

Perplexica runs on Next.js and handles all API requests. It works right away on the same network and stays accessible with port forwarding for internal usage within your organization.

## One-Click Deployment

[![Deploy to Sealos](https://raw.githubusercontent.com/labring-actions/templates/main/Deploy-on-Sealos.svg)](https://usw.sealos.io/?openapp=system-template%3FtemplateName%3Dperplexica)
[![Deploy to RepoCloud](https://d16t0pc4846x52.cloudfront.net/deploylobe.svg)](https://repocloud.io/details/?app_id=267)
[![Run on ClawCloud](https://raw.githubusercontent.com/ClawCloud/Run-Template/refs/heads/main/Run-on-ClawCloud.svg)](https://template.run.claw.cloud/?referralCode=U11MRQ8U9RM4&openapp=system-fastdeploy%3FtemplateName%3Dperplexica)
[![Deploy on Hostinger](https://assets.hostinger.com/vps/deploy.svg)](https://www.hostinger.com/vps/docker-hosting?compose_url=https://raw.githubusercontent.com/ItzCrazyKns/Perplexica/refs/heads/master/docker-compose.yaml)

## Upcoming Features

- [x] Add settings page
- [x] Adding support for local LLMs
- [x] History Saving features
- [x] Writing Assistant Mode
- [x] Adding API support
- [ ] Enhanced file processing capabilities
- [ ] Advanced document analysis features

## Support Us

If you find Perplexica useful, consider giving us a star on GitHub. This helps more people discover Perplexica and supports the development of new features. Your support is greatly appreciated.

### Donations

We also accept donations to help sustain our project. If you would like to contribute, you can use the following options to donate. Thank you for your support!

| Ethereum                                              |
| ----------------------------------------------------- |
| Address: `0xB025a84b2F269570Eb8D4b05DEdaA41D8525B6DD` |

## Contribution

Perplexica is built on the idea that AI should be easy for everyone to use in secure, private environments. If you find bugs or have ideas for this internal version, please share them via GitHub Issues. For more information on contributing to Perplexica you can read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Help and Support

If you have any questions or feedback, please feel free to reach out to us. You can create an issue on GitHub or join our Discord server. There, you can connect with other users, share your experiences and reviews, and receive more personalized help. [Click here](https://discord.gg/EFwsmQDgAu) to join the Discord server. To discuss matters outside of regular support, feel free to contact me on Discord at `itzcrazykns`.

Thank you for exploring Perplexica, the AI-powered chat assistant designed for internal usage. We are constantly working to improve Perplexica and expand its capabilities for secure, private AI interactions. We value your feedback and contributions which help us make Perplexica even better for internal enterprise use. Don't forget to check back for updates and new features!
