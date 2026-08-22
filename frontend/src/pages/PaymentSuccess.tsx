/**
 * Payment Success Page
 */
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Show success message
    toast.success('Payment successful! Your subscription is now active.');
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center">
          {/* Success Icon */}
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Payment Successful!
          </h1>

          {/* Description */}
          <p className="text-gray-600 mb-2">
            Thank you for subscribing to Swiply Premium!
          </p>
          <p className="text-gray-600 mb-8">
            You now have unlimited access to all premium features.
          </p>

          {/* Session ID */}
          {sessionId && (
            <div className="bg-gray-50 rounded-lg p-4 mb-8">
              <p className="text-sm text-gray-500 mb-1">Transaction ID</p>
              <p className="text-xs text-gray-700 font-mono break-all">{sessionId}</p>
            </div>
          )}

          {/* Features List */}
          <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
            <h3 className="font-semibold text-gray-900 mb-3">You now have access to:</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                Unlimited job applications
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                AI-powered cover letters
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                Automated job applications
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                Priority support
              </li>
            </ul>
          </div>

          {/* Actions */}
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg transition flex items-center justify-center gap-2 mb-4"
          >
            Go to Dashboard
            <ArrowRight className="w-5 h-5" />
          </button>

          <button
            onClick={() => navigate('/jobs')}
            className="w-full py-3 px-6 rounded-xl border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition"
          >
            Start Applying to Jobs
          </button>
        </div>

        {/* Email Confirmation */}
        <p className="text-center text-sm text-gray-500 mt-6">
          A confirmation email has been sent to your registered email address.
        </p>
      </div>
    </div>
  );
};

export default PaymentSuccess;
