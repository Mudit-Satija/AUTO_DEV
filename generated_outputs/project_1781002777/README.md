StudyHub

A student dashboard, courses, assignments and calendar planner app built using React, Vite, TypeScript, and TailwindCSS.

Features
- Dashboard with overview of upcoming assignments and events
- Courses page to view and manage enrolled courses
- Course Details page with nested assignments and events
- Assignments page to track deadlines and status
- Calendar planner with daily, weekly, and monthly views
- Persistent storage via localStorage for all entities (Course, Assignment, Event)
- Responsive design with TailwindCSS

Project Structure
src/
├── pages/
│   ├── Dashboard.tsx
│   ├── Courses.tsx
│   ├── CourseDetails.tsx
│   ├── Assignments.tsx
│   └── Calendar.tsx
├── App.tsx
├── main.tsx
└── index.css

Setup Instructions

1. Prerequisites
- Node.js (v18 or higher)
- npm or yarn

2. Clone the repository
git clone https://github.com/yourusername/studyhub.git
cd studyhub

3. Install dependencies
npm install

4. Start the development server
npm run dev

The app will be available at http://localhost:5173

5. Build for production
npm run build

The optimized build will be generated in the dist/ folder.

Usage
- Navigate between pages using the top navigation bar
- All data is stored in localStorage and persists between sessions
- No backend server required — fully client-side application

Entity Management
All entities (Course, Assignment, Event) are stored under the following localStorage keys:
- 'studyhub-courses'
- 'studyhub-assignments'
- 'studyhub-events'

Data is automatically synchronized across all pages via a shared state context.

Dependencies
- React 18+
- Vite 4+
- TypeScript 5+
- TailwindCSS 3+
- react-router-dom 6+

License
MIT