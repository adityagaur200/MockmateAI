import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LoadingScreen from "@/components/LoadingScreen";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { ChevronDown, ArrowLeft } from "lucide-react";

const parseFeedback = (feedback: any) => {
  if (!feedback) return "No feedback available.";

  // If it's already an object
  if (typeof feedback === "object") {
    // Check for feedback property (individual question feedback)
    if (feedback.feedback) return feedback.feedback;
    // Check for final_feedback property (full response)
    if (feedback.final_feedback) return feedback.final_feedback;
    return "No feedback available.";
  }

  // If it's a string, try to parse as JSON
  if (typeof feedback === "string") {
    try {
      const clean = feedback.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      
      if (typeof parsed === "object") {
        // Check for both feedback and final_feedback properties
        return parsed.feedback || parsed.final_feedback || clean;
      }
      return clean;
    } catch (err) {
      // If parsing fails, return the original string
      return feedback;
    }
  }

  return "Invalid feedback format";
};

const parseFeedbackScore = (feedback: any) => {
  if (!feedback) return 0;

  if (typeof feedback === "object") {
    // Check for score property (individual question) or final_score (full response)
    return feedback.score ?? feedback.final_score ?? 0;
  }

  if (typeof feedback === "string") {
    try {
      const clean = feedback.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      // Check for both score and final_score properties
      return parsed.score ?? parsed.final_score ?? 0;
    } catch {
      return 0;
    }
  }

  return 0;
};

const formatTimeSpent = (start?: string, end?: string) => {
  if (!start || !end) return "N/A";
  const startDate = new Date(start);
  const endDate = new Date(end);
  if (Number.isNaN(startDate.valueOf()) || Number.isNaN(endDate.valueOf())) {
    return "N/A";
  }

  const ms = endDate.getTime() - startDate.getTime();
  if (ms < 0) return "N/A";

  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const segments = [];
  if (hours) segments.push(`${hours}h`);
  if (minutes) segments.push(`${minutes}m`);
  if (seconds || segments.length === 0) segments.push(`${seconds}s`);

  return segments.join(" ");
};

