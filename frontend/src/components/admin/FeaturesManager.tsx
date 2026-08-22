/**
 * Features Manager - Control which features require subscription
 */
import { useState, useEffect } from 'react';
import { Flag, Lock, Unlock } from 'lucide-react';
import { adminService } from '../../services/adminService';
import toast from 'react-hot-toast';

interface FeatureFlag {
  id?: number;
  feature_name: string;
  requires_subscription: boolean;
  description?: string;
}

const FeaturesManager = () => {
  const [features, setFeatures] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = async () => {
    try {
      const data = await adminService.getFeatures();
      setFeatures(data.features);
    } catch (error) {
      toast.error('Failed to load features');
    } finally {
      setLoading(false);
    }
  };

  const toggleFeature = async (feature: FeatureFlag) => {
    try {
      await adminService.updateFeature({
        ...feature,
        requires_subscription: !feature.requires_subscription
      });
      toast.success(`Feature ${feature.requires_subscription ? 'unlocked' : 'locked'}`);
      loadFeatures();
    } catch (error) {
      toast.error('Failed to update feature');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading features...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-gray-900">Feature Access Control</h3>
        <p className="text-gray-600">Control which features require an active subscription</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">Feature</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-700">Description</th>
              <th className="text-center px-6 py-3 text-sm font-semibold text-gray-700">Access</th>
              <th className="text-center px-6 py-3 text-sm font-semibold text-gray-700">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {features.map((feature) => (
              <tr key={feature.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Flag className="w-5 h-5 text-gray-400" />
                    <span className="font-medium text-gray-900">{feature.feature_name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {feature.description || 'No description'}
                </td>
                <td className="px-6 py-4 text-center">
                  {feature.requires_subscription ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                      <Lock className="w-3 h-3" />
                      Locked
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                      <Unlock className="w-3 h-3" />
                      Free
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-center">
                  <button
                    onClick={() => toggleFeature(feature)}
                    className={`px-4 py-2 rounded-lg transition font-medium text-sm ${
                      feature.requires_subscription
                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                        : 'bg-red-100 text-red-700 hover:bg-red-200'
                    }`}
                  >
                    {feature.requires_subscription ? 'Unlock' : 'Lock'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FeaturesManager;
