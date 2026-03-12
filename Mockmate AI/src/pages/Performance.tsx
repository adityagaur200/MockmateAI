import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  LineChart, Line, Area, AreaChart,
} from "recharts";
import { TrendingUp, Target, Award, Clock, ChevronDown } from "lucide-react";
import { useState } from "react";

const overallScores = [
  { interview: "Interview 1", score: 5 },
  { interview: "Interview 2", score: 6 },
  { interview: "Interview 3", score: 6.5 },
  { interview: "Interview 4", score: 7 },
  { interview: "Interview 5", score: 7.5 },
  { interview: "Interview 6", score: 8 },
];

const skillRadar = [
  { skill: "Technical", value: 78 },
  { skill: "Communication", value: 85 },
  { skill: "Problem Solving", value: 72 },
  { skill: "Behavioral", value: 90 },
  { skill: "System Design", value: 65 },
  { skill: "Domain Knowledge", value: 70 },
];

const categoryScores = [
  { category: "React.js", score: 8.2 },
  { category: "Node.js", score: 7.0 },
  { category: "System Design", score: 6.5 },
  { category: "DSA", score: 5.8 },
  { category: "Behavioral", score: 8.8 },
  { category: "SQL", score: 7.5 },
];

const questionFeedback = [
  {
    question: "Describe your experience with React.js, highlighting any specific projects or components you've developed.",
    userAnswer: "I have worked with React for 3 years building component libraries and dashboards...",
    correctAnswer: "A strong answer should mention specific projects, component architecture decisions, state management approaches, and measurable outcomes...",
    score: 8,
    feedback: "Good coverage of experience. Could improve by mentioning performance optimization techniques and testing strategies.",
  },
  {
    question: "Explain the differences between Spring Boot and Node.js and why you might choose one over the other.",
    userAnswer: "Spring Boot is Java-based and Node.js uses JavaScript. Spring Boot is better for enterprise...",
    correctAnswer: "Compare runtime environments, threading models, ecosystem maturity, use cases (microservices, real-time apps), performance characteristics...",
    score: 6,
    feedback: "Basic comparison provided. Needs deeper technical analysis of threading models, ecosystem differences, and specific use-case scenarios.",
  },
  {
    question: "How would you design a real-time collaborative editing system?",
    userAnswer: "I would use WebSockets for real-time communication and a conflict resolution algorithm...",
    correctAnswer: "Discuss OT/CRDT algorithms, WebSocket architecture, operational transformation, server architecture, data persistence, and scaling strategies...",
    score: 7,
    feedback: "Good mention of WebSockets. Should elaborate on CRDT vs OT trade-offs and how to handle offline/reconnection scenarios.",
  },
];

const ExpandableQuestion = ({ item }: { item: typeof questionFeedback[0] }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl border bg-card shadow-card overflow-hidden transition-all duration-300 hover:shadow-card-hover">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-5 text-left"
      >
        <div className="flex-1 pr-4">
          <p className="text-sm font-medium leading-relaxed">{item.question}</p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="text-sm font-semibold text-primary">{item.score}/10</span>
          <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
        </div>
      </button>

      {open && (
        <motion.div
          className="px-5 pb-5 space-y-4 border-t pt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.2 }}
        >
          <div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Your Answer</span>
            <p className="text-sm text-foreground/80 mt-1 leading-relaxed">{item.userAnswer}</p>
          </div>
          <div>
            <span className="text-xs font-semibold text-primary uppercase tracking-wide">Ideal Answer</span>
            <p className="text-sm text-foreground/80 mt-1 leading-relaxed">{item.correctAnswer}</p>
          </div>
          <div className="rounded-lg bg-primary/5 border border-primary/10 p-3">
            <span className="text-xs font-semibold text-primary">💡 Feedback</span>
            <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{item.feedback}</p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

const PerformancePage = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-28 pb-24">
        <div className="container">
          {/* Header */}
          <motion.div
            className="mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-3xl font-bold tracking-tight mb-1">Performance Analysis</h1>
            <p className="text-muted-foreground">Track your progress and identify areas for improvement.</p>
          </motion.div>

          {/* Summary Stats */}
          <motion.div
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {[
              { icon: Award, label: "Best Score", value: "8/10", color: "text-primary" },
              { icon: TrendingUp, label: "Improvement", value: "+40%", color: "text-primary" },
              { icon: Target, label: "Avg. Score", value: "7.2/10", color: "text-primary" },
              { icon: Clock, label: "Avg. Duration", value: "22 min", color: "text-primary" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-2xl border bg-card p-5 shadow-card hover:shadow-card-hover transition-all duration-300"
              >
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <span className="text-xs text-muted-foreground">{stat.label}</span>
              </div>
            ))}
          </motion.div>

          {/* Charts Row */}
          <div className="grid lg:grid-cols-2 gap-6 mb-10">
            {/* Progress Over Time */}
            <motion.div
              className="rounded-2xl border bg-card p-6 shadow-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h3 className="font-semibold mb-4">Score Progress</h3>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={overallScores}>
                  <defs>
                    <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(243, 75%, 59%)" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="hsl(243, 75%, 59%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 13%, 91%)" />
                  <XAxis dataKey="interview" tick={{ fontSize: 12 }} stroke="hsl(220, 9%, 46%)" />
                  <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} stroke="hsl(220, 9%, 46%)" />
                  <Tooltip />
                  <Area type="monotone" dataKey="score" stroke="hsl(243, 75%, 59%)" fill="url(#scoreGradient)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Skills Radar */}
            <motion.div
              className="rounded-2xl border bg-card p-6 shadow-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.25 }}
            >
              <h3 className="font-semibold mb-4">Skills Breakdown</h3>
              <ResponsiveContainer width="100%" height={240}>
                <RadarChart data={skillRadar}>
                  <PolarGrid stroke="hsl(220, 13%, 91%)" />
                  <PolarAngleAxis dataKey="skill" tick={{ fontSize: 11 }} stroke="hsl(220, 9%, 46%)" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} stroke="hsl(220, 9%, 46%)" />
                  <Radar dataKey="value" stroke="hsl(243, 75%, 59%)" fill="hsl(243, 75%, 59%)" fillOpacity={0.15} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          {/* Category Scores */}
          <motion.div
            className="rounded-2xl border bg-card p-6 shadow-card mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h3 className="font-semibold mb-4">Category Performance</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={categoryScores} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 13%, 91%)" />
                <XAxis dataKey="category" tick={{ fontSize: 12 }} stroke="hsl(220, 9%, 46%)" />
                <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} stroke="hsl(220, 9%, 46%)" />
                <Tooltip />
                <Bar dataKey="score" fill="hsl(243, 75%, 59%)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>
      </section>
      <Footer />
    </div>
  );
};

export default PerformancePage;
