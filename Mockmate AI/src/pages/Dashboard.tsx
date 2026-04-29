import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LoadingScreen from "@/components/LoadingScreen";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Plus, Clock, CheckCircle, BarChart3, X, Award } from "lucide-react";
import { useState, useEffect } from "react";
import Resume from "@/components/Resume";
import {
  AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";

const DashboardPage = () => {
  const [newInterview, setnewInterview] = useState(false);
  const [dashboard, setDashboard] = useState<any | null>(null);
  const [skillRadar, setSkillRadar] = useState<Array<{ skill: string; value: number }>>([
    { skill: "Technical", value: 0 },
    { skill: "Communication", value: 0 },
    { skill: "Problem Solving", value: 0 },
    { skill: "Behavioral", value: 0 },
    { skill: "System Design", value: 0 },
    { skill: "Domain Knowledge", value: 0 },
  ]);

  useEffect(() => {
  const token = localStorage.getItem("token");

  if (!token) {
    console.error("No token found");
    return;
  }

  fetch("http://localhost:8000/interview/dashboard", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`, 
    },
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error("Failed to fetch dashboard");
      }
      return res.json();
    })
    .then((data) => {
      console.log("Dashboard data:", data);
      console.log({
        avg_score: data.avg_score,
        recent_interviews: data.recent_interviews,
        skill_radar: data.skill_radar,
        total_interviews: data.total_interviews,
        total_time: data.total_time,
      });
      console.log("Total Interviews Count:", data.total_interviews, "Type:", typeof data.total_interviews);

      setDashboard(data);
      
      // Update skill radar with actual API data
      if (data.skill_radar && Array.isArray(data.skill_radar) && data.skill_radar.length > 0) {
        // Normalize skill radar data from API
        const normalizedRadar = data.skill_radar.map((item: any) => ({
          skill: item.skill || "Unknown",
          value: typeof item.value === "number" ? Math.min(Math.max(item.value, 0), 100) : 0,
        }));
        setSkillRadar(normalizedRadar);
      }
    })
    .catch((err) => console.error(err));
}, []);

  if (!dashboard) {
    return (
      <LoadingScreen
        message="Loading your dashboard..."
        detail="Preparing your progress metrics and interview insights for you."
      />
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="pt-28 pb-24">
        <div className="container">

          {/* Header */}
          <motion.div
            className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-10 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">
                Manage your mock interviews and track progress.
              </p>
            </div>

            <Button
              className="bg-gradient-primary gap-2"
              onClick={() => setnewInterview(true)}
            >
              <Plus className="h-4 w-4" />
              New Interview
            </Button>

            {/* Modal */}
            {newInterview && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-md">
                <div className="relative">
                  <button
                    onClick={() => setnewInterview(false)}
                    className="absolute -top-5 -right-7 p-2 rounded-full bg-white shadow-md"
                  >
                    <X className="w-4 h-4" />
                  </button>

                  <div className="bg-white rounded-2xl p-6 w-[50vw] max-h-[93vh]">
                    <Resume />
                  </div>
                </div>
              </div>
            )}
          </motion.div>

          {/* Stats */}
          <motion.div
            className="grid sm:grid-cols-4 gap-4 mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {[
              {
                icon: CheckCircle,
                label: "Interviews Completed",
                value: dashboard.recent_interviews?.length || 0,
              },
              {
                icon: Award,
                label: "Best Score",
                value: dashboard.recent_interviews.length > 0 
                  ? `${Math.max(...dashboard.recent_interviews.map((i: any) => i.score || 0))}/10`
                  : "0/10",
              },
              {
                icon: BarChart3,
                label: "Average Score",
                value: `${dashboard.avg_score}/10`,
              },
              {
                icon: Clock,
                label: "Total Practice Time",
                value: `${dashboard.total_time} hrs`,
              },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-2xl border bg-card p-6"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <stat.icon className="h-4 w-4" />
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {stat.label}
                  </span>
                </div>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            ))}
          </motion.div>

          {/* Charts Row */}
          <div className="grid lg:grid-cols-2 gap-6 mb-10">
            {/* Score Progress Chart */}
            <motion.div
              className="rounded-2xl border bg-card p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h3 className="font-semibold mb-4">Score Progress</h3>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart
                  data={dashboard.recent_interviews.map((interview: any, idx: number) => ({
                    interview: interview.job_name || `Interview ${idx + 1}`,
                    score: interview.score || 0,
                  }))}
                >
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

            {/* Skills Radar Chart */}
            <motion.div
              className="rounded-2xl border bg-card p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.25 }}
            >
              <h3 className="font-semibold mb-4">
                Skills Breakdown {dashboard.skill_radar && dashboard.skill_radar.length > 0 ? "(Latest)" : "(No Data)"}
              </h3>
              {skillRadar && skillRadar.length > 0 && skillRadar.some(s => s.value > 0) ? (
                <ResponsiveContainer width="100%" height={280}>
                  <RadarChart data={skillRadar} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <PolarGrid stroke="hsl(220, 13%, 91%)" />
                    <PolarAngleAxis dataKey="skill" tick={{ fontSize: 11 }} stroke="hsl(220, 9%, 46%)" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} stroke="hsl(220, 9%, 46%)" />
                    <Radar 
                      name="Skills" 
                      dataKey="value" 
                      stroke="hsl(243, 75%, 59%)" 
                      fill="hsl(243, 75%, 59%)" 
                      fillOpacity={0.25} 
                      strokeWidth={2} 
                    />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-80 bg-muted/30 rounded-lg">
                  <p className="text-muted-foreground text-center">
                    Complete interviews to see your skills breakdown
                  </p>
                </div>
              )}
            </motion.div>
          </div>

          {/* Recent Interviews */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-xl font-semibold mb-4">
              Recent Interviews
            </h2>

            <div className="space-y-3">
              {dashboard.recent_interviews.length === 0 ? (
                <p className="text-muted-foreground">
                  No interviews yet.
                </p>
              ) : (
                dashboard.recent_interviews.map((interview) => (
                  <div
                    key={interview.id}
                    className="rounded-xl border bg-card p-5 flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">
                          {interview.job_name || interview.role || "Interview"}
                        </h3>
                        {interview.status && (
                          <span className="rounded-full bg-primary/10 text-primary px-2 py-1 text-xs font-semibold">
                            {interview.status}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                      {interview.date ? new Date(interview.date).toLocaleDateString() : "No date"}
                      </p>
                  </div>

                    <div className="flex items-center gap-4">
                      <span className="text-sm font-medium text-primary">
                        {interview.score}/10
                      </span>

                      <Link to={`/analysis/${interview.id}`}>
                        <Button variant="outline" size="sm">
                          View Analysis
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>

        </div>
      </section>

      <Footer />
    </div>
  );
};

export default DashboardPage;