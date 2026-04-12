import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, X, Briefcase, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from "react-router-dom";


const Resume = () => {
    const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setResumeFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
  if (!resumeFile || !jobTitle) return;

  try {
    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("job_description", jobDescription);
    formData.append("job_name", jobTitle);

    
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to continue.");
      navigate("/Auth");
      return;
    }
    const response = await fetch("http://localhost:8000/interview/start", {
      method: "POST",
      body: formData,
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error("API failed");
    }

    const data = await response.json();

    // ✅ BOTH: perform action + redirect
    navigate("/interview", {
      state: {
        interviewData: data
      }
    });

  } catch (error) {
    console.error("Error:", error);
  }
};

  return (
     <div className="rounded-2xl border bg-card p-8 shadow-card space-y-6">
            {/* Resume Upload */}
            <div>
              <label className="text-sm font-medium mb-2 block">Resume</label>
              <div
                className={`relative rounded-xl border-2 border-dashed p-8 text-center transition-all duration-200 cursor-pointer ${
                  dragActive
                    ? "border-primary bg-primary/5"
                    : resumeFile
                    ? "border-primary/30 bg-primary/5"
                    : "border-border hover:border-primary/40 hover:bg-secondary/50"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileChange}
                />
                {resumeFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="h-5 w-5 text-primary" />
                    <span className="text-sm font-medium">{resumeFile.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setResumeFile(null);
                      }}
                      className="ml-2 p-1 rounded-full hover:bg-secondary transition-colors"
                    >
                      <X className="h-3.5 w-3.5 text-muted-foreground" />
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-8 w-8 text-muted-foreground/50 mx-auto" />
                    <p className="text-sm text-muted-foreground">
                      Drag & drop your resume or{" "}
                      <span className="text-primary font-medium">browse</span>
                    </p>
                    <p className="text-xs text-muted-foreground/60">
                      PDF, DOCX, or TXT (max 10MB)
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Job Title */}
            <div>
              <label className="text-sm font-medium mb-2 block">Job Title</label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="e.g. Frontend Developer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Job Description */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Job Description
              </label>
              <Textarea
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="min-h-[120px] resize-none"
              />
            </div>

            {/* Submit */}
            <Button
              size="lg"
              className="w-full bg-gradient-primary hover:shadow-glow transition-all duration-300 h-12 text-base"
              onClick={handleSubmit}
              disabled={!resumeFile || !jobTitle}
            >
              Generate Interview Questions
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>

  )
}

export default Resume
