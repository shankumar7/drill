"use client";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white p-8">
      <h1 className="text-5xl font-bold mb-6">Military Drill Evaluation System</h1>
      <p className="mb-8 text-lg text-center max-w-2xl">
        Welcome! Use the button below to start evaluating cadets with the Savadhan drill.
      </p>
      <a href="/evaluation" className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 rounded text-white text-lg transition transform hover:scale-105">
        Go to Evaluation
      </a>
    </main>
  );
}
