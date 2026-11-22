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
  Calendar
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-navy-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <Users className="w-6 h-6 text-blue-500" />
            <span>Resident Directory</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Manage authenticated society residents and reference facial encodings ({residents.length} registered)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchResidents}
            className="p-2.5 rounded-xl bg-navy-900 hover:bg-navy-800 border border-navy-700 text-slate-300 transition-colors"
            title="Refresh directory"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setIsRegisterOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition-all hover:scale-105 active:scale-95"
          >
            <UserPlus size={16} />
            <span>Add Resident</span>
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

      {/* Search Input Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by Resident ID (e.g. R001) or Name..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-navy-900 border border-navy-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
        />
      </div>

      {/* Residents Grid / Table */}
      {loading ? (
        <div className="p-12 text-center rounded-2xl bg-navy-900/60 border border-navy-800">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-400">Loading resident records from SQLite database...</p>
        </div>
      ) : filteredResidents.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-navy-900/60 border border-navy-800">
          <AlertCircle className="w-10 h-10 text-slate-500 mx-auto mb-3" />
          <h4 className="text-base font-bold text-white">No Residents Found</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            {search ? 'No residents matched your search query.' : 'There are currently no residents registered.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredResidents.map((r) => (
            <div
              key={r.resident_id}
              className="rounded-2xl bg-navy-900/80 border border-navy-800 hover:border-navy-600/80 p-4 shadow-lg transition-all hover:-translate-y-1 flex flex-col justify-between group"
            >
              <div>
                <div className="relative aspect-square rounded-xl overflow-hidden bg-navy-950 border border-navy-800 mb-3">
                  <img
                    src={residentsApi.getPhotoUrl(r.resident_id)}
                    alt={r.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    onError={(e) => {
                      e.target.src = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2'><circle cx='12' cy='8' r='4'/><path d='M20 21a8 8 0 1 0-16 0'/></svg>";
                    }}
                  />
                  <div className="absolute top-2 left-2">
                    <Badge variant="cyan" size="xs">
                      {r.resident_id}
                    </Badge>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-white truncate" title={r.name}>
                  {r.name}
                </h3>
                
                <div className="mt-1 flex items-center space-x-1.5 text-[11px] text-slate-400">
                  <Calendar size={12} className="text-slate-500 shrink-0" />
                  <span className="truncate">{r.registration_date}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-navy-800 flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider font-semibold text-emerald-400 flex items-center space-x-1">
                  <ShieldCheck size={12} />
                  <span>Enrolled</span>
                </span>
                <button
                  onClick={() => {
                    setDeletingResident(r);
                    setIsDeleteOpen(true);
                  }}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  title={`Delete ${r.name}`}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Registration Modal */}
      <Modal
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        title="Register New Resident"
      >
        <form onSubmit={handleRegisterSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Resident ID
            </label>
            <div className="relative">
              <IdCard className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                required
                value={registerForm.resident_id}
                onChange={(e) => setRegisterForm({ ...registerForm, resident_id: e.target.value })}
                placeholder="e.g. R023"
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-navy-950 border border-navy-700 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono uppercase"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Full Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                required
                value={registerForm.name}
                onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                placeholder="e.g. Elena Rostova"
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-navy-950 border border-navy-700 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Facial Photograph (Single Frontal Face)
            </label>
            <div className="mt-1 flex justify-center px-4 pt-4 pb-5 border-2 border-dashed border-navy-700 hover:border-blue-500/60 rounded-xl bg-navy-950/60 transition-colors cursor-pointer relative">
              <input
                type="file"
                accept="image/jpeg,image/png,image/jpg"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="text-center">
                {previewUrl ? (
                  <div className="relative inline-block">
                    <img 
                      src={previewUrl} 
                      alt="Preview" 
                      className="w-24 h-24 rounded-xl object-cover border border-blue-500 shadow-md mx-auto" 
                    />
                    <p className="text-xs text-blue-400 mt-2 font-medium">Click to change photo</p>
                  </div>
                ) : (
                  <>
                    <UploadCloud className="mx-auto h-8 w-8 text-slate-400" />
                    <p className="text-xs text-slate-300 mt-1.5 font-medium">Click or drag portrait photo here</p>
                    <p className="text-[10px] text-slate-500 mt-1">JPEG or PNG (Max 10MB)</p>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-navy-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsRegisterOpen(false)}
              className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 text-xs font-semibold text-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={registering}
              className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50 flex items-center space-x-2"
            >
              {registering ? (
                <>
                  <RefreshCw size={13} className="animate-spin" />
                  <span>Encoding Face...</span>
                </>
              ) : (
                <span>Register & Store</span>
              )}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        title="Confirm Deletion"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-300">
            Are you sure you want to delete resident{' '}
            <strong className="text-white font-mono">{deletingResident?.resident_id}</strong> (
            <span className="text-cyan-400 font-semibold">{deletingResident?.name}</span>)?
          </p>
          <p className="text-xs text-rose-400/90 bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
            Warning: This action permanently deletes the resident record, stored 128-D face encoding, and reference photograph.
          </p>
          <div className="pt-3 border-t border-navy-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsDeleteOpen(false)}
              className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 text-xs font-semibold text-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={deleting}
              onClick={confirmDelete}
              className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-600/30 transition-all disabled:opacity-50"
            >
              {deleting ? 'Deleting...' : 'Delete Resident'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
