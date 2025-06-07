# Orchids SWE Intern Challenge Template

This project consists of a backend built with FastAPI and a frontend built with Next.js and TypeScript.

## Backend

The backend uses `uv` for package management.

### Installation

To install the backend dependencies, run the following command in the backend project directory:

```bash
uv sync
```

### Create Environment File

Create a .env file in the backend directory:
```# backend/.env
ANTHROPIC_API_KEY=your_anthropic_api_key_here```

### Get your Anthropic API key

Go to Anthropic Console
Sign up/login and create an API key
Copy the key to your .env file

### Install Chrome WebDriver

The application uses webdriver-manager to automatically manage Chrome WebDriver, but you need Chrome browser installed

### Running the Backend

To run the backend development server, use the following command:

```bash
uv run fastapi dev
```

## Frontend

The frontend is built with Next.js and TypeScript.

### Installation

To install the frontend dependencies, navigate to the frontend project directory and run:

```bash
npm install
```

### Running the Frontend

To start the frontend development server, run:

```bash
npm run dev
```
