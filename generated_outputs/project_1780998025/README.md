TaskFlow

A dark-mode task dashboard and management application built using React, Vite, TypeScript, and TailwindCSS.

Overview
TaskFlow is a sleek, dark-themed task management dashboard designed for productivity and focus. It allows users to view, add, edit, and delete tasks with an intuitive interface. Built with modern web technologies, TaskFlow provides a responsive and performant experience with zero dependencies on external backends — all task data is managed client-side.

Features
- Dark mode interface with TailwindCSS
- Task creation, editing, and deletion
- Responsive dashboard layout
- TypeScript for type safety
- Vite for fast development and builds
- React hooks for state management

Pages
- Dashboard: Main view showing all tasks in a clean grid
- Tasks: View and manage individual task entries

Setup Instructions

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

Build for Production
To build a production-ready bundle:
   npm run build

The output will be in the dist/ directory.

File Structure
src/
├── pages/
│   ├── Dashboard.tsx
│   └── Tasks.tsx
├── App.tsx
├── main.tsx
└── tailwind.config.js

Dependencies
- react
- react-dom
- vite
- typescript
- tailwindcss
- @types/react
- @types/react-dom

License
MIT

Note: TaskFlow is a client-side application. No backend server or database is required. Task data is stored in memory during runtime.