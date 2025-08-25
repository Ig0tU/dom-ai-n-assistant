
Built by https://www.blackbox.ai

---

# DOM-AI-N Assistant (Ultimate)

## Project Overview
The **DOM-AI-N Assistant** is a powerful AI web assistant that integrates with your browser to enhance your web experience. This project, built as a user script, allows users to interact with any webpage through an intuitive interface powered by the Google Gemini API. Featuring a range of tools for DOM manipulation, information retrieval, and browser control, the assistant empowers users to automate tasks and streamline their workflows on the web.

## Installation
To install the DOM-AI-N Assistant, you will need a browser extension that supports user scripts, such as [Tampermonkey](https://www.tampermonkey.net/) or [Greasemonkey](https://www.greasespot.net/). Follow these steps:

1. Install the Tampermonkey or Greasemonkey extension in your browser.
2. Create a new script using the extension's dashboard.
3. Copy the contents of the `chameleon-ai-forge.user.js` or `domai.css` file and paste them into the new script.
4. Save the script and ensure it is enabled.
5. Navigate to any webpage, and the assistant should be visible in the lower right corner.

## Usage
Once the DOM-AI-N Assistant is installed, you can interact with any webpage in the following ways:

- **Open Assistant**: Click on the assistant icon in the bottom right corner to open the user interface.
- **Chat with the AI**: Type your request in the input field, such as "Make all buttons green" or "Click the login button."
- **Access Tools**: Utilize the list of available tools by clicking the tools button, which provides functionalities like inspecting elements, modifying styles, and retrieving information about the page.
- **Settings**: Click on the settings button to enter your Gemini API key, customize themes, or clear log data.

## Features
- **AI-Powered Conversations**: Directly chat with the assistant to automate tasks and gather information.
- **DOM Manipulation**: Modify styles, click elements, and change content on the page.
- **Information Retrieval**: Fetch and display details about elements, links, images, and more.
- **Browser Control**: Navigate, refresh, and manipulate browser tabs with ease.
- **User-Friendly Interface**: A clean design with a responsive layout that supports both light and dark themes.

## Dependencies
This project includes the following dependencies:
- **Tampermonkey/Greasemonkey**: For executing user scripts and providing APIs like `GM_addStyle`, `GM_getValue`, and `GM_xmlhttpRequest`.

## Project Structure
```plaintext
.
├── chameleon-ai-forge.user.js   # Main user script for the assistant
├── domai.css                     # CSS styling for the assistant interface
└── README.md                     # Project documentation
```

### Important JS Variables
- `GEMINI_API_URL`: The endpoint for the Google Gemini API.
- `chatHistory`: Array to hold previous interactions for context.
- `tools`: Object containing all the tools available in the assistant.

Each tool included in the assistant is designed to handle specific user requests, making it intuitive to automate almost any web-based task.

## License
This project is open-source and available under the [MIT License](LICENSE).

---

For more information or to report issues, please contact the project maintainers listed in the `chameleon-ai-forge.user.js` file.