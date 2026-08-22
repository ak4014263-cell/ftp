/**
 * Payment Service - Stripe Integration
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost/api';

export interface CheckoutRequest {
  user_id: string;
  email: string;
  plan?: string;
}

export interface SubscriptionStatus {
  status: string;
  subscription_id: string | null;
  customer_id?: string;
  current_period_end: string | null;
  plan_type: string | null;
}

export const paymentService = {
  /**
   * Create a Stripe checkout session
   */
  async createCheckoutSession(data: CheckoutRequest): Promise<{ checkout_url: string; session_id: string }> {
    const response = await axios.post(`${API_BASE_URL}/payment/create-checkout-session`, data);
    return response.data;
  },

  /**
   * Get subscription status for a user
   */
  async getSubscriptionStatus(userId: string): Promise<SubscriptionStatus> {
    const response = await axios.get(`${API_BASE_URL}/payment/subscription/${userId}`);
    return response.data;
  },

  /**
   * Cancel a subscription
   */
  async cancelSubscription(userId: string): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${API_BASE_URL}/payment/cancel-subscription/${userId}`);
    return response.data;
  },
};
