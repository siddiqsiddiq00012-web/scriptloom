export function SkeletonCard() {
  return (
    <div className="card" style={{ padding: "var(--sp-5)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
        <div className="skeleton skeleton-avatar" />
        <div style={{ flex: 1 }}>
          <div className="skeleton skeleton-title" style={{ width: "50%" }} />
          <div className="skeleton skeleton-text-sm" style={{ width: "30%" }} />
        </div>
      </div>
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text" style={{ width: "75%" }} />
    </div>
  );
}

export function SkeletonMetricCard() {
  return (
    <div className="card card-padding">
      <div className="skeleton skeleton-text-sm" style={{ width: "40%", marginBottom: "12px" }} />
      <div className="skeleton" style={{ height: 32, width: "60%", marginBottom: "8px" }} />
      <div className="skeleton skeleton-text-sm" style={{ width: "50%" }} />
    </div>
  );
}

export function SkeletonGrid({ count = 3 }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonMetricGrid() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "20px" }}>
      {Array.from({ length: 4 }).map((_, i) => (
        <SkeletonMetricCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonRow() {
  return (
    <div className="card" style={{ padding: "16px 20px", display: "flex", alignItems: "center", gap: "16px" }}>
      <div className="skeleton" style={{ width: 36, height: 36, borderRadius: "10px" }} />
      <div style={{ flex: 1 }}>
        <div className="skeleton skeleton-text" style={{ width: "40%", marginBottom: "6px" }} />
        <div className="skeleton skeleton-text-sm" style={{ width: "25%" }} />
      </div>
      <div className="skeleton skeleton-btn" />
    </div>
  );
}
