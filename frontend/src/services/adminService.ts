/**
 * Admin Service API
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost/api';

// Set auth token for requests
const setAuthToken = (token: string) => {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export interface AdminLogin {
  username: string;
  password: string;
}

export interface SubscriptionPlan {
  id?: number;
  plan_name: string;
  price: number;
  stripe_price_id: string;
  features: string[];
  description?: string;
}

export interface FeatureFlag {
  id?: number;
  feature_name: string;
  requires_subscription: boolean;
  description?: string;
}

export const adminService = {
  /**
   * Admin login
   */
  async login(credentials: AdminLogin): Promise<{ access_token: string; username: string }> {
    const response = await axios.post(`${API_BASE_URL}/admin/login`, credentials);
    if (response.data.access_token) {
      setAuthToken(response.data.access_token);
      localStorage.setItem('admin_token', response.data.access_token);
    }
    return response.data;
  },

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/admin/dashboard/stats`);
    return response.data;
  },

  /**
   * Get all subscriptions
   */
  async getSubscriptions(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/admin/subscriptions?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  /**
   * Get all subscription plans
   */
  async getPlans(): Promise<{ plans: SubscriptionPlan[] }> {
    const response = await axios.get(`${API_BASE_URL}/admin/plans`);
    return response.data;
  },

  /**
   * Create or update subscription plan
   */
  async updatePlan(plan: SubscriptionPlan): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/admin/plans`, plan);
    return response.data;
  },

  /**
   * Get all feature flags
   */
  async getFeatures(): Promise<{ features: FeatureFlag[] }> {
    const response = await axios.get(`${API_BASE_URL}/admin/features`);
    return response.data;
  },

  /**
   * Update feature flag
   */
  async updateFeature(feature: FeatureFlag): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/admin/features`, feature);
    return response.data;
  },

  /**
   * Get Stripe prices
   */
  async getStripePrices(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/admin/stripe/prices`);
    return response.data;
  },

  /**
   * Get Stripe products
   */
  async getStripeProducts(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/admin/stripe/products`);
    return response.data;
  },

  /**
   * Cancel user subscription
   */
  async cancelUserSubscription(userId: string): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/admin/subscription/${userId}/cancel`);
    return response.data;
  },

  /**
   * Initialize admin (first-time setup)
   */
  async initializeAdmin(): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/admin/init-admin`);
    return response.data;
  },

  /**
   * Load token from storage
   */
  loadToken() {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setAuthToken(token);
    }
    return token;
  },

  /**
   * Logout
   */
  logout() {
    localStorage.removeItem('admin_token');
    delete axios.defaults.headers.common['Authorization'];
  }
};
