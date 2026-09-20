export function EmptyState({ title, children }: { title: string; children: string }) {
  return (
    <section className="empty-state">
      <h2>{title}</h2>
      <p>{children}</p>
    </section>
  );
}
