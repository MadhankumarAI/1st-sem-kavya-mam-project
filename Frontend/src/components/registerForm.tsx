import React, { useState } from 'react';
import { Mail, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';
import Cookies from 'js-cookie';

interface FormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

const RegisterForm = () => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [verificationStep, setVerificationStep] = useState<boolean>(false);
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [message, setMessage] = useState<string>('');

  const generateVerificationCode = () => {
    return Math.floor(100000 + Math.random() * 900000).toString();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    const newErrors: FormErrors = {};

    if (!formData.username) {
      newErrors.username = 'Username is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    if (!verificationStep) {
      // Generate and store verification code
      const code = generateVerificationCode();
      Cookies.set('verificationCode', code);

      try {
        // Send verification code to backend
        const response = await fetch('http://localhost:8000/reg/send-mail/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            code: code
          }),
        });

        if (response.ok) {
          setVerificationStep(true);
          setMessage('Verification code has been sent to your email');
        } else {
          setMessage('Failed to send verification code');
        }
      } catch (error) {
        setMessage('Error occurred while sending verification code');
      }
    } else {
      // Verify code and register user
      const storedCode = Cookies.get('verificationCode');

      if (verificationCode === storedCode) {
        try {
          const response = await fetch('http://localhost:8000/reg', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
          });

          if (response.ok) {
            setMessage('Registration successful!');
            // Redirect to login page after successful registration
            window.location.href = '/login';
          } else {
            setMessage('Registration failed');
          }
        } catch (error) {
          setMessage('Error occurred during registration');
        }
      } else {
        setMessage('Invalid verification code');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center relative p-4">
      {/* 3D Background - You'll need to implement your own background or remove this */}
      <div className="absolute inset-0 -z-10">
        {/* Add your background here */}
      </div>

      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-gray-800">InterXAI</h3>
        </div>

        {message && (
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 text-blue-700 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            <p>{message}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {!verificationStep ? (
            <>
              <div className="space-y-4">
                <div>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Username"
                    />
                  </div>
                  {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username}</p>}
                </div>

                <div>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Email"
                    />
                  </div>
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                </div>

                <div>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Password"
                    />
                  </div>
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
                </div>

                <div>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Confirm Password"
                    />
                  </div>
                  {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>}
                </div>
              </div>
            </>
          ) : (
            <div>
              <div className="relative">
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter verification code"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
          >
            {!verificationStep ? 'Create account' : 'Verify'}
            <ArrowRight className="ml-2 w-5 h-5" />
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="text-blue-600 hover:underline font-semibold">
              Sign In
            </a>
          </p>
          <a
            href="http://localhost:8000/auth/google"
            className="inline-block mt-2 text-blue-600 hover:underline"
          >
            Login with Google
          </a>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;