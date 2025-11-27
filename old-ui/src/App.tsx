import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ChatPage } from './pages/ChatPage';
import { FridgePage } from './pages/FridgePage';
import { PlannerPage } from './pages/PlannerPage';
import { GroceryPage } from './pages/GroceryPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/fridge" element={<FridgePage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/grocery" element={<GroceryPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
