import { AudioUpload } from "./components/AudioUpload";
import "./App.css";

function App() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">AI DJ Transition Engine</h1>
      <AudioUpload />
    </div>
  );
}

export default App;