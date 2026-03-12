import { Mic, Camera, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";

const MockInterviewPreview = () => {
  return (
    <div className="rounded-2xl border bg-card shadow-card-hover overflow-hidden">
      {/* Top tabs */}
      <div className="flex items-center gap-2 px-6 pt-5 pb-3 flex-wrap">
        {["Question #1", "Question #2", "Question #3", "Question #4", "Question #5"].map(
          (q, i) => (
            <span
              key={q}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-colors ${
                i === 0
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-muted-foreground"
              }`}
            >
              {q}
            </span>
          )
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6 p-6">
        {/* Question card */}
        <div className="space-y-4">
          <p className="text-base font-medium leading-relaxed">
            Describe your experience with React.js, highlighting any specific
            projects or components you've developed.
          </p>
          <button className="text-muted-foreground hover:text-foreground transition-colors">
            <Volume2 className="h-4 w-4" />
          </button>

          <div className="rounded-xl bg-primary/5 border border-primary/10 p-4">
            <p className="text-xs font-semibold text-primary mb-1">💡 Note:</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Click on Record Answer when you want to answer the question. At
              the end of interview we will give you the feedback along with
              correct answer for each question.
            </p>
          </div>
        </div>

        {/* Webcam placeholder */}
        <div className="flex flex-col items-center gap-4">
          <div className="w-full aspect-video rounded-xl bg-foreground/5 border border-border flex items-center justify-center relative overflow-hidden">
            <Camera className="h-10 w-10 text-muted-foreground/30" />
            <div className="absolute top-3 right-3 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-destructive animate-pulse-soft" />
              <span className="text-[10px] text-muted-foreground font-medium">LIVE</span>
            </div>
          </div>
          <Button variant="outline" className="gap-2">
            <Mic className="h-4 w-4" />
            Record Answer
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MockInterviewPreview;
