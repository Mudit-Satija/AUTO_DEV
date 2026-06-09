TaskFlow

A dark-mode task dashboard and management application built using React, Vite, TypeScript, and TailwindCSS.

Features
- Dark mode interface with TailwindCSS
- Task management via Dashboard and Tasks pages
- Single source of truth using localStorage for tasks
- Responsive design with clean, modern UI
- Navigation between Dashboard and Tasks pages

Setup Instructions

1. Clone the repository:
   git clone https://github.com/yourusername/taskflow.git
   cd taskflow

2. Install dependencies:
   npm install

3. Start the development server:
   npm run dev

4. Open your browser and navigate to http://localhost:5173

Usage

- Dashboard: View an overview of your tasks, including counts and progress.
- Tasks: Add, edit, and delete tasks. All changes are persisted to localStorage.

Data Persistence

All tasks are stored in localStorage under the key 'tasks'. This ensures data persists across sessions and is shared between Dashboard and Tasks pages.

No backend is required — TaskFlow is a frontend-only application.

File Structure

src/
├── pages/
│   ├── Dashboard.tsx
│   └── Tasks.tsx
├── App.tsx
├── main.tsx
└── index.css

Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License

MIT