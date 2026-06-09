TaskFlow

A dark-mode task dashboard and management application built using React, Vite, TypeScript, and TailwindCSS.

Features
- Clean, dark-mode UI with TailwindCSS
- Task management: create, view, update, and delete tasks
- Responsive dashboard layout
- Fully typed with TypeScript
- Fast development with Vite

Getting Started

Prerequisites
- Node.js (v18 or higher)
- npm or yarn

Installation
1. Clone the repository:
   git clone https://github.com/yourusername/taskflow.git
   cd taskflow

2. Install dependencies:
   npm install
   # or
   yarn install

3. Start the development server:
   npm run dev
   # or
   yarn dev

The app will be available at http://localhost:5173

Project Structure
src/
├── pages/
│   ├── Dashboard.tsx   # Main dashboard view
│   └── Tasks.tsx       # Task management view
├── App.tsx
├── main.tsx
└── index.css

Usage
- Navigate to the Dashboard to view all tasks in an organized layout
- Use the Tasks page to add, edit, or remove individual tasks
- All task data is managed in-memory (no backend required for this version)

Built With
- React 18
- Vite 4
- TypeScript 5
- TailwindCSS 3

License
MIT

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
