export default function CoursesPage() {
  return (
    <div className="container py-8">
      <h1 className="font-heading text-4xl mb-8">Available Courses</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Mathematics</h2>
          <p className="text-muted-foreground mb-4">Master mathematical concepts from basic arithmetic to advanced calculus.</p>
          <div className="text-sm text-muted-foreground">12 Modules • 48 Lessons</div>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Physics</h2>
          <p className="text-muted-foreground mb-4">Explore the fundamental laws that govern our universe.</p>
          <div className="text-sm text-muted-foreground">10 Modules • 40 Lessons</div>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Computer Science</h2>
          <p className="text-muted-foreground mb-4">Learn programming, algorithms, and computational thinking.</p>
          <div className="text-sm text-muted-foreground">15 Modules • 60 Lessons</div>
        </div>
      </div>
    </div>
  );
}