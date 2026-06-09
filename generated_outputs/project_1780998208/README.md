TaskFlow

A dark-mode task dashboard and management application built using React, Vite, TypeScript, and TailwindCSS.

Features
- Clean, dark-mode UI with TailwindCSS
- Task management dashboard with add, edit, and delete functionality
- Responsive design for desktop and mobile
- TypeScript for type safety
- Vite for fast development and build times

Setup Instructions

1. Clone the repository:
   git clone https://github.com/yourusername/taskflow.git
   cd taskflow

2. Install dependencies:
   npm install

3. Start the development server:
   npm run dev

4. Open your browser and navigate to http://localhost:5173

Project Structure
- src/
  - pages/
    - Dashboard.tsx    # Main dashboard view
    - Tasks.tsx        # Task management view
  - App.tsx
  - main.tsx
  - index.css

The application uses React with TypeScript and TailwindCSS for styling. All state is managed locally in React components. No backend server is required for basic functionality.

Built with:
- React 18
- Vite 4
- TypeScript 5
- TailwindCSS 3

License
MIT