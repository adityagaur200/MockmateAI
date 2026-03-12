import MockInterviewPreview from "@/components/MockInterviewPreview"
import Navbar from "@/components/Navbar"
import Footer  from "@/components/Footer";

const Interview = () => {
    return (
        <div className="container mx-auto p-4">
            <Navbar/>
            <div style={{ marginTop: "4rem", marginBottom: "3rem" }}>
                <MockInterviewPreview/>
            </div>
            <Footer/>
        </div>
    )
}
export default Interview;