/**
 * Subscriptions Manager - View and manage all user subscriptions
 */
import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { adminService } from '../../services/adminService';
import toast from 'react-hot-toast';

const SubscriptionsManager = () => {
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const loadSubscriptions = async () => {
    try {
      const data = await adminService.getSubscriptions(0, 100);
      setSubscriptions(data.subscriptions);
    } catch (error) {
      toast.error('Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async (userId: string) => {
    if (!confirm('Are you sure you want to cancel this subscription?')) {
      return;
    }

    try {
      await adminService.cancelUserSubscription(userId);
      toast.success('Subscription canceled');
      loadSubscriptions();
    } catch (error) {
      toast.error('Failed to cancel subscription');
    }
  };

  const filteredSubscriptions = subscriptions.filter((sub) =>
    sub.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sub.user_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="text-center py-8">Loading subscriptions...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Search by email or user ID..."
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">User</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">Plan</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">Status</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">Period End</th>
              <th className="text-center px-6 py-3 text-sm font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredSubscriptions.map((sub) => (
              <tr key={sub.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4">
                  <div>
                    <p className="font-medium text-gray-900">{sub.email || 'No email'}</p>
                    <p className="text-xs text-gray-500">{sub.user_id}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium capitalize">
                    {sub.plan_type || 'Unknown'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    sub.subscription_status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : sub.subscription_status === 'canceled'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {sub.subscription_status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {sub.current_period_end
                    ? new Date(sub.current_period_end).toLocaleDateString()
                    : 'N/A'}
                </td>
                <td className="px-6 py-4 text-center">
                  {sub.subscription_status === 'active' && (
                    <button
                      onClick={() => handleCancelSubscription(sub.user_id)}
                      className="px-3 py-1 text-red-600 hover:bg-red-50 rounded-lg transition text-sm"
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredSubscriptions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No subscriptions found
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionsManager;
