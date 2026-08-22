/**
 * Plans Manager Component - Manage subscription plans and pricing
 */
import { useState, useEffect } from 'react';
import { Plus, Edit2, DollarSign, Package } from 'lucide-react';
import { adminService } from '../../services/adminService';
import toast from 'react-hot-toast';

interface SubscriptionPlan {
  id?: number;
  plan_name: string;
  price: number;
  stripe_price_id: string;
  features: string[];
  description?: string;
}

const PlansManager = () => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [stripePrices, setStripePrices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingPlan, setEditingPlan] = useState<SubscriptionPlan | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState<SubscriptionPlan>({
    plan_name: '',
    price: 0,
    stripe_price_id: '',
    features: [],
    description: ''
  });

  useEffect(() => {
    loadPlans();
    loadStripePrices();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await adminService.getPlans();
      setPlans(data.plans);
    } catch (error) {
      toast.error('Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const loadStripePrices = async () => {
    try {
      const data = await adminService.getStripePrices();
      setStripePrices(data.prices);
    } catch (error) {
      console.error('Failed to load Stripe prices:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await adminService.updatePlan(formData);
      toast.success('Plan updated successfully');
      setShowForm(false);
      setFormData({
        plan_name: '',
        price: 0,
        stripe_price_id: '',
        features: [],
        description: ''
      });
      loadPlans();
    } catch (error) {
      toast.error('Failed to update plan');
    }
  };

  const handleEdit = (plan: SubscriptionPlan) => {
    setFormData(plan);
    setEditingPlan(plan);
    setShowForm(true);
  };

  const addFeature = () => {
    setFormData({
      ...formData,
      features: [...formData.features, '']
    });
  };

  const updateFeature = (index: number, value: string) => {
    const newFeatures = [...formData.features];
    newFeatures[index] = value;
    setFormData({ ...formData, features: newFeatures });
  };

  const removeFeature = (index: number) => {
    setFormData({
      ...formData,
      features: formData.features.filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return <div className="text-center py-8">Loading plans...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Subscription Plans</h3>
          <p className="text-gray-600">Manage pricing and plan features</p>
        </div>
        <button
          onClick={() => {
            setEditingPlan(null);
            setFormData({
              plan_name: '',
              price: 0,
              stripe_price_id: '',
              features: [],
              description: ''
            });
            setShowForm(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-5 h-5" />
          Add Plan
        </button>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {plans.map((plan) => (
          <div key={plan.id} className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-200 hover:border-blue-500 transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="text-xl font-bold text-gray-900 capitalize">{plan.plan_name}</h4>
                <p className="text-sm text-gray-600">{plan.description}</p>
              </div>
              <button
                onClick={() => handleEdit(plan)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <Edit2 className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <div className="mb-4">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-gray-900">${plan.price}</span>
                <span className="text-gray-600">/ month</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Stripe Price ID: {plan.stripe_price_id}</p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-semibold text-gray-700">Features:</p>
              <ul className="space-y-1">
                {plan.features.map((feature, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              {editingPlan ? 'Edit Plan' : 'Create New Plan'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Plan Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plan Name
                </label>
                <input
                  type="text"
                  value={formData.plan_name}
                  onChange={(e) => setFormData({ ...formData, plan_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., premium, pro, enterprise"
                  required
                />
              </div>

              {/* Price */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price (USD)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="29.00"
                  required
                />
              </div>

              {/* Stripe Price ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stripe Price ID
                </label>
                <select
                  value={formData.stripe_price_id}
                  onChange={(e) => setFormData({ ...formData, stripe_price_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Stripe Price</option>
                  {stripePrices.map((price) => (
                    <option key={price.id} value={price.id}>
                      {price.id} - ${(price.unit_amount / 100).toFixed(2)} {price.currency.toUpperCase()}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Or manually enter: price_xxxxxxxxxxxxx
                </p>
                <input
                  type="text"
                  value={formData.stripe_price_id}
                  onChange={(e) => setFormData({ ...formData, stripe_price_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mt-2"
                  placeholder="price_1U5l89AM5V5laBzu61PnRBrM"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Brief description of this plan"
                />
              </div>

              {/* Features */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Features
                  </label>
                  <button
                    type="button"
                    onClick={addFeature}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    + Add Feature
                  </button>
                </div>
                <div className="space-y-2">
                  {formData.features.map((feature, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={feature}
                        onChange={(e) => updateFeature(index, e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Feature description"
                      />
                      <button
                        type="button"
                        onClick={() => removeFeature(index)}
                        className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
                >
                  {editingPlan ? 'Update Plan' : 'Create Plan'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlansManager;
