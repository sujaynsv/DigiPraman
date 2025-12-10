import { JitsiMeeting } from "@jitsi/react-sdk";
import { useParams } from "react-router-dom";

export default function JitsiMeetComponent() {
  const { id } = useParams();                     // dynamic room id from route
  const roomName = `LoanRoom-${id}` || "TestRoom"; // fallback if id missing

  return (
    <div style={{ height: "100vh", width: "100%", overflow: "hidden" }}>
      <JitsiMeeting
        roomName={roomName}
        domain="meet.jit.si"
        userInfo={{
          displayName: "Officer"
        }}

        // KEY PART — removes preview, joins directly
        configOverwrite={{
          startWithAudioMuted: false,
          startWithVideoMuted: false,
          prejoinPageEnabled: false    // 🚀 disables preview page
        }}

        interfaceConfigOverwrite={{
          VIDEO_LAYOUT_FIT: "both",
          MOBILE_APP_PROMO: false
        }}

        getIFrameRef={(iframeRef) => {
          iframeRef.style.height = "100vh";
          iframeRef.style.width = "100%";
        }}
      />
    </div>
  );
}
