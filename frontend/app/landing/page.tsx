import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-neutral-800">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span className="text-white text-xs font-bold">SL</span>
          </div>
          <span className="text-sm font-semibold text-white">StateLens</span>
        </div>
        <Link
          href="/"
          className="text-xs px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
        >
          Open Debugger
        </Link>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-8 text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 rounded-full bg-indigo-600/10 border border-indigo-500/20 px-3 py-1.5 text-xs text-indigo-400 mb-8">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 inline-block" />
          Chrome DevTools for AI Agents
        </div>

        <h1 className="text-5xl font-bold text-white tracking-tight leading-tight mb-6">
          Debug your AI agent.
          <br />
          <span className="text-indigo-400">Understand every decision.</span>
        </h1>

        <p className="text-lg text-neutral-400 leading-relaxed mb-10 max-w-xl">
          StateLens gives you a visual debugger for LangGraph executions. Inspect every node,
          state transition, tool call, and prompt — without reading logs.
        </p>

        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="px-6 py-3 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-500 transition-colors"
          >
            Open Debugger
          </Link>
          <a
            href="https://github.com"
            className="px-6 py-3 rounded-xl border border-neutral-700 text-neutral-300 text-sm font-medium hover:bg-neutral-800 transition-colors"
          >
            View on GitHub
          </a>
        </div>
      </main>

      {/* Features */}
      <section className="px-8 py-16 max-w-5xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: "◈",
              title: "Execution Graph",
              description:
                "Visualize every node in your LangGraph as an interactive graph. See the full execution flow at a glance.",
            },
            {
              icon: "⏱",
              title: "Timeline",
              description:
                "See exactly how long each node took. Spot bottlenecks and understand execution order.",
            },
            {
              icon: "◎",
              title: "State Inspector",
              description:
                "Diff state before and after each node. Understand exactly how state evolves through execution.",
            },
            {
              icon: "⚙",
              title: "Tool Viewer",
              description:
                "Inspect every tool call input and output. Debug external API calls and function invocations.",
            },
            {
              icon: "◇",
              title: "Prompt Viewer",
              description:
                "See the exact prompt sent to every LLM. Understand why your model produced a given response.",
            },
            {
              icon: "⟆",
              title: "Zero Config",
              description:
                'One line of code: observe(graph). No decorators, no logging, no configuration files.',
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-5"
            >
              <div className="text-2xl text-indigo-400 mb-3">{feature.icon}</div>
              <h3 className="text-sm font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-xs text-neutral-500 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-neutral-800 px-8 py-5 text-center text-xs text-neutral-600">
        StateLens — Local-first AI debugging. No cloud. No auth. Just answers.
      </footer>
    </div>
  );
}
