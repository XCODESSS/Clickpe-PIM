import Link from "next/link";

export default function NotFound() {
  return (
    <main className="workspace">
      <div className="route-header">
        <h1>Snapshot page not found</h1>
        <p>The selected finalized snapshot does not contain this route. Return to the overview and choose a stored record.</p>
      </div>
      <Link href="/">Return to overview</Link>
    </main>
  );
}
