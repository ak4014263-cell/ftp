/**
 * Payment Cancel Page
 */
import { useNavigate } from 'react-router-dom';
import { XCircle, ArrowLeft, CreditCard } from 'lucide-react';

const PaymentCancel = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center">
          {/* Cancel Icon */}
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <XCircle className="w-12 h-12 text-red-600" />
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Payment Canceled
          </h1>

          {/* Description */}
          <p className="text-gray-600 mb-8">
            Your payment was canceled and no charges were made. You can try again whenever you're ready.
          </p>

          {/* Why Premium */}
          <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
            <h3 className="font-semibold text-gray-900 mb-3">Premium Benefits:</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✓ Unlimited job applications</li>
              <li>✓ AI-powered automation</li>
              <li>✓ Smart job matching</li>
              <li>✓ Priority support</li>
            </ul>
          </div>

          {/* Actions */}
          <button
            onClick={() => navigate('/payment')}
            className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg transition flex items-center justify-center gap-2 mb-4"
          >
            <CreditCard className="w-5 h-5" />
            Try Again
          </button>

          <button
            onClick={() => navigate('/dashboard')}
            className="w-full py-3 px-6 rounded-xl border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
        </div>

        {/* Support */}
        <p className="text-center text-sm text-gray-500 mt-6">
          Need help? Contact our{' '}
          <a href="mailto:support@swiply.io" className="text-blue-600 hover:underline">
            support team
          </a>
        </p>
      </div>
    </div>
  );
};

export default PaymentCancel;
