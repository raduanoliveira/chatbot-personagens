import { useState, useEffect } from "react";
import { ChatPage } from "./pages/ChatPage";
import { CharactersPage } from "./pages/CharactersPage";
import "./App.css";

type Page = "chat" | "characters";

function App() {
    const [currentPage, setCurrentPage] = useState<Page>("chat");

    // Reseta scroll ao trocar de página
    useEffect(() => {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, [currentPage]);

    return (
        <div className="app-container">
            {currentPage === "chat" && (
                <div className="page-wrapper page-wrapper--active">
                    <ChatPage onNavigateToCharacters={() => setCurrentPage("characters")} />
                </div>
            )}
            {currentPage === "characters" && (
                <div className="page-wrapper page-wrapper--active">
                    <CharactersPage onNavigateToChat={() => setCurrentPage("chat")} />
                </div>
            )}
        </div>
    );
}

export default App;
