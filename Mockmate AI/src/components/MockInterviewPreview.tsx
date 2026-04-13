import { Mic, Camera, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { set } from "date-fns";

const MockInterviewPreview = () => {
  const navigate = useNavigate();
  const interviewId = localStorage.getItem("InterviewId");
  console.log("Interview ID from localStorage:", interviewId);

const [question, setQuestion] = useState("");
const [loading, setLoading] = useState(true);

const [isRecording, setIsRecording] = useState(false);
const [mediaRecorder, setMediaRecorder] = useState(null);
const [recordedBlob, setRecordedBlob] = useState(null);

const videoRef = useRef(null);
const streamRef = useRef(null);

// ✅ FETCH QUESTION
const fetchQuestion = async () => {
try {
const res = await fetch(
`http://localhost:8000/interview/${interviewId}/question`
);

  const data = await res.json();
  console.log("API Response:", data);

  if (data.status === "COMPLETED") {
    setQuestion("Interview Completed 🎉");
    navigate("/dashboard");
    return;
  }

  if (data.current_question) {
    setQuestion(data.current_question);
  }

} catch (err) {
  console.error("Fetch error:", err);
  setQuestion("Error loading question ❌");
} finally {
  setLoading(false);
}
};

// ✅ INITIAL LOAD
useEffect(() => {
if (!interviewId) return;
fetchQuestion();
}, [interviewId]);

// 🎥 Start camera
const startMedia = async () => {
const stream = await navigator.mediaDevices.getUserMedia({
video: true,
audio: true,
});


streamRef.current = stream;

if (videoRef.current) {
  videoRef.current.srcObject = stream;
}

return stream;

};

// 🎤 Start Recording
const startRecording = async () => {
const stream = await startMedia();


const recorder = new MediaRecorder(stream);
setMediaRecorder(recorder);

const chunks = [];

recorder.ondataavailable = (e) => {
  chunks.push(e.data);
};

recorder.onstop = () => {
  const blob = new Blob(chunks, { type: "video/webm" });
  setRecordedBlob(blob);

  streamRef.current.getTracks().forEach((track) => track.stop());
};

recorder.start();
setIsRecording(true);


};

// 🛑 Stop Recording
const stopRecording = () => {
if (mediaRecorder) {
mediaRecorder.stop();
setIsRecording(false);
}
};

// 🔁 POLLING (FIXED)
const pollForNextQuestion = (oldQuestion) => {
  const interval = setInterval(async () => {
    const res = await fetch(
      `http://localhost:8000/interview/${interviewId}/question`
    );

    const data = await res.json();
    console.log("Polling:", data);

    // 🔥 STOP if interview completed
    if (data.status === "COMPLETED") {
      clearInterval(interval);

      alert("Interview Completed 🎉");

      navigate("/dashboard");
      return;
    }

    // ✅ Update only if new question
    if (
      data.current_question &&
      data.current_question !== oldQuestion
    ) {
      setQuestion(data.current_question);
      clearInterval(interval);
    }

  }, 3000);

  setTimeout(() => clearInterval(interval), 30000); // safety stop after 1 min
};

// 🚀 Submit Answer
const submitAnswer = async () => {
try {
if (!recordedBlob) {
alert("Please record an answer first 🎤");
return;
}


  const oldQuestion = question; // store current

  const formData = new FormData();
  formData.append("file", recordedBlob, "answer.webm");

  await fetch(
    `http://localhost:8000/interview/${interviewId}/answer`,
    {
      method: "POST",
      body: formData,
    }
  );

  // ⏳ show processing
  setQuestion("Processing your answer... ⏳");

  // 🔁 start polling
  pollForNextQuestion(oldQuestion);

  setRecordedBlob(null);

} catch (err) {
  console.error("Submit error:", err);
}


};

return ( <div className="rounded-2xl border bg-card shadow-card-hover overflow-hidden"> <div className="grid md:grid-cols-2 gap-6 p-6">


    {/* Question */}
    <div className="space-y-4">
      <p className="text-base font-medium leading-relaxed">
        {loading ? "Loading..." : question}
      </p>

      <button className="text-muted-foreground hover:text-foreground">
        <Volume2 className="h-4 w-4" />
      </button>

      <div className="rounded-xl bg-primary/5 border p-4">
        <p className="text-xs font-semibold text-primary mb-1">💡 Note:</p>
        <p className="text-xs text-muted-foreground">
          Record your answer, then click Submit.
        </p>
      </div>
    </div>

    {/* Video */}
    <div className="flex flex-col items-center gap-4">
      <div className="w-full aspect-video rounded-xl bg-black overflow-hidden relative">
        <video
          ref={videoRef}
          autoPlay
          muted
          className="w-full h-full object-cover"
        />

        {!isRecording && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Camera className="h-10 w-10 text-white/40" />
          </div>
        )}
      </div>

      <Button
        variant="outline"
        onClick={isRecording ? stopRecording : startRecording}
      >
        <Mic className="h-4 w-4 mr-2" />
        {isRecording ? "Stop Recording" : "Start Recording"}
      </Button>

      <Button
        variant="default"
        onClick={submitAnswer}
        disabled={!recordedBlob}
      >
        Submit Answer
      </Button>
    </div>
  </div>
</div>

);
};

export default MockInterviewPreview;
