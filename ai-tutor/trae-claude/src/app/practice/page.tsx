export default function PracticePage() {
  return (
    <div className="container py-8">
      <h1 className="font-heading text-4xl mb-8">Practice Exercises</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Problem Solving</h2>
          <p className="text-muted-foreground mb-4">Practice with interactive problems that adapt to your skill level.</p>
          <div className="text-sm text-muted-foreground">100+ Problems</div>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Quizzes</h2>
          <p className="text-muted-foreground mb-4">Test your knowledge with subject-specific quizzes.</p>
          <div className="text-sm text-muted-foreground">50+ Quizzes</div>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-heading text-2xl mb-4">Coding Challenges</h2>
          <p className="text-muted-foreground mb-4">Improve your programming skills with hands-on challenges.</p>
          <div className="text-sm text-muted-foreground">75+ Challenges</div>
        </div>
      </div>
    </div>
  );
}