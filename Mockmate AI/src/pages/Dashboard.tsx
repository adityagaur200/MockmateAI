import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Plus, Clock, CheckCircle, BarChart3,X } from "lucide-react";
import { useState } from "react";
import Resume from "@/components/Resume";

const pastInterviews = [
  { id: 1, role: "Frontend Developer", company: "TechCorp", date: "Mar 10, 2026", score: 8, status: "Completed" },
  { id: 2, role: "Full Stack Engineer", company: "StartupXYZ", date: "Mar 8, 2026", score: 7, status: "Completed" },
  { id: 3, role: "React Developer", company: "DesignCo", date: "Mar 5, 2026", score: 6, status: "Completed" },
];

const DashboardPage = () => {
  const[newInterview,setnewInterview]=useState(false);
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-28 pb-24">
        <div className="container">
          <motion.div
            className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-10 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-1">Dashboard</h1>
              <p className="text-muted-foreground">Manage your mock interviews and track progress.</p>
            </div>
            <Button className="bg-gradient-primary hover:shadow-glow transition-all duration-300 gap-2" onClick={()=>setnewInterview(true)}>
              <Plus className="h-4 w-4" />
              New Interview
            </Button>
          {newInterview && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-md">
    
    {/* Wrapper with 15px spacing on both sides */}
    <div className="relative">
      
      {/* Close Button */}
      <button
        onClick={() => setnewInterview(false)}
        className="absolute -top-5 -right-7 z-10 p-2 rounded-full bg-white shadow-md hover:bg-gray-100 text-gray-700 transition-all duration-200"
      >
        <X className="w-4 h-4" />
      </button>

      {/* Modal Content */}
      <div className="bg-white rounded-2xl shadow-xl p-6 w-[50vw] max-h-[93vh]">
        <Resume />
      </div>

    </div>
  </div>
)}
          </motion.div>

          {/* Stats */}
          <motion.div
            className="grid sm:grid-cols-3 gap-4 mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {[
              { icon: CheckCircle, label: "Interviews Completed", value: "12" },
              { icon: BarChart3, label: "Average Score", value: "7.2/10" },
              { icon: Clock, label: "Total Practice Time", value: "4.5 hrs" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-2xl border bg-card p-6 shadow-card hover:shadow-card-hover transition-all duration-300"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <stat.icon className="h-4 w-4" />
                  </div>
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                </div>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            ))}
          </motion.div>

          {/* Past Interviews */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h2 className="text-xl font-semibold mb-4">Recent Interviews</h2>
            <div className="space-y-3">
              {pastInterviews.map((interview) => (
                <div
                  key={interview.id}
                  className="rounded-xl border bg-card p-5 shadow-card hover:shadow-card-hover transition-all duration-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div>
                    <h3 className="font-medium">{interview.role}</h3>
                    <p className="text-sm text-muted-foreground">
                      {interview.company} · {interview.date}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-medium text-primary">{interview.score}/10</span>
                    <Link to="/performance">
                      <Button variant="outline" size="sm">View Analysis</Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
      <Footer />
    </div>
  );
};

export default DashboardPage;
