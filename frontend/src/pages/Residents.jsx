import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Search, 
  UserPlus, 
  Trash2, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle,
  UploadCloud,
  IdCard,
  User,
  ShieldCheck,
  Calendar,
  AlertTriangle
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import Alert from '../components/common/Alert';
import { residentsApi } from '../services/api';

export default function Residents() {
  const [residents, setResidents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  // Register Modal state
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [registerForm, setRegisterForm] = useState({ resident_id: '', name: '' });
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [registering, setRegistering] = useState(false);

  // Delete Modal state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deletingResident, setDeletingResident] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchResidents();
  }, []);

  const fetchResidents = async () => {
    setLoading(true);
    try {
      const res = await residentsApi.getAll();
      setResidents(res.data);
    } catch (err) {
      setNotification({
        type: 'error',
        message: 'Failed to retrieve resident records from FastAPI backend.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!['image/jpeg', 'image/png', 'image/jpg', 'image/webp'].includes(file.type)) {
        setNotification({ type: 'warning', message: 'Please select a valid JPEG or PNG image.' });
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!registerForm.resident_id.trim() || !registerForm.name.trim()) {
      setNotification({ type: 'warning', message: 'Both Resident ID and Full Name are required.' });
      return;
    }
    if (!selectedFile) {
      setNotification({ type: 'warning', message: 'A face photograph is required to generate facial encodings.' });
      return;
    }

    setRegistering(true);
    const data = new FormData();
    data.append('resident_id', registerForm.resident_id.trim().toUpperCase());
    data.append('name', registerForm.name.trim());
    data.append('photo', selectedFile);

    try {
      const res = await residentsApi.register(data);
      setNotification({ type: 'success', message: res.data.message });
      setIsRegisterOpen(false);
      setRegisterForm({ resident_id: '', name: '' });
      setSelectedFile(null);
      setPreviewUrl(null);
      fetchResidents();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed. Check face visibility and lighting.';
      setNotification({ type: 'error', message: detail });
    } finally {
      setRegistering(false);
    }
  };

  const confirmDelete = async () => {
    if (!deletingResident) return;
    setDeleting(true);
    try {
      const res = await residentsApi.delete(deletingResident.resident_id);
      setNotification({ type: 'success', message: res.data.message });
      setIsDeleteOpen(false);
      setDeletingResident(null);
      fetchResidents();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to delete resident.';
      setNotification({ type: 'error', message: detail });
    } finally {
      setDeleting(false);
    }
  };

  const filteredResidents = residents.filter((r) => 
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.resident_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-graphite-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2 font-mono">
            <Users className="w-6 h-6 text-crimson-500" />
            <span>RESIDENT ROSTER</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1 font-mono">
            Biometric credentials & HOG facial encodings ({residents.length} authenticated profiles)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchResidents}
            className="p-2.5 rounded-xl bg-graphite-900 hover:bg-graphite-800 border border-graphite-700 text-slate-300 transition-colors"
            title="Refresh directory"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setIsRegisterOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold uppercase tracking-wider shadow-lg shadow-crimson-600/30 transition-all hover:scale-105 active:scale-95 border border-crimson-500/40"
          >
            <UserPlus size={15} />
            <span>Enroll Resident</span>
          </button>
        </div>
      </div>

      {notification && (
        <Alert
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-graphite-900 p-3.5 rounded-2xl border border-graphite-800">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Resident Name or ID..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-graphite-950 border border-graphite-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-crimson-600 font-mono"
          />
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Showing <span className="text-white font-bold">{filteredResidents.length}</span> of {residents.length} records
        </div>
      </div>

      {/* Resident Table */}
      <div className="rounded-2xl bg-graphite-900 border border-graphite-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-graphite-950/80 border-b border-graphite-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
              <tr>
                <th className="px-5 py-3.5">Resident</th>
                <th className="px-5 py-3.5">Resident ID</th>
                <th className="px-5 py-3.5">Enrollment Date</th>
                <th className="px-5 py-3.5">Biometric Status</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-graphite-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-5 py-12 text-center text-slate-400 font-mono">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-crimson-500" />
                    <span>Loading resident database...</span>
                  </td>
                </tr>
              ) : filteredResidents.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-5 py-12 text-center text-slate-400 font-mono">
                    No matching resident profiles found.
                  </td>
                </tr>
              ) : (
                filteredResidents.map((r) => (
                  <tr key={r.resident_id} className="hover:bg-graphite-850/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center space-x-3">
                        <img
                          src={residentsApi.getPhotoUrl(r.resident_id)}
                          alt={r.name}
                          className="w-10 h-10 rounded-xl object-cover bg-graphite-800 border border-graphite-700 shrink-0"
                          onError={(e) => {
                            e.target.src = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2'><circle cx='12' cy='8' r='4'/><path d='M20 21a8 8 0 1 0-16 0'/></svg>";
                          }}
                        />
                        <span className="font-bold text-white text-sm">{r.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono font-bold text-crimson-400 bg-crimson-600/10 px-2.5 py-1 rounded-md border border-crimson-600/20">
                        {r.resident_id}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-slate-400 text-[11px]">
                      {r.registration_date}
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant="allowed" size="xs">
                        128-D ENCODED
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => {
                          setDeletingResident(r);
                          setIsDeleteOpen(true);
                        }}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-crimson-400 hover:bg-crimson-600/10 transition-colors"
                        title="Delete resident"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Enroll Resident Modal */}
      <Modal
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        title="Enroll New Resident"
        maxWidth="max-w-lg"
      >
        <form onSubmit={handleRegisterSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
              Resident ID (Unique identifier)
            </label>
            <div className="relative">
              <IdCard className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="e.g. RES_009"
                value={registerForm.resident_id}
                onChange={(e) => setRegisterForm({ ...registerForm, resident_id: e.target.value })}
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-graphite-950 border border-graphite-700 text-xs font-mono text-white placeholder-slate-600 focus:outline-none focus:border-crimson-600 uppercase"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
              Full Legal Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="e.g. Maya Patel"
                value={registerForm.name}
                onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-graphite-950 border border-graphite-700 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-crimson-600"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
              Face Photo (High-Contrast Frontal)
            </label>
            <div className="p-4 rounded-xl border border-dashed border-graphite-700 bg-graphite-950/60 text-center hover:border-crimson-600/50 transition-colors">
              {previewUrl ? (
                <div className="flex flex-col items-center">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-24 h-24 rounded-xl object-cover border border-graphite-700 mb-2 shadow-lg"
                  />
                  <label className="text-xs font-mono text-crimson-400 cursor-pointer hover:underline">
                    Change image
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
              ) : (
                <label className="cursor-pointer block">
                  <UploadCloud className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                  <p className="text-xs font-mono text-slate-300">Click to upload face image</p>
                  <p className="text-[10px] text-slate-500 mt-1">JPEG, PNG up to 10MB</p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                    required
                  />
                </label>
              )}
            </div>
          </div>

          <div className="pt-3 border-t border-graphite-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsRegisterOpen(false)}
              className="px-4 py-2 rounded-xl bg-graphite-800 hover:bg-graphite-750 text-slate-300 text-xs font-mono uppercase tracking-wider"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={registering}
              className="px-5 py-2 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold font-mono uppercase tracking-wider shadow-lg shadow-crimson-600/30 transition-all disabled:opacity-50"
            >
              {registering ? 'Computing Encodings...' : 'Commit to SQLite'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        title="Confirm Personnel Removal"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <div className="p-3 rounded-xl bg-crimson-600/10 border border-crimson-600/30 text-xs text-rose-300 flex items-start space-x-2.5">
            <AlertTriangle className="w-4 h-4 text-crimson-500 shrink-0 mt-0.5" />
            <p>
              Are you sure you want to delete <strong className="text-white">{deletingResident?.name}</strong> ({deletingResident?.resident_id})? This will permanently remove their 128-D biometric encodings from SQLite.
            </p>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              onClick={() => setIsDeleteOpen(false)}
              className="px-4 py-2 rounded-xl bg-graphite-800 hover:bg-graphite-750 text-slate-300 text-xs font-mono uppercase tracking-wider"
            >
              Cancel
            </button>
            <button
              onClick={confirmDelete}
              disabled={deleting}
              className="px-4 py-2 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold font-mono uppercase tracking-wider shadow-lg shadow-crimson-600/30 disabled:opacity-50"
            >
              {deleting ? 'Deleting...' : 'Delete Resident'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
