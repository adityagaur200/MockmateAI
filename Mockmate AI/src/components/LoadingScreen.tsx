import { motion } from "framer-motion";

interface LoadingScreenProps {
  message?: string;
  detail?: string;
}

const LoadingScreen = ({
  message = "Loading your AI experience...",
  detail = "This may take a few seconds while we prepare everything for you.",
}: LoadingScreenProps) => {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#060b1b] text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <span className="absolute -left-20 top-20 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
        <span className="absolute right-0 top-32 h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl" />
        <span className="absolute left-1/2 bottom-10 h-72 w-72 -translate-x-1/2 rounded-full bg-violet-500/15 blur-3xl" />
      </div>

      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="relative w-full max-w-3xl overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-cyan-500/10 backdrop-blur-xl"
        >
          <div className="absolute -inset-10 bg-gradient-to-br from-cyan-500/10 via-violet-500/10 to-fuchsia-500/10 blur-3xl" />
          <div className="relative flex flex-col items-center gap-6 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
              className="relative flex h-28 w-28 items-center justify-center rounded-full bg-white/10 shadow-inner shadow-cyan-500/10"
            >
              <div className="absolute inset-0 rounded-full border border-cyan-300/25" />
              <div className="absolute inset-5 rounded-full border border-fuchsia-300/30" />
              <div className="absolute inset-12 rounded-full border border-violet-300/40" />
              <div className="absolute -left-2 top-1/2 h-4 w-4 -translate-y-1/2 rounded-full bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.8)]" />
            </motion.div>

            <div className="relative space-y-4">
              <p className="text-sm uppercase tracking-[0.35em] text-cyan-200/75">Loading</p>
              <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                {message}
              </h1>
              <p className="mx-auto max-w-2xl text-sm leading-6 text-slate-200/85">
                {detail}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-slate-200/80">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                <span className="h-3 w-3 animate-pulse rounded-full bg-cyan-400" />
                Fetching data
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                <span className="h-3 w-3 animate-pulse rounded-full bg-indigo-400" style={{ animationDelay: "120ms" }} />
                Warming up AI
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                <span className="h-3 w-3 animate-pulse rounded-full bg-fuchsia-400" style={{ animationDelay: "240ms" }} />
                Almost ready
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingScreen;
