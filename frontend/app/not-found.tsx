export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-bold mb-2">404 - Page Not Found</h1>
      <p className="text-slate-400 text-sm">The page you are looking for does not exist.</p>
      <a href="/" className="mt-4 px-4 py-2 bg-indigo-600 rounded-xl text-xs font-semibold">
        Return Home
      </a>
    </div>
  );
}