const AnalysisDetail = () => {
  const { interviewId } = useParams();
  const [interview, setInterview] = useState<any>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const renderFeedbackLine = (line: string, idx: number) => {
    if (line.startsWith("## ")) {
      return (
        <p key={idx} className="text-base font-semibold mt-4 mb-2">
          {line.replace("## ", "")}
        </p>
      );
    }

    if (line.startsWith("1.") || line.startsWith("2.") || line.startsWith("3.") || line.startsWith("4.") || line.startsWith("5.")) {
      return (
        <p key={idx} className="text-sm text-muted-foreground leading-relaxed ml-4">
          {line}
        </p>
      );
    }

    return (
      <p key={idx} className="text-sm leading-relaxed text-foreground/80">
        {line}
      </p>
    );
  };

  useEffect(() => {
    const fetchInterview = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("No token found");
          setLoading(false);
          return;
        }

        const response = await fetch(`http://localhost:8000/interview/${interviewId}`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch interview details");
        }

        const data = await response.json();
        setInterview(data);
      } catch (err) {
        console.error("Error fetching interview:", err);
      } finally {
        setLoading(false);
      }
    };

    if (interviewId) {
      fetchInterview();
    }
  }, [interviewId]);

  if (loading) {
    return (
      <LoadingScreen
        message="Loading interview details..."
        detail="We are gathering your analysis so you can review your mock interview.
"
      />
    );
  }

  if (!interview) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-red-500">Interview not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-28 pb-24">
        <div className="container">
          {/* Header */}
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Link to="/dashboard">
              <Button variant="ghost" size="sm" className="mb-4 gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-3xl font-bold mb-2">{interview.job_name || "Interview Analysis"}</h1>
            
          </motion.div>

          {/* Interview Summary */}
          <motion.div
            className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr] mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <h2 className="text-xl font-semibold mb-4">Interview Summary</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-muted p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Job</p>
                  <p className="font-medium text-foreground">{interview.job_name || "N/A"}</p>
                </div>
                <div className="rounded-2xl bg-muted p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Status</p>
                  <p className="font-medium text-foreground">{interview.status || "N/A"}</p>
                </div>
                <div className="rounded-2xl bg-muted p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Questions</p>
                  <p className="font-medium text-foreground">{interview.history?.length || 0}</p>
                </div>
                <div className="rounded-2xl bg-muted p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Date</p>
                  <p className="font-medium text-foreground">
                    {interview.created_at ? new Date(interview.created_at).toLocaleDateString() : "N/A"}
                  </p>
                </div>
                <div className="rounded-2xl bg-muted p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Time Spent</p>
                  <p className="font-medium text-foreground">
                    {formatTimeSpent(interview.created_at, interview.ended_at)}
                  </p>
                </div>
              </div>

              {interview.job_description && (
                <div className="mt-6 rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-muted-foreground mb-2">Job Instructions</p>
                  <p className="text-sm leading-relaxed text-foreground/80">{interview.job_description}</p>
                </div>
              )}
            </div>

            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between gap-6 mb-6">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground mb-2">Final Score</p>
                  <p className="text-5xl font-bold text-primary">{interview.final_score || 0}</p>
                </div>
                <div className="rounded-3xl bg-primary/10 px-4 py-3 text-primary font-semibold">
                  {interview.status || "COMPLETED"}
                </div>
              </div>
              <div className="rounded-2xl bg-muted p-4 text-sm leading-relaxed text-foreground/80">
                {interview.final_feedback ? (
                  interview.final_feedback.split("\n").map((line: string, idx: number) => renderFeedbackLine(line, idx))
                ) : (
                  <p className="text-muted-foreground">No feedback available.</p>
                )}
              </div>
            </div>
          </motion.div>
            {/* Areas to Improve */}
          {interview.areas_to_improve && interview.areas_to_improve.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-10"
            >
              <h2 className="text-xl font-semibold mb-4">Areas to Improve</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {interview.areas_to_improve.map((area: string, idx: number) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + idx * 0.1 }}
                    className="rounded-xl border bg-card p-5 hover:shadow-lg transition-all duration-300"
                  >
                    <div className="flex gap-4">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-amber-100 text-amber-700">
                          <span className="text-lg font-semibold">{idx + 1}</span>
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">
                          {area}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
          {/* Questions and Answers */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-10"
          >
            <h2 className="text-xl font-semibold mb-4">Questions & Answers</h2>

            <div className="space-y-4">
              {interview.history && interview.history.length > 0 ? (
                interview.history.map((item: any, idx: number) => {
                  const score = parseFeedbackScore(item.feedback);

                  return (
                    <div
                      key={idx}
                      className="rounded-xl border bg-card overflow-hidden transition-all duration-300 hover:shadow-lg"
                    >
                      <button
                        onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                        className="w-full flex items-center justify-between p-5 text-left"
                      >
                        <div className="flex-1 pr-4">
                          <p className="text-sm font-medium leading-relaxed mb-2">
                            Q{idx + 1}: {item.question}
                          </p>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          <span className="text-sm font-semibold text-primary">
                            {score}/10
                          </span>
                          <ChevronDown
                            className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
                              expandedIndex === idx ? "rotate-180" : ""
                            }`}
                          />
                        </div>
                      </button>

                      {expandedIndex === idx && (
                        <motion.div
                          className="px-5 pb-5 space-y-4 border-t pt-4"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.2 }}
                        >
                          <div>
                            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                              Your Answer
                            </span>
                            <p className="text-sm text-foreground/80 mt-2 leading-relaxed">
                              {item.answer}
                            </p>
                          </div>

                          <div className="rounded-lg bg-primary/5 border border-primary/10 p-4">
                            <span className="text-xs font-semibold text-primary uppercase tracking-wide">
                              💡 Feedback
                            </span>
                            <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                              {parseFeedback(item.feedback)}
                            </p>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  );
                })
              ) : (
                <p className="text-muted-foreground">No questions recorded for this interview.</p>
              )}
            </div>
          </motion.div>
        </div>
      </section>
      <Footer />
    </div>
  );
};

export default AnalysisDetail;
