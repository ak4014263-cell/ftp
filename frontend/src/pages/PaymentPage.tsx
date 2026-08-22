/**
 * Payment/Subscription Page
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Check, Zap, Shield, Crown } from 'lucide-react';
import { paymentService } from '../services/paymentService';
import toast from 'react-hot-toast';

const PaymentPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);
  
  // Get user from localStorage or your auth store
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    if (user.id) {
      loadSubscriptionStatus();
    }
  }, [user.id]);

  const loadSubscriptionStatus = async () => {
    try {
      const status = await paymentService.getSubscriptionStatus(user.id);
      setSubscriptionStatus(status);
    } catch (error) {
      console.error('Error loading subscription:', error);
    }
  };

  const handleSubscribe = async () => {
    if (!user.id || !user.email) {
      toast.error('Please log in to subscribe');
      navigate('/login');
      return;
    }

    setLoading(true);
    try {
      const { checkout_url } = await paymentService.createCheckoutSession({
        user_id: user.id,
        email: user.email,
        plan: 'premium'
      });

      // Redirect to Stripe Checkout
      window.location.href = checkout_url;
    } catch (error: any) {
      console.error('Checkout error:', error);
      toast.error(error.response?.data?.detail || 'Failed to create checkout session');
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    try {
      await paymentService.cancelSubscription(user.id);
      toast.success('Subscription canceled successfully');
      loadSubscriptionStatus();
    } catch (error) {
      toast.error('Failed to cancel subscription');
    }
  };

  const isActive = subscriptionStatus?.status === 'active';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Upgrade to Premium
          </h1>
          <p className="text-xl text-gray-600">
            Unlock unlimited job applications with AI-powered automation
          </p>
        </div>

        {/* Current Subscription Status */}
        {subscriptionStatus && (
          <div className="mb-8 p-6 bg-white rounded-xl shadow-lg border border-gray-200">
            <h3 className="text-lg font-semibold mb-2">Current Subscription</h3>
            <div className="flex items-center gap-4">
              <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                isActive 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {subscriptionStatus.status.toUpperCase()}
              </span>
              {subscriptionStatus.plan_type && (
                <span className="text-gray-600">
                  Plan: <strong>{subscriptionStatus.plan_type}</strong>
                </span>
              )}
              {subscriptionStatus.current_period_end && (
                <span className="text-gray-600">
                  Valid until: {new Date(subscriptionStatus.current_period_end).toLocaleDateString()}
                </span>
              )}
            </div>
            {isActive && (
              <button
                onClick={handleCancelSubscription}
                className="mt-4 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
              >
                Cancel Subscription
              </button>
            )}
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Free Plan */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-8 h-8 text-gray-600" />
              <h2 className="text-2xl font-bold text-gray-900">Free Plan</h2>
            </div>
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">$0</span>
              <span className="text-gray-600 ml-2">/ month</span>
            </div>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">5 job applications per day</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">Basic job recommendations</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">Standard support</span>
              </li>
            </ul>
            <button
              disabled
              className="w-full py-3 px-6 rounded-xl bg-gray-100 text-gray-500 font-semibold cursor-not-allowed"
            >
              Current Plan
            </button>
          </div>

          {/* Premium Plan */}
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-2xl p-8 border-2 border-blue-700 relative overflow-hidden">
            <div className="absolute top-4 right-4">
              <span className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-sm font-bold">
                RECOMMENDED
              </span>
            </div>
            <div className="flex items-center gap-3 mb-4">
              <Crown className="w-8 h-8 text-yellow-300" />
              <h2 className="text-2xl font-bold text-white">Premium Plan</h2>
            </div>
            <div className="mb-6">
              <span className="text-4xl font-bold text-white">$29</span>
              <span className="text-blue-100 ml-2">/ month</span>
            </div>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">Unlimited job applications</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">AI-powered cover letters</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">Automated job applications</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">Smart job matching</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">Priority support</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-yellow-300 mt-0.5" />
                <span className="text-white font-medium">Application tracking</span>
              </li>
            </ul>
            <button
              onClick={handleSubscribe}
              disabled={loading || isActive}
              className="w-full py-3 px-6 rounded-xl bg-white text-blue-600 font-bold hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                'Processing...'
              ) : isActive ? (
                <>
                  <Check className="w-5 h-5" />
                  Active Subscription
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Upgrade Now
                </>
              )}
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Why Upgrade to Premium?
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-lg mb-2">Save Time</h4>
              <p className="text-gray-600">
                Apply to hundreds of jobs in minutes with our AI automation
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CreditCard className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-semibold text-lg mb-2">Smart Matching</h4>
              <p className="text-gray-600">
                Get matched with jobs that fit your skills and experience
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-lg mb-2">Secure & Safe</h4>
              <p className="text-gray-600">
                Your data is encrypted and protected with industry standards
              </p>
            </div>
          </div>
        </div>

        {/* Powered by Stripe */}
        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">
            Secure payment powered by{' '}
            <a href="https://stripe.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              Stripe
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
