import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import Residents from './pages/Residents';
import LiveGate from './pages/LiveGate';
import EntryLogs from './pages/EntryLogs';
import Evaluation from './pages/Evaluation';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/residents" element={<Residents />} />
          <Route path="/gate" element={<LiveGate />} />
          <Route path="/logs" element={<EntryLogs />} />
          <Route path="/evaluation" element={<Evaluation />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}
