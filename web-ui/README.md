# Drill Web UI

Next.js dashboard for drill command selection and evaluation display. This frontend is a control surface for the Python backend; it does not run YOLO, pose detection, or computer vision logic in the browser.

## Run Locally

```bash
cd web-ui
npm install
npm run dev
```

Open `http://localhost:3000` after the dev server starts.

## Backend URL

The frontend reads the backend base URL from `NEXT_PUBLIC_BACKEND_URL`.

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

If this variable is not set, the frontend falls back to `http://localhost:8000`.

## Mock Data

The dashboard can run without the backend. If the backend is unavailable, the UI keeps rendering with deterministic mock evaluation data and clearly marks the connection state as `Using mock data`.

## Commands

The command selector includes:

- `SAVDHAN`
- `VISHRAM`
- `LO 1.1.2` through `LO 1.1.11`

`KADWAR` and `CANE_DRILL` are currently shown as warnings only. They are not selectable commands until backend rule metadata and evaluation support are added.

## Legacy Python GUI

The old Python GUI is not part of this Next.js workflow. Use it only as reference while the team transitions the UI to `web-ui`.
