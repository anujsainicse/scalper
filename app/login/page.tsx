/**
 * Login Page
 * Handles user authentication with Email/Password and Google OAuth via Supabase
 */

'use client'

import React, { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, Mail } from 'lucide-react'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const { user, loading, signInWithGoogle, supabase } = useAuth()
  const router = useRouter()
  const [isSigningIn, setIsSigningIn] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [resetEmailSent, setResetEmailSent] = useState(false)

  // Redirect if already logged in
  useEffect(() => {
    if (!loading && user) {
      router.push('/')
    }
  }, [user, loading, router])

  const handleGoogleSignIn = async () => {
    setIsSigningIn(true)
    try {
      await signInWithGoogle()
    } catch (error: any) {
      console.error('Sign in error:', error)
      toast.error(error.message || 'Failed to sign in with Google')
      setIsSigningIn(false)
    }
  }

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email) {
      toast.error('Please enter your email address')
      return
    }

    if (!supabase) {
      toast.error('Supabase not configured')
      return
    }

    setIsSigningIn(true)

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      })

      if (error) throw error

      setResetEmailSent(true)
      toast.success('Password reset link sent! Check your email.')
    } catch (error: any) {
      console.error('Password reset error:', error)
      toast.error(error.message || 'Failed to send reset email')
    } finally {
      setIsSigningIn(false)
    }
  }

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email || !password) {
      toast.error('Please enter email and password')
      return
    }

    if (!supabase) {
      toast.error('Supabase not configured')
      return
    }

    setIsSigningIn(true)

    try {
      if (isSignUp) {
        // Sign up
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        })

        if (error) throw error

        if (data.user) {
          toast.success('Account created! Please check your email for verification.')
          // Switch to login tab
          setIsSignUp(false)
          setPassword('')
        }
      } else {
        // Sign in
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (error) throw error

        if (data.user) {
          toast.success('Signed in successfully!')
          router.push('/')
        }
      }
    } catch (error: any) {
      console.error('Auth error:', error)
      toast.error(error.message || `Failed to ${isSignUp ? 'sign up' : 'sign in'}`)
    } finally {
      setIsSigningIn(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background to-muted">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-3xl font-bold">Scalper Bot</CardTitle>
          <CardDescription className="text-base">
            Sign in to manage your trading bots
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email">Email</TabsTrigger>
              <TabsTrigger value="google">Google</TabsTrigger>
            </TabsList>

            {/* Email Login/Signup Tab */}
            <TabsContent value="email" className="space-y-4">
              {showForgotPassword ? (
                /* Forgot Password Form */
                <form onSubmit={handleForgotPassword} className="space-y-4">
                  {resetEmailSent ? (
                    <div className="text-center space-y-4 py-4">
                      <div className="text-green-600 dark:text-green-400">
                        <Mail className="h-12 w-12 mx-auto mb-3" />
                        <h3 className="font-semibold text-lg mb-2">Check Your Email</h3>
                        <p className="text-sm text-muted-foreground">
                          We've sent a password reset link to <strong>{email}</strong>
                        </p>
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setShowForgotPassword(false)
                          setResetEmailSent(false)
                          setEmail('')
                        }}
                        className="w-full"
                      >
                        Back to Sign In
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="reset-email">Email</Label>
                        <Input
                          id="reset-email"
                          type="email"
                          placeholder="your@email.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          disabled={isSigningIn}
                          required
                        />
                        <p className="text-xs text-muted-foreground">
                          Enter your email to receive a password reset link
                        </p>
                      </div>

                      <Button
                        type="submit"
                        disabled={isSigningIn}
                        className="w-full"
                        size="lg"
                      >
                        {isSigningIn ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Sending...
                          </>
                        ) : (
                          <>
                            <Mail className="mr-2 h-4 w-4" />
                            Send Reset Link
                          </>
                        )}
                      </Button>

                      <div className="text-center text-sm">
                        <button
                          type="button"
                          onClick={() => {
                            setShowForgotPassword(false)
                            setEmail('')
                          }}
                          className="text-primary hover:underline"
                          disabled={isSigningIn}
                        >
                          Back to Sign In
                        </button>
                      </div>
                    </>
                  )}
                </form>
              ) : (
                /* Regular Login/Signup Form */
                <form onSubmit={handleEmailAuth} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={isSigningIn}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="password">Password</Label>
                      {!isSignUp && (
                        <button
                          type="button"
                          onClick={() => setShowForgotPassword(true)}
                          className="text-xs text-primary hover:underline"
                          disabled={isSigningIn}
                        >
                          Forgot password?
                        </button>
                      )}
                    </div>
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={isSigningIn}
                      required
                      minLength={6}
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={isSigningIn}
                    className="w-full"
                    size="lg"
                  >
                    {isSigningIn ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {isSignUp ? 'Creating account...' : 'Signing in...'}
                      </>
                    ) : (
                      <>
                        <Mail className="mr-2 h-4 w-4" />
                        {isSignUp ? 'Create Account' : 'Sign In'}
                      </>
                    )}
                  </Button>

                  <div className="text-center text-sm">
                    <button
                      type="button"
                      onClick={() => {
                        setIsSignUp(!isSignUp)
                        setPassword('')
                      }}
                      className="text-primary hover:underline"
                      disabled={isSigningIn}
                    >
                      {isSignUp
                        ? 'Already have an account? Sign in'
                        : "Don't have an account? Sign up"}
                    </button>
                  </div>
                </form>
              )}
            </TabsContent>

            {/* Google Login Tab */}
            <TabsContent value="google" className="space-y-4">
              <Button
                onClick={handleGoogleSignIn}
                disabled={isSigningIn}
                className="w-full"
                size="lg"
                variant="outline"
              >
                {isSigningIn ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Continue with Google
                  </>
                )}
              </Button>
            </TabsContent>
          </Tabs>

          <div className="text-center text-sm text-muted-foreground">
            <p>By signing in, you agree to our Terms of Service</p>
            <p>and Privacy Policy</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
